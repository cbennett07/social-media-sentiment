variable "name" {
  type = string
}

variable "region" {
  type = string
}

variable "services" {
  description = "Map of service name to Cloud Run service name"
  type = map(object({
    cloud_run_name = string
    path_prefix    = string  # e.g., "/api/*", "/*"
  }))
}

variable "default_service" {
  description = "The default backend service name (usually frontend)"
  type        = string
}

variable "labels" {
  type    = map(string)
  default = {}
}

variable "network" {
  description = "VPC network name for proxy-only subnet"
  type        = string
  default     = ""
}

# Reserve regional external IP
resource "google_compute_address" "lb_ip" {
  name         = "${var.name}-ip"
  region       = var.region
  address_type = "EXTERNAL"
  network_tier = "STANDARD"
}

# Serverless NEGs for each Cloud Run service
resource "google_compute_region_network_endpoint_group" "serverless_neg" {
  for_each = var.services

  name                  = "${var.name}-${each.key}-neg"
  network_endpoint_type = "SERVERLESS"
  region                = var.region

  cloud_run {
    service = each.value.cloud_run_name
  }
}

# Regional backend services
resource "google_compute_region_backend_service" "backends" {
  for_each = var.services

  name                  = "${var.name}-${each.key}-backend"
  region                = var.region
  protocol              = "HTTP"
  load_balancing_scheme = "EXTERNAL_MANAGED"

  backend {
    group           = google_compute_region_network_endpoint_group.serverless_neg[each.key].id
    balancing_mode  = "UTILIZATION"
    capacity_scaler = 1.0
  }
}

# Regional URL map for routing
resource "google_compute_region_url_map" "urlmap" {
  name            = "${var.name}-urlmap"
  region          = var.region
  default_service = google_compute_region_backend_service.backends[var.default_service].id

  host_rule {
    hosts        = ["*"]
    path_matcher = "main"
  }

  path_matcher {
    name            = "main"
    default_service = google_compute_region_backend_service.backends[var.default_service].id

    dynamic "path_rule" {
      for_each = { for k, v in var.services : k => v if v.path_prefix != "/*" }
      content {
        paths   = [path_rule.value.path_prefix]
        service = google_compute_region_backend_service.backends[path_rule.key].id
      }
    }
  }
}

# Regional HTTP target proxy
resource "google_compute_region_target_http_proxy" "http_proxy" {
  name    = "${var.name}-http-proxy"
  region  = var.region
  url_map = google_compute_region_url_map.urlmap.id
}

# Regional forwarding rule
resource "google_compute_forwarding_rule" "http" {
  name                  = "${var.name}-http-rule"
  region                = var.region
  target                = google_compute_region_target_http_proxy.http_proxy.id
  port_range            = "80"
  ip_address            = google_compute_address.lb_ip.address
  load_balancing_scheme = "EXTERNAL_MANAGED"
  network_tier          = "STANDARD"
  network               = var.network
}

# Outputs
output "ip_address" {
  value = google_compute_address.lb_ip.address
}

output "http_url" {
  value = "http://${google_compute_address.lb_ip.address}"
}
