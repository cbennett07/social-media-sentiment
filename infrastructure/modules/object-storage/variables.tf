variable "name" {
  description = "Name of the bucket"
  type        = string
}

variable "location" {
  description = "Location/region for the bucket"
  type        = string
}

variable "storage_class" {
  description = "Storage class (standard, nearline, coldline, archive)"
  type        = string
  default     = "standard"
}

variable "versioning_enabled" {
  description = "Enable object versioning"
  type        = bool
  default     = false
}

variable "lifecycle_rules" {
  description = "Lifecycle rules for object management"
  type = list(object({
    age_days        = number
    storage_class   = optional(string)
    delete          = optional(bool, false)
    prefix          = optional(string)
  }))
  default = []
}

variable "cors_origins" {
  description = "CORS allowed origins"
  type        = list(string)
  default     = []
}

variable "public_access" {
  description = "Allow public access to objects"
  type        = bool
  default     = false
}

variable "labels" {
  description = "Labels/tags to apply"
  type        = map(string)
  default     = {}
}
