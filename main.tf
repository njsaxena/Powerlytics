# EcoGridIQ Terraform Configuration
terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Variables
variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "dataset_id" {
  description = "BigQuery Dataset ID"
  type        = string
  default     = "ecogrid_dwh"
}

# Enable required APIs
resource "google_project_service" "apis" {
  for_each = toset([
    "bigquery.googleapis.com",
    "aiplatform.googleapis.com",
    "run.googleapis.com",
    "cloudbuild.googleapis.com",
    "storage.googleapis.com",
    "logging.googleapis.com",
    "monitoring.googleapis.com"
  ])
  
  service = each.value
  disable_on_destroy = false
}

# BigQuery Dataset
resource "google_bigquery_dataset" "ecogrid_dwh" {
  dataset_id    = var.dataset_id
  friendly_name = "EcoGridIQ Data Warehouse"
  description   = "Energy analytics data warehouse for EcoGridIQ"
  location      = "US"
  
  depends_on = [google_project_service.apis]
}

# Cloud Storage Bucket for frontend
resource "google_storage_bucket" "frontend" {
  name          = "${var.project_id}-ecogrid-frontend"
  location      = "US"
  force_destroy = true
  
  website {
    main_page_suffix = "index.html"
    not_found_page   = "404.html"
  }
  
  uniform_bucket_level_access = true
  
  depends_on = [google_project_service.apis]
}

# Make bucket publicly readable
resource "google_storage_bucket_iam_member" "public_read" {
  bucket = google_storage_bucket.frontend.name
  role   = "roles/storage.objectViewer"
  member = "allUsers"
}

# Service Account for Cloud Run
resource "google_service_account" "ecogrid_backend" {
  account_id   = "ecogrid-backend"
  display_name = "EcoGridIQ Backend Service Account"
  description  = "Service account for EcoGridIQ backend API"
}

# IAM bindings for service account
resource "google_project_iam_member" "bigquery_user" {
  project = var.project_id
  role    = "roles/bigquery.user"
  member  = "serviceAccount:${google_service_account.ecogrid_backend.email}"
}

resource "google_project_iam_member" "bigquery_data_viewer" {
  project = var.project_id
  role    = "roles/bigquery.dataViewer"
  member  = "serviceAccount:${google_service_account.ecogrid_backend.email}"
}

resource "google_project_iam_member" "aiplatform_user" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.ecogrid_backend.email}"
}

resource "google_project_iam_member" "logging_writer" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.ecogrid_backend.email}"
}

# Cloud Run service (will be deployed via Cloud Build)
resource "google_cloud_run_service" "ecogrid_backend" {
  name     = "ecogrid-backend"
  location = var.region
  
  template {
    spec {
      containers {
        image = "gcr.io/${var.project_id}/ecogrid-backend:latest"
        
        ports {
          container_port = 8080
        }
        
        env {
          name  = "GOOGLE_CLOUD_PROJECT"
          value = var.project_id
        }
        
        env {
          name  = "BIGQUERY_DATASET"
          value = var.dataset_id
        }
        
        env {
          name  = "VERTEX_AI_LOCATION"
          value = var.region
        }
        
        resources {
          limits = {
            cpu    = "2"
            memory = "2Gi"
          }
        }
      }
      
      service_account_name = google_service_account.ecogrid_backend.email
    }
  }
  
  traffic {
    percent         = 100
    latest_revision = true
  }
  
  depends_on = [google_project_service.apis]
}

# Allow unauthenticated access to Cloud Run
resource "google_cloud_run_service_iam_member" "public_access" {
  service  = google_cloud_run_service.ecogrid_backend.name
  location = google_cloud_run_service.ecogrid_backend.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Outputs
output "frontend_url" {
  description = "Frontend website URL"
  value       = "https://storage.googleapis.com/${google_storage_bucket.frontend.name}"
}

output "backend_url" {
  description = "Backend API URL"
  value       = google_cloud_run_service.ecogrid_backend.status[0].url
}

output "bigquery_dataset" {
  description = "BigQuery dataset ID"
  value       = google_bigquery_dataset.ecogrid_dwh.dataset_id
}
