# EcoGridIQ Terraform Outputs

output "project_id" {
  description = "The GCP project ID"
  value       = var.project_id
}

output "region" {
  description = "The GCP region"
  value       = var.region
}

output "frontend_url" {
  description = "URL of the deployed frontend application"
  value       = "https://storage.googleapis.com/${google_storage_bucket.frontend.name}"
}

output "backend_url" {
  description = "URL of the deployed backend API"
  value       = google_cloud_run_service.ecogrid_backend.status[0].url
}

output "bigquery_dataset" {
  description = "BigQuery dataset ID for energy data"
  value       = google_bigquery_dataset.ecogrid_dwh.dataset_id
}

output "service_account_email" {
  description = "Email of the service account used by the backend"
  value       = google_service_account.ecogrid_backend.email
}

output "storage_bucket" {
  description = "Name of the Cloud Storage bucket for frontend"
  value       = google_storage_bucket.frontend.name
}

output "deployment_info" {
  description = "Deployment information for easy reference"
  value = {
    frontend_url = "https://storage.googleapis.com/${google_storage_bucket.frontend.name}"
    backend_url  = google_cloud_run_service.ecogrid_backend.status[0].url
    dataset      = google_bigquery_dataset.ecogrid_dwh.dataset_id
    region       = var.region
    project      = var.project_id
  }
}
