# Enable required APIs
resource "google_project_service" "apis" {
  for_each = toset([
    "run.googleapis.com",
    "sqladmin.googleapis.com",
    "redis.googleapis.com",
    "secretmanager.googleapis.com",
    "vpcaccess.googleapis.com",
    "servicenetworking.googleapis.com",
    "binaryauthorization.googleapis.com",
    "compute.googleapis.com",
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

  region = var.region
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

  name   = "${local.name_prefix}-collector"
  image  = var.collector_image
  port   = 8080
  region = var.region

  environment = {
    REDIS_URL     = module.redis.connection_url
    QUEUE_TOPIC   = "raw_content"
    RSS_ENABLED   = "true"
  }

  # Only include secrets that have values
  secrets = merge(
    var.newsapi_key != "" ? { NEWSAPI_KEY = module.secrets.secret_refs["newsapi-key"] } : {},
    var.reddit_client_id != "" ? { REDDIT_CLIENT_ID = module.secrets.secret_refs["reddit-client-id"] } : {},
    var.reddit_client_secret != "" ? { REDDIT_CLIENT_SECRET = module.secrets.secret_refs["reddit-client-secret"] } : {}
  )

  cpu               = "1"
  memory            = "512Mi"
  min_instances     = 0
  max_instances     = 5
  vpc_connector     = module.networking.vpc_connector
  allow_unauthenticated = true
  labels            = local.labels

  depends_on = [google_project_service.apis, module.redis, module.secrets]
}

# Processor Service
module "processor" {
  source = "./modules/container-service"

  name   = "${local.name_prefix}-processor"
  image  = var.processor_image
  port   = 8081
  region = var.region

  environment = {
    REDIS_URL            = module.redis.connection_url
    QUEUE_TOPIC          = "raw_content"
    DATABASE_URL         = module.postgres.connection_string
    STORAGE_BUCKET       = module.storage.bucket_name
    LLM_PROVIDER         = var.llm_provider
    AWS_REGION           = var.region
  }

  # Only include secrets that have values
  secrets = merge(
    var.anthropic_api_key != "" ? { ANTHROPIC_API_KEY = module.secrets.secret_refs["anthropic-api-key"] } : {},
    var.openai_api_key != "" ? { OPENAI_API_KEY = module.secrets.secret_refs["openai-api-key"] } : {}
  )

  cpu               = "2"
  memory            = "1Gi"
  min_instances     = 0
  max_instances     = 10
  vpc_connector     = module.networking.vpc_connector
  allow_unauthenticated = true
  labels            = local.labels

  depends_on = [google_project_service.apis, module.redis, module.postgres, module.storage, module.secrets]
}

# API Service
module "api" {
  source = "./modules/container-service"

  name   = "${local.name_prefix}-api"
  image  = var.api_image
  port   = 8082
  region = var.region

  environment = {
    DATABASE_URL = module.postgres.connection_string
    CORS_ORIGINS = jsonencode(["*"])  # Allow all origins for load balancer
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

# Frontend Service
module "frontend" {
  source = "./modules/container-service"

  name   = "${local.name_prefix}-frontend"
  image  = var.frontend_image
  port   = 80
  region = var.region

  # No API_URL needed - load balancer routes /api/* to API backend
  environment = {}

  cpu               = "1"
  memory            = "512Mi"
  min_instances     = 1
  max_instances     = 5
  vpc_connector     = module.networking.vpc_connector
  allow_unauthenticated = true
  labels            = local.labels

  depends_on = [google_project_service.apis, module.api]
}

# ===================
# LOAD BALANCER
# ===================

module "load_balancer" {
  source = "./modules/load-balancer"

  name    = local.name_prefix
  region  = var.region
  network = module.networking.vpc_id

  services = {
    frontend = {
      cloud_run_name = module.frontend.name
      path_prefix    = "/*"
    }
    api = {
      cloud_run_name = module.api.name
      path_prefix    = "/api/*"
    }
    collector = {
      cloud_run_name = module.collector.name
      path_prefix    = "/collect"
    }
    processor = {
      cloud_run_name = module.processor.name
      path_prefix    = "/process"
    }
  }

  default_service = "frontend"
  labels          = local.labels

  depends_on = [google_project_service.apis, module.frontend, module.api, module.collector, module.processor]
}
