# Enable required APIs
resource "google_project_service" "apis" {
  for_each = toset([
    "run.googleapis.com",
    "sqladmin.googleapis.com",
    "redis.googleapis.com",
    "secretmanager.googleapis.com",
    "vpcaccess.googleapis.com",
    "servicenetworking.googleapis.com",
  ])

  service            = each.value
  disable_on_destroy = false
}

# Random suffix for unique resource names
resource "random_id" "suffix" {
  byte_length = 4
}

locals {
  name_prefix = "sentiment-${var.environment}"
  labels = {
    environment = var.environment
    app         = "sentiment-analysis"
    managed_by  = "terraform"
  }
}

# ===================
# NETWORKING
# ===================

module "networking" {
  source = "./modules/networking"

  name   = local.name_prefix
  region = var.region
  labels = local.labels

  depends_on = [google_project_service.apis]
}

# ===================
# SECRETS
# ===================

module "secrets" {
  source = "./modules/secrets"

  secrets = {
    newsapi-key          = var.newsapi_key
    reddit-client-id     = var.reddit_client_id
    reddit-client-secret = var.reddit_client_secret
    anthropic-api-key    = var.anthropic_api_key
    openai-api-key       = var.openai_api_key
  }

  labels = local.labels

  depends_on = [google_project_service.apis]
}

# ===================
# DATABASE
# ===================

module "postgres" {
  source = "./modules/postgres"

  name             = "${local.name_prefix}-db-${random_id.suffix.hex}"
  database_name    = "sentiment"
  tier             = var.db_tier
  postgres_version = "16"
  vpc_network      = module.networking.vpc_id
  public_ip        = false
  backup_enabled   = var.environment == "prod"
  labels           = local.labels

  depends_on = [google_project_service.apis, module.networking]
}

# ===================
# REDIS
# ===================

module "redis" {
  source = "./modules/redis"

  name          = "${local.name_prefix}-redis"
  tier          = var.redis_tier
  memory_gb     = var.redis_memory_gb
  redis_version = "7.0"
  vpc_network   = module.networking.vpc_id
  labels        = local.labels

  depends_on = [google_project_service.apis, module.networking]
}

# ===================
# OBJECT STORAGE
# ===================

module "storage" {
  source = "./modules/object-storage"

  name          = "${local.name_prefix}-raw-${random_id.suffix.hex}"
  location      = var.region
  storage_class = "STANDARD"

  lifecycle_rules = [
    {
      age_days      = 90
      storage_class = "NEARLINE"
    },
    {
      age_days = 365
      delete   = true
    }
  ]

  labels = local.labels

  depends_on = [google_project_service.apis]
}

# ===================
# CONTAINER SERVICES
# ===================

# Collector Service
module "collector" {
  source = "./modules/container-service"

  name  = "${local.name_prefix}-collector"
  image = var.collector_image
  port  = 8080

  environment = {
    REDIS_URL     = module.redis.connection_url
    QUEUE_TOPIC   = "raw_content"
    RSS_ENABLED   = "true"
  }

  secrets = {
    NEWSAPI_KEY          = module.secrets.secret_refs["newsapi-key"]
    REDDIT_CLIENT_ID     = module.secrets.secret_refs["reddit-client-id"]
    REDDIT_CLIENT_SECRET = module.secrets.secret_refs["reddit-client-secret"]
  }

  cpu               = "1"
  memory            = "512Mi"
  min_instances     = 0
  max_instances     = 5
  vpc_connector     = module.networking.vpc_connector
  allow_unauthenticated = true
  labels            = local.labels

  depends_on = [google_project_service.apis, module.redis]
}

# Processor Service
module "processor" {
  source = "./modules/container-service"

  name  = "${local.name_prefix}-processor"
  image = var.processor_image
  port  = 8081

  environment = {
    REDIS_URL            = module.redis.connection_url
    QUEUE_TOPIC          = "raw_content"
    DATABASE_URL         = module.postgres.connection_string
    STORAGE_BUCKET       = module.storage.bucket_name
    LLM_PROVIDER         = var.llm_provider
    AWS_REGION           = var.region
  }

  secrets = {
    ANTHROPIC_API_KEY = module.secrets.secret_refs["anthropic-api-key"]
    OPENAI_API_KEY    = module.secrets.secret_refs["openai-api-key"]
  }

  cpu               = "2"
  memory            = "1Gi"
  min_instances     = 0
  max_instances     = 10
  vpc_connector     = module.networking.vpc_connector
  allow_unauthenticated = false
  labels            = local.labels

  depends_on = [google_project_service.apis, module.redis, module.postgres, module.storage]
}

# API Service
module "api" {
  source = "./modules/container-service"

  name  = "${local.name_prefix}-api"
  image = var.api_image
  port  = 8082

  environment = {
    DATABASE_URL = module.postgres.connection_string
    CORS_ORIGINS = jsonencode(["https://${local.name_prefix}-api.run.app"])
  }

  cpu               = "1"
  memory            = "512Mi"
  min_instances     = 1  # Keep warm for API
  max_instances     = 10
  vpc_connector     = module.networking.vpc_connector
  allow_unauthenticated = true
  labels            = local.labels

  depends_on = [google_project_service.apis, module.postgres]
}
