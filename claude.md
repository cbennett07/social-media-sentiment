# Claude.md - Development Notes

## Project Overview

Social media sentiment analysis platform that collects articles from RSS feeds, NewsAPI, Reddit, and Twitter, processes them through an LLM for sentiment analysis, and displays results in a dashboard.

## Resuming After Restart

### If Docker containers are stopped:

```bash
cd /repos/social-media-sentiment

# Check if containers are running
docker compose ps

# Start all services (data persists in Docker volumes)
docker compose up -d

# If you need to rebuild after code changes
docker compose up -d --build
```

### If starting fresh (no containers, no volumes):

```bash
cd /repos/social-media-sentiment

# Ensure .env has your ANTHROPIC_API_KEY
cat .env | grep ANTHROPIC_API_KEY

# If missing, add it:
# Edit .env and set: ANTHROPIC_API_KEY=sk-ant-api03-...

# Start all services
docker compose up -d --build

# Collect some articles
curl -X POST http://localhost:8080/collect \
  -H "Content-Type: application/json" \
  -d '{"phrase": "AI", "sources": ["rss"]}'

# Process them
curl -X POST http://localhost:8081/process \
  -H "Content-Type: application/json" \
  -d '{"batch_size": 20}'
```

### Verify everything is working:

```bash
# Check all services are healthy
docker compose ps

# Test endpoints
curl http://localhost:8080/health  # Collector
curl http://localhost:8081/health  # Processor
curl http://localhost:8082/health  # API
curl -I http://localhost:3000      # Frontend

# Check database has data
docker compose exec -T postgres psql -U postgres -d sentiment \
  -c "SELECT COUNT(*) FROM processed_items;"
```

## Local Development

### Prerequisites
- Docker and Docker Compose
- API keys (optional, for full functionality):
  - `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` - Required for sentiment analysis
  - `NEWSAPI_KEY` - For NewsAPI source
  - `REDDIT_CLIENT_ID` / `REDDIT_CLIENT_SECRET` - For Reddit source
  - `TWITTER_BEARER_TOKEN` - For Twitter source

### Quick Start

```bash
# Copy environment file and add your API keys
cp .env.example .env
# Edit .env to add your ANTHROPIC_API_KEY

# Start all services
docker compose up -d --build

# Collect articles (RSS works without API keys)
curl -X POST http://localhost:8080/collect \
  -H "Content-Type: application/json" \
  -d '{"phrase": "technology", "sources": ["rss"]}'

# Process collected articles (requires LLM API key)
curl -X POST http://localhost:8081/process \
  -H "Content-Type: application/json" \
  -d '{"batch_size": 20}'
```

### Services

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | React dashboard |
| Collector | http://localhost:8080 | Article collection API |
| Processor | http://localhost:8081 | Sentiment analysis API |
| API | http://localhost:8082 | Data query API |
| MinIO Console | http://localhost:9001 | Object storage (minioadmin/minioadmin) |
| PostgreSQL | localhost:5432 | Database (postgres/postgres) |
| Redis | localhost:6379 | Message queue |

## Recent Changes (2026-01-29)

### Bug Fixes

1. **Timezone comparison fix** (`main.py:63-64`)
   - Changed `datetime.now()` to `datetime.now(timezone.utc)` to fix "can't compare offset-naive and offset-aware datetimes" error in RSS collection

2. **Sentiment timeline improvements** (`api/database.py`)
   - Added default date ranges per granularity to show appropriate time windows:
     - Hour: last 2 days
     - Day: last 14 days
     - Week: last 12 weeks
     - Month: last year
   - Removed zero-filled gaps - only shows periods with actual data

3. **Dynamic granularity buttons** (`frontend/src/App.tsx`)
   - Granularity options (Hour/Day/Week/Month) now dynamically show/hide based on data range
   - Requires minimum data span: hour (2.4h), day (1d), week (14d), month (60d)

### API Enhancements

1. **Searches endpoint** (`api/database.py`, `api/models.py`)
   - Added `first_published` and `last_published` fields to `/searches` response
   - These represent the actual article publication dates (vs collection dates)

## Recent Changes (2026-01-31)

### GCP Deployment Fixes

1. **Regional Load Balancer** (`infrastructure/environments/gcp/modules/load-balancer/main.tf`)
   - Global load balancers blocked by org constraint, switched to Regional External Application Load Balancer
   - Added proxy-only subnet for EXTERNAL_MANAGED load balancing scheme
   - Uses STANDARD network tier for external IP

2. **Processor 403 Error Fix** (`infrastructure/environments/gcp/main.tf:196`)
   - Changed `allow_unauthenticated = false` to `true` for processor service
   - Load balancer needs unauthenticated access to route traffic

3. **GCS Storage Support** (`processor/storage/gcs.py`)
   - Added Google Cloud Storage backend for processor
   - Previously only had S3/MinIO support which failed on GCP
   - Auto-detects GCS when `STORAGE_ENDPOINT_URL` is not set
   - Uses Application Default Credentials on Cloud Run

4. **Docker Build Fix** (`.dockerignore`)
   - Added `.dockerignore` to exclude `.env` file from container builds
   - `.env` had `STORAGE_ENDPOINT_URL=http://localhost:9000` which broke GCP deployment

5. **API Route Prefix** (`api/main.py`)
   - Added `/api` prefix to all API routes using FastAPI router
   - Required for load balancer URL map path matching (`/api/*` -> API backend)
   - Health check remains at both `/health` (Cloud Run) and `/api/health` (load balancer)

### Vertex AI Claude Integration

Switched from direct Anthropic API to Vertex AI for LLM processing. All billing now goes through GCP.

1. **Vertex AI Client** (`processor/llm/vertex.py`)
   - Added `VertexAIClaudeClient` using `AnthropicVertex` from the anthropic SDK
   - Uses Application Default Credentials (no API key needed on Cloud Run)
   - Model: `claude-sonnet-4-5` in `us-east5` region

2. **LLM Provider Configuration** (`processor/config.py`, `processor/main.py`)
   - Added `llm_provider = "vertex"` option (alongside "anthropic" and "openai")
   - Added `GCP_PROJECT_ID` and `GCP_REGION` environment variables
   - Auto-selects Vertex AI when `LLM_PROVIDER=vertex`

3. **Terraform Updates** (`infrastructure/environments/gcp/main.tf`)
   - Enabled `aiplatform.googleapis.com` API
   - Set `LLM_PROVIDER=vertex` for processor
   - Set `GCP_REGION=us-east5` for Vertex AI (Claude not available in all regions)

4. **Requirements** (`requirements-processor.txt`)
   - Changed `anthropic>=0.18.0` to `anthropic[vertex]>=0.18.0` for Vertex AI support

### Enabling Vertex AI Claude

To use Claude on Vertex AI, you must:
1. Go to Vertex AI Model Garden in GCP Console
2. Find Claude model (e.g., `claude-sonnet-4-5`)
3. Click "Enable" and accept Terms & Conditions
4. Note: Model availability varies by region (us-east5 works for Claude Sonnet 4.5)

## Architecture Notes

- **Collector** pushes raw articles to Redis queue
- **Processor** pulls from queue, calls Vertex AI Claude for sentiment analysis, stores results in PostgreSQL and GCS
- **API** serves processed data to frontend
- **Frontend** displays sentiment charts, themes, entities, and article list

### LLM Provider Options

The processor supports multiple LLM providers via `LLM_PROVIDER` environment variable:

| Provider | Value | Requirements | Billing |
|----------|-------|--------------|---------|
| Vertex AI Claude | `vertex` | GCP project with Vertex AI enabled | GCP billing |
| Anthropic API | `anthropic` | `ANTHROPIC_API_KEY` | Anthropic billing |
| OpenAI API | `openai` | `OPENAI_API_KEY` | OpenAI billing |

Current GCP deployment uses **Vertex AI** (`LLM_PROVIDER=vertex`) with Claude Sonnet 4.5.

## GCP Deployment

### Current Deployment

**Public URL: http://35.210.81.215**

- Project ID: `social-media-sentiment-485915`
- Region: `europe-west1`
- Load Balancer: Regional External Application Load Balancer

### Accessing the Deployed App

The load balancer routes traffic as follows:
- `/` - Frontend dashboard
- `/api/*` - API service (searches, items, themes, sentiment, entities)
- `/collect` - Collector service
- `/process` - Processor service

### Collect and Process Data on GCP

```bash
# Collect articles (RSS works without API keys)
curl -X POST http://35.210.81.215/collect \
  -H "Content-Type: application/json" \
  -d '{"phrase": "AI", "sources": ["rss"]}'

# Process collected articles (uses Vertex AI Claude - billed through GCP)
curl -X POST http://35.210.81.215/process \
  -H "Content-Type: application/json" \
  -d '{"batch_size": 20}'

# Check API health
curl http://35.210.81.215/api/health

# List searches
curl http://35.210.81.215/api/searches
```

### Infrastructure Components (GCP)

| Component | Service | Details |
|-----------|---------|---------|
| Frontend | Cloud Run | `sentiment-dev-frontend` |
| API | Cloud Run | `sentiment-dev-api` |
| Collector | Cloud Run | `sentiment-dev-collector` |
| Processor | Cloud Run | `sentiment-dev-processor` |
| Database | Cloud SQL | PostgreSQL 16, `sentiment-dev-db-*` |
| Cache | Memorystore | Redis 7.0, `sentiment-dev-redis` |
| Storage | Cloud Storage | `sentiment-dev-raw-*` |
| LLM | Vertex AI | Claude Sonnet 4.5 (`us-east5`) |
| Load Balancer | Regional External ALB | Routes to Cloud Run via serverless NEGs |

### Redeploying Services

```bash
cd infrastructure/environments/gcp

# Rebuild and push a service image (must use linux/amd64 for Cloud Run)
docker buildx build --platform linux/amd64 -t eu.gcr.io/social-media-sentiment-485915/api:latest -f api/Dockerfile --push .

# Force Cloud Run to pull new image
gcloud run services update sentiment-dev-api \
  --image=eu.gcr.io/social-media-sentiment-485915/api:latest \
  --region=europe-west1 \
  --project=social-media-sentiment-485915

# Or redeploy all via Terraform
terraform apply
```

### Notes on Load Balancer Setup

- Global load balancers are blocked by org constraint (`constraints/compute.disableGlobalLoadBalancing`)
- Using Regional External Application Load Balancer instead
- Requires a proxy-only subnet (`sentiment-dev-proxy-only`) in the VPC
- Uses STANDARD network tier for the external IP
- API routes are prefixed with `/api` to work with URL map path matching

### Fresh GCP Deployment

If deploying to a new GCP project:

1. **Create a GCP Project** and note the project ID

2. **Authenticate with gcloud**:
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   gcloud auth application-default login
   ```

3. **Deploy with Terraform**:
   ```bash
   cd infrastructure/environments/gcp

   # Create terraform.tfvars with your settings
   cp terraform.tfvars.example terraform.tfvars
   # Edit terraform.tfvars

   terraform init
   terraform plan
   terraform apply
   ```

4. **Build and push container images**:
   ```bash
   # Build for linux/amd64 (required for Cloud Run)
   for svc in collector processor api frontend; do
     docker buildx build --platform linux/amd64 \
       -t eu.gcr.io/YOUR_PROJECT_ID/$svc:latest \
       -f $svc/Dockerfile --push .
   done
   ```

## Stopping Services

```bash
# Stop all containers (preserves data)
docker compose down

# Stop and remove all data (fresh start)
docker compose down -v
```
