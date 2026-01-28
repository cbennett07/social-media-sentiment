variable "secrets" {
  description = "Map of secret names to their values"
  type        = map(string)
  sensitive   = true
}

variable "labels" {
  description = "Labels/tags to apply"
  type        = map(string)
  default     = {}
}
