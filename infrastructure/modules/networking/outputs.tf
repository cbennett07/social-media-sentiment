output "vpc_id" {
  description = "VPC/Network ID"
  value       = ""  # Implemented by provider-specific module
}

output "vpc_name" {
  description = "VPC/Network name"
  value       = ""  # Implemented by provider-specific module
}

output "private_subnet_ids" {
  description = "Private subnet IDs"
  value       = []  # Implemented by provider-specific module
}

output "public_subnet_ids" {
  description = "Public subnet IDs"
  value       = []  # Implemented by provider-specific module
}

output "vpc_connector" {
  description = "VPC connector for serverless services"
  value       = ""  # Implemented by provider-specific module
}
