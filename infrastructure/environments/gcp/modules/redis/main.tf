variable "name" {
  type = string
}

variable "tier" {
  type    = string
  default = "BASIC"
}

variable "memory_gb" {
  type    = number
  default = 1
}

variable "redis_version" {
  type    = string
  default = "7.0"
}

variable "vpc_network" {
  type = string
}

variable "auth_enabled" {
  type    = bool
  default = true
}

variable "labels" {
  type    = map(string)
  default = {}
}

resource "google_redis_instance" "main" {
  name           = var.name
  tier           = var.tier == "ha" ? "STANDARD_HA" : upper(var.tier)
  memory_size_gb = var.memory_gb
  redis_version  = "REDIS_${replace(var.redis_version, ".", "_")}"

  authorized_network = var.vpc_network
  connect_mode       = "PRIVATE_SERVICE_ACCESS"

  auth_enabled = var.auth_enabled

  labels = var.labels
}

output "host" {
  value = google_redis_instance.main.host
}

output "port" {
  value = google_redis_instance.main.port
}

output "connection_url" {
  value     = var.auth_enabled ? "redis://:${google_redis_instance.main.auth_string}@${google_redis_instance.main.host}:${google_redis_instance.main.port}" : "redis://${google_redis_instance.main.host}:${google_redis_instance.main.port}"
  sensitive = true
}
