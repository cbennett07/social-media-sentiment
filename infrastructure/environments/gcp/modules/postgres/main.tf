variable "name" {
  type = string
}

variable "database_name" {
  type    = string
  default = "sentiment"
}

variable "tier" {
  type    = string
  default = "db-f1-micro"
}

variable "storage_gb" {
  type    = number
  default = 10
}

variable "postgres_version" {
  type    = string
  default = "16"
}

variable "vpc_network" {
  type = string
}

variable "public_ip" {
  type    = bool
  default = false
}

variable "backup_enabled" {
  type    = bool
  default = true
}

variable "labels" {
  type    = map(string)
  default = {}
}

resource "random_password" "db_password" {
  length  = 24
  special = false
}

resource "google_sql_database_instance" "main" {
  name             = var.name
  database_version = "POSTGRES_${var.postgres_version}"

  settings {
    tier      = var.tier
    disk_size = var.storage_gb
    disk_type = "PD_SSD"

    ip_configuration {
      ipv4_enabled    = var.public_ip
      private_network = var.vpc_network
    }

    backup_configuration {
      enabled                        = var.backup_enabled
      point_in_time_recovery_enabled = var.backup_enabled
      start_time                     = "03:00"
    }

    user_labels = var.labels
  }

  deletion_protection = false  # Set to true for production
}

resource "google_sql_database" "database" {
  name     = var.database_name
  instance = google_sql_database_instance.main.name
}

resource "google_sql_user" "user" {
  name     = "app"
  instance = google_sql_database_instance.main.name
  password = random_password.db_password.result
}

output "connection_string" {
  value     = "postgresql://${google_sql_user.user.name}:${random_password.db_password.result}@${google_sql_database_instance.main.private_ip_address}:5432/${var.database_name}"
  sensitive = true
}

output "host" {
  value = google_sql_database_instance.main.private_ip_address
}

output "port" {
  value = 5432
}

output "database_name" {
  value = var.database_name
}

output "instance_connection_name" {
  value = google_sql_database_instance.main.connection_name
}
