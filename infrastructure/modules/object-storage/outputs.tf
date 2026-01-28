output "bucket_name" {
  description = "Name of the created bucket"
  value       = var.name
}

output "bucket_url" {
  description = "URL of the bucket"
  value       = ""  # Implemented by provider-specific module
}

output "s3_endpoint" {
  description = "S3-compatible endpoint URL"
  value       = ""  # Implemented by provider-specific module
}
