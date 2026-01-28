output "connection_string" {
  description = "Database connection string"
  value       = ""  # Implemented by provider-specific module
  sensitive   = true
}

output "host" {
  description = "Database host"
  value       = ""  # Implemented by provider-specific module
}

output "port" {
  description = "Database port"
  value       = 5432
}

output "database_name" {
  description = "Database name"
  value       = var.database_name
}
