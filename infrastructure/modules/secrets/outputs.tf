output "secret_refs" {
  description = "Map of secret names to their provider-specific references"
  value       = {}  # Implemented by provider-specific module
}
