variable "secrets" {
  type      = map(string)
  sensitive = true
}

variable "labels" {
  type    = map(string)
  default = {}
}

resource "google_secret_manager_secret" "secrets" {
  for_each  = var.secrets
  secret_id = each.key

  labels = var.labels

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "versions" {
  for_each    = var.secrets
  secret      = google_secret_manager_secret.secrets[each.key].id
  secret_data = each.value
}

output "secret_refs" {
  description = "Map of secret names to their Cloud Run secret references"
  value = {
    for name, secret in google_secret_manager_secret.secrets :
    name => "${secret.secret_id}:latest"
  }
}
