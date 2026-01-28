output "url" {
  description = "URL of the deployed service"
  value       = ""  # Implemented by provider-specific module
}

output "name" {
  description = "Name of the deployed service"
  value       = var.name
}
