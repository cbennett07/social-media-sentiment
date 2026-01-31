variable "secrets" {
  type      = map(string)
  sensitive = true
}

variable "labels" {
  type    = map(string)
  default = {}
}

variable "region" {
  type    = string
  default = "europe-west1"
}

locals {
  # Extract keys as non-sensitive for for_each iteration
  secret_keys = nonsensitive(toset(keys(var.secrets)))
  # Filter out empty secrets for version creation
  non_empty_secrets = nonsensitive(toset([for k, v in var.secrets : k if v != ""]))
}

resource "google_secret_manager_secret" "secrets" {
  for_each  = local.secret_keys
  secret_id = each.key

  labels = var.labels

  replication {
    user_managed {
      replicas {
        location = var.region
      }
    }
  }
}

resource "google_secret_manager_secret_version" "versions" {
  for_each    = local.non_empty_secrets
  secret      = google_secret_manager_secret.secrets[each.key].id
  secret_data = var.secrets[each.key]
}

# Get project info for compute service account
data "google_project" "current" {}

# Allow Cloud Run (compute) service account to access secrets
resource "google_secret_manager_secret_iam_member" "cloud_run_access" {
  for_each  = local.non_empty_secrets
  secret_id = google_secret_manager_secret.secrets[each.key].id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${data.google_project.current.number}-compute@developer.gserviceaccount.com"
}

output "secret_refs" {
  description = "Map of secret names to their Cloud Run secret references"
  value = {
    for name, secret in google_secret_manager_secret.secrets :
    name => "${secret.secret_id}:latest"
  }
}
