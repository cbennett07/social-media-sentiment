output "collector_url" {
  description = "URL of the collector service"
  value       = module.collector.url
}

output "processor_url" {
  description = "URL of the processor service"
  value       = module.processor.url
}

output "api_url" {
  description = "URL of the API service"
  value       = module.api.url
}

output "database_connection" {
  description = "Database connection string"
  value       = module.postgres.connection_string
  sensitive   = true
}

output "redis_host" {
  description = "Redis host"
  value       = module.redis.host
}

output "storage_bucket" {
  description = "Storage bucket name"
  value       = module.storage.bucket_name
}
