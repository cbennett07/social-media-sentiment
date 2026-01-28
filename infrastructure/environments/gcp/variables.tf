variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

# Container images
variable "collector_image" {
  description = "Collector service container image"
  type        = string
}

variable "processor_image" {
  description = "Processor service container image"
  type        = string
}

variable "api_image" {
  description = "API service container image"
  type        = string
}

# API Keys (sensitive)
variable "newsapi_key" {
  description = "NewsAPI API key"
  type        = string
  sensitive   = true
  default     = ""
}

variable "reddit_client_id" {
  description = "Reddit client ID"
  type        = string
  sensitive   = true
  default     = ""
}

variable "reddit_client_secret" {
  description = "Reddit client secret"
  type        = string
  sensitive   = true
  default     = ""
}

variable "anthropic_api_key" {
  description = "Anthropic API key"
  type        = string
  sensitive   = true
  default     = ""
}

variable "openai_api_key" {
  description = "OpenAI API key"
  type        = string
  sensitive   = true
  default     = ""
}

variable "llm_provider" {
  description = "LLM provider to use (anthropic or openai)"
  type        = string
  default     = "anthropic"
}

# Database
variable "db_tier" {
  description = "Cloud SQL instance tier"
  type        = string
  default     = "db-f1-micro"  # Small for dev, use db-custom-X-Y for prod
}

# Redis
variable "redis_tier" {
  description = "Memorystore tier (BASIC or STANDARD_HA)"
  type        = string
  default     = "BASIC"
}

variable "redis_memory_gb" {
  description = "Redis memory in GB"
  type        = number
  default     = 1
}
