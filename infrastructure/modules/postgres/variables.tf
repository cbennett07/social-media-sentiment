variable "name" {
  description = "Name of the database instance"
  type        = string
}

variable "database_name" {
  description = "Name of the database to create"
  type        = string
  default     = "sentiment"
}

variable "tier" {
  description = "Instance tier/size (provider-specific)"
  type        = string
  default     = "small"  # Maps to provider-specific tiers
}

variable "storage_gb" {
  description = "Storage size in GB"
  type        = number
  default     = 10
}

variable "postgres_version" {
  description = "PostgreSQL version"
  type        = string
  default     = "16"
}

variable "vpc_network" {
  description = "VPC network for private IP (provider-specific)"
  type        = string
  default     = null
}

variable "public_ip" {
  description = "Enable public IP access"
  type        = bool
  default     = false
}

variable "backup_enabled" {
  description = "Enable automated backups"
  type        = bool
  default     = true
}

variable "labels" {
  description = "Labels/tags to apply"
  type        = map(string)
  default     = {}
}
