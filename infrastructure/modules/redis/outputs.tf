output "host" {
  description = "Redis host"
  value       = ""  # Implemented by provider-specific module
}

output "port" {
  description = "Redis port"
  value       = 6379
}

output "connection_url" {
  description = "Redis connection URL"
  value       = ""  # Implemented by provider-specific module
  sensitive   = true
}
