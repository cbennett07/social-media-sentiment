variable "name" {
  description = "Name prefix for networking resources"
  type        = string
}

variable "cidr_block" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "region" {
  description = "Region for the network"
  type        = string
}

variable "enable_nat" {
  description = "Enable NAT for private subnets"
  type        = bool
  default     = true
}

variable "labels" {
  description = "Labels/tags to apply"
  type        = map(string)
  default     = {}
}
