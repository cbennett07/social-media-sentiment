# Infrastructure

CSP-agnostic Terraform infrastructure for the Sentiment Analysis application.

## Structure

```
infrastructure/
├── modules/                    # Abstract module interfaces
│   ├── container-service/      # Container deployment (Cloud Run, ECS, etc.)
│   ├── postgres/               # PostgreSQL database
│   ├── redis/                  # Redis cache/queue
│   ├── object-storage/         # S3-compatible storage
│   ├── secrets/                # Secret management
│   └── networking/             # VPC and networking
│
└── environments/               # Provider-specific implementations
    ├── gcp/                    # Google Cloud Platform
    │   ├── main.tf
    │   ├── variables.tf
    │   ├── outputs.tf
    │   └── modules/            # GCP-specific module implementations
    │
    ├── aws/                    # Amazon Web Services (skeleton)
    │   ├── main.tf
    │   ├── variables.tf
    │   └── modules/
    │
    └── local/                  # Local Docker development
        └── docker-compose.yml  # (symlink to root)
```

## Module Interface

Each module in `modules/` defines a standard interface (variables and outputs) that
provider-specific implementations must satisfy. This allows the main configuration
to remain consistent across cloud providers.

| Module | Purpose | GCP Service | AWS Service |
|--------|---------|-------------|-------------|
| container-service | Run containers | Cloud Run | ECS Fargate / App Runner |
| postgres | SQL database | Cloud SQL | RDS |
| redis | Cache/queue | Memorystore | ElastiCache |
| object-storage | Blob storage | Cloud Storage | S3 |
| secrets | Secret management | Secret Manager | Secrets Manager |
| networking | VPC/networking | VPC | VPC |

## Usage

### Prerequisites

1. Install Terraform >= 1.5.0
2. Authenticate with your cloud provider:
   - GCP: `gcloud auth application-default login`
   - AWS: `aws configure`

### Deploy to GCP

```bash
cd infrastructure/environments/gcp

# Copy and edit variables
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values

# Initialize
terraform init

# Plan
terraform plan

# Apply
terraform apply
```

### Deploy to AWS

```bash
cd infrastructure/environments/aws

# Copy and edit variables
cp terraform.tfvars.example terraform.tfvars

terraform init
terraform plan
terraform apply
```

### Local Development

Use Docker Compose from the project root:

```bash
# From project root
make up
```

## Container Images

Before deploying, build and push container images to your registry:

### GCP (Artifact Registry)

```bash
# Configure Docker for GCR
gcloud auth configure-docker gcr.io

# Build and push
docker build -t gcr.io/PROJECT/sentiment-collector:latest -f Dockerfile .
docker build -t gcr.io/PROJECT/sentiment-processor:latest -f processor/Dockerfile .
docker build -t gcr.io/PROJECT/sentiment-api:latest -f api/Dockerfile .

docker push gcr.io/PROJECT/sentiment-collector:latest
docker push gcr.io/PROJECT/sentiment-processor:latest
docker push gcr.io/PROJECT/sentiment-api:latest
```

### AWS (ECR)

```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin ACCOUNT.dkr.ecr.us-east-1.amazonaws.com

# Build and push
docker build -t ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/sentiment-collector:latest -f Dockerfile .
docker push ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/sentiment-collector:latest
# ... repeat for other images
```

## Secrets

Sensitive values (API keys) should be provided via:

1. **Environment variables**: `TF_VAR_anthropic_api_key=xxx terraform apply`
2. **terraform.tfvars** (gitignored): Add secrets to your local tfvars file
3. **CI/CD secrets**: Configure in your pipeline (GitHub Actions, Cloud Build, etc.)

Never commit secrets to the repository.

## Cost Considerations

### Development (minimal cost)

- GCP: Cloud Run (scale to zero), db-f1-micro, BASIC Redis
- AWS: App Runner, db.t3.micro, cache.t3.micro

### Production (higher availability)

- GCP: Cloud Run (min instances), db-custom-2-4096, STANDARD_HA Redis
- AWS: ECS Fargate, db.r6g.large, cache.r6g.large with replication

## Adding a New Cloud Provider

1. Create a new directory under `environments/`
2. Implement each module interface with provider-specific resources
3. Wire modules together in `main.tf`
4. Document provider-specific setup in this README

The module interfaces in `modules/` define the contract - your implementation
just needs to satisfy the same inputs and outputs.
