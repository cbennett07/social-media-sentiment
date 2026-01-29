.PHONY: help up down logs build clean test infra collect process

help:
	@echo "Available targets:"
	@echo "  make infra          - Start infrastructure only (Redis, Postgres, MinIO)"
	@echo "  make up             - Start all services"
	@echo "  make up-worker      - Start all services with continuous processor worker"
	@echo "  make down           - Stop all services"
	@echo "  make logs           - Tail logs for all services"
	@echo "  make build          - Build all containers"
	@echo "  make clean          - Remove containers and volumes"
	@echo "  make test           - Run tests"
	@echo "  make collect        - Trigger a collection (requires PHRASE)"
	@echo "  make process        - Trigger processing batch"
	@echo "  make searches       - List all searches"
	@echo "  make themes         - Get aggregated themes"
	@echo "  make sentiment      - Get sentiment timeline"

# Start infrastructure only (for local development)
infra:
	docker compose up -d redis postgres minio minio-init

# Start all services
up:
	docker compose up -d

# Start with worker profile (continuous processing)
up-worker:
	docker compose --profile worker up -d

# Stop services
down:
	docker compose down

# View logs
logs:
	docker compose logs -f

logs-collector:
	docker compose logs -f collector

logs-processor:
	docker compose logs -f processor

logs-api:
	docker compose logs -f api

# Build images
build:
	docker compose build

# Clean up everything including volumes
clean:
	docker compose down -v --remove-orphans

# Run tests
test:
	pytest tests/ -v

# Development helpers
install:
	pip install -r requirements.txt -r requirements-processor.txt -r requirements-api.txt

# Trigger collection (usage: make collect PHRASE="climate change")
collect:
ifndef PHRASE
	$(error PHRASE is required. Usage: make collect PHRASE="your search phrase")
endif
	curl -X POST http://localhost:8080/collect \
		-H "Content-Type: application/json" \
		-d '{"phrase": "$(PHRASE)"}'

# Trigger processing batch
process:
	curl -X POST http://localhost:8081/process \
		-H "Content-Type: application/json" \
		-d '{}'

# API queries
searches:
	curl -s http://localhost:8082/searches | jq .

items:
	curl -s "http://localhost:8082/items?page_size=10" | jq .

themes:
	curl -s http://localhost:8082/themes | jq .

sentiment:
	curl -s "http://localhost:8082/sentiment/timeline?granularity=day" | jq .

entities:
	curl -s http://localhost:8082/entities | jq .

sources:
	curl -s http://localhost:8082/sources | jq .

# Health checks
health:
	@echo "Collector:" && curl -s http://localhost:8080/health | jq . || echo "Not running"
	@echo "\nProcessor:" && curl -s http://localhost:8081/health | jq . || echo "Not running"
	@echo "\nAPI:" && curl -s http://localhost:8082/health | jq . || echo "Not running"

# Database shell
psql:
	docker compose exec postgres psql -U postgres -d sentiment

# Redis CLI
redis-cli:
	docker compose exec redis redis-cli

# Frontend development
frontend-dev:
	cd frontend && npm run dev

frontend-build:
	cd frontend && npm run build

logs-frontend:
	docker compose logs -f frontend

# URLs:
# Frontend: http://localhost:3000 (or http://localhost:5173 for dev mode)
# API docs: http://localhost:8082/docs
# MinIO console: http://localhost:9001 (minioadmin/minioadmin)
