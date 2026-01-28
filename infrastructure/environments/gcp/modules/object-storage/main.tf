variable "name" {
  type = string
}

variable "location" {
  type = string
}

variable "storage_class" {
  type    = string
  default = "STANDARD"
}

variable "versioning_enabled" {
  type    = bool
  default = false
}

variable "lifecycle_rules" {
  type = list(object({
    age_days      = number
    storage_class = optional(string)
    delete        = optional(bool, false)
    prefix        = optional(string)
  }))
  default = []
}

variable "cors_origins" {
  type    = list(string)
  default = []
}

variable "public_access" {
  type    = bool
  default = false
}

variable "labels" {
  type    = map(string)
  default = {}
}

resource "google_storage_bucket" "bucket" {
  name          = var.name
  location      = var.location
  storage_class = upper(var.storage_class)

  uniform_bucket_level_access = true
  public_access_prevention    = var.public_access ? "inherited" : "enforced"

  versioning {
    enabled = var.versioning_enabled
  }

  dynamic "lifecycle_rule" {
    for_each = var.lifecycle_rules
    content {
      condition {
        age = lifecycle_rule.value.age_days
        matches_prefix = lifecycle_rule.value.prefix != null ? [lifecycle_rule.value.prefix] : []
      }
      action {
        type          = lifecycle_rule.value.delete ? "Delete" : "SetStorageClass"
        storage_class = lifecycle_rule.value.delete ? null : upper(lifecycle_rule.value.storage_class)
      }
    }
  }

  dynamic "cors" {
    for_each = length(var.cors_origins) > 0 ? [1] : []
    content {
      origin          = var.cors_origins
      method          = ["GET", "HEAD", "PUT", "POST", "DELETE"]
      response_header = ["*"]
      max_age_seconds = 3600
    }
  }

  labels = var.labels
}

# Service account for S3-compatible access
resource "google_service_account" "storage_sa" {
  account_id   = "${replace(var.name, "-", "")}sa"
  display_name = "Storage access for ${var.name}"
}

resource "google_storage_bucket_iam_member" "storage_access" {
  bucket = google_storage_bucket.bucket.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.storage_sa.email}"
}

resource "google_service_account_key" "storage_key" {
  service_account_id = google_service_account.storage_sa.name
}

output "bucket_name" {
  value = google_storage_bucket.bucket.name
}

output "bucket_url" {
  value = google_storage_bucket.bucket.url
}

output "s3_endpoint" {
  value = "https://storage.googleapis.com"
}

output "access_key_id" {
  value     = google_service_account.storage_sa.email
  sensitive = true
}

output "secret_access_key" {
  value     = base64decode(google_service_account_key.storage_key.private_key)
  sensitive = true
}
