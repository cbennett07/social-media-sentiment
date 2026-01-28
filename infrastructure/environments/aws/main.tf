# AWS Implementation
# This is a skeleton - implement modules similar to GCP

locals {
  name_prefix = "sentiment-${var.environment}"
}

resource "random_id" "suffix" {
  byte_length = 4
}

# ===================
# NETWORKING
# ===================

# TODO: Implement VPC with public/private subnets
# module "networking" {
#   source = "./modules/networking"
#   ...
# }

# ===================
# SECRETS
# ===================

# TODO: Implement AWS Secrets Manager
# module "secrets" {
#   source = "./modules/secrets"
#   ...
# }

# ===================
# DATABASE (RDS)
# ===================

# TODO: Implement RDS PostgreSQL
# module "postgres" {
#   source = "./modules/postgres"
#   ...
# }

# ===================
# REDIS (ElastiCache)
# ===================

# TODO: Implement ElastiCache Redis
# module "redis" {
#   source = "./modules/redis"
#   ...
# }

# ===================
# OBJECT STORAGE (S3)
# ===================

resource "aws_s3_bucket" "raw_content" {
  bucket = "${local.name_prefix}-raw-${random_id.suffix.hex}"
}

resource "aws_s3_bucket_versioning" "raw_content" {
  bucket = aws_s3_bucket.raw_content.id
  versioning_configuration {
    status = "Disabled"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "raw_content" {
  bucket = aws_s3_bucket.raw_content.id

  rule {
    id     = "archive-old"
    status = "Enabled"

    transition {
      days          = 90
      storage_class = "STANDARD_IA"
    }

    expiration {
      days = 365
    }
  }
}

# ===================
# CONTAINER SERVICES (ECS or App Runner)
# ===================

# TODO: Implement ECS Fargate or App Runner services
# module "collector" {
#   source = "./modules/container-service"
#   ...
# }

# module "processor" {
#   source = "./modules/container-service"
#   ...
# }

# module "api" {
#   source = "./modules/container-service"
#   ...
# }

output "storage_bucket" {
  value = aws_s3_bucket.raw_content.bucket
}
