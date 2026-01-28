variable "name" {
  description = "Name of the service"
  type        = string
}

variable "image" {
  description = "Container image to deploy"
  type        = string
}

variable "port" {
  description = "Port the container listens on"
  type        = number
  default     = 8080
}

variable "environment" {
  description = "Environment variables for the container"
  type        = map(string)
  default     = {}
}

variable "secrets" {
  description = "Secret references (provider-specific format)"
  type        = map(string)
  default     = {}
}

variable "cpu" {
  description = "CPU allocation (e.g., '1' or '1000m')"
  type        = string
  default     = "1"
}

variable "memory" {
  description = "Memory allocation (e.g., '512Mi' or '1Gi')"
  type        = string
  default     = "512Mi"
}

variable "min_instances" {
  description = "Minimum number of instances"
  type        = number
  default     = 0
}

variable "max_instances" {
  description = "Maximum number of instances"
  type        = number
  default     = 10
}

variable "allow_unauthenticated" {
  description = "Allow unauthenticated access"
  type        = bool
  default     = false
}

variable "vpc_connector" {
  description = "VPC connector for private networking (provider-specific)"
  type        = string
  default     = null
}

variable "labels" {
  description = "Labels/tags to apply"
  type        = map(string)
  default     = {}
}
