# EcoGridIQ Terraform Variables

variable "project_id" {
  description = "The GCP project ID where resources will be created"
  type        = string
}

variable "region" {
  description = "The GCP region for resources"
  type        = string
  default     = "us-central1"
}

variable "dataset_id" {
  description = "BigQuery dataset ID for energy data"
  type        = string
  default     = "ecogrid_dwh"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "enable_monitoring" {
  description = "Enable monitoring and alerting"
  type        = bool
  default     = true
}

variable "enable_vertex_ai" {
  description = "Enable Vertex AI features"
  type        = bool
  default     = true
}

variable "backup_retention_days" {
  description = "Number of days to retain BigQuery data backups"
  type        = number
  default     = 30
}
