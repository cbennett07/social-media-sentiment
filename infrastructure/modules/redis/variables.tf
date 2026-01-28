variable "name" {
  description = "Name of the Redis instance"
  type        = string
}

variable "tier" {
  description = "Instance tier (basic, standard, ha)"
  type        = string
  default     = "basic"
}

variable "memory_gb" {
  description = "Memory size in GB"
  type        = number
  default     = 1
}

variable "redis_version" {
  description = "Redis version"
  type        = string
  default     = "7.0"
}

variable "vpc_network" {
  description = "VPC network for private access"
  type        = string
  default     = null
}

variable "auth_enabled" {
  description = "Enable Redis AUTH"
  type        = bool
  default     = true
}

variable "labels" {
  description = "Labels/tags to apply"
  type        = map(string)
  default     = {}
}
