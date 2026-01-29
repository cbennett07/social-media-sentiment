# Claude.md - Development Notes

## Project Overview

Social media sentiment analysis platform that collects articles from RSS feeds, NewsAPI, Reddit, and Twitter, processes them through an LLM for sentiment analysis, and displays results in a dashboard.

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

## Architecture Notes

- **Collector** pushes raw articles to Redis queue
- **Processor** pulls from queue, calls LLM API, stores results in PostgreSQL and MinIO
- **API** serves processed data to frontend
- **Frontend** displays sentiment charts, themes, entities, and article list
