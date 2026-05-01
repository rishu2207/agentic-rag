.PHONY: help start stop restart status logs health setup format lint test test-cov clean \
        backend frontend frontend-install frontend-build frontend-dev

# Default target
help: ## Show this help message
	@echo "Agentic RAG Platform — available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

# ---------- Service management ----------
start: ## Start the full stack (backend + frontend + infra)
	docker compose up --build -d

stop: ## Stop all services
	docker compose down

restart: ## Restart all services
	docker compose restart

status: ## Show service status
	docker compose ps

logs: ## Tail service logs
	docker compose logs -f

# ---------- Health checks ----------
health: ## Probe each service
	@echo "Checking service health..."
	@curl -s http://localhost:8000/api/v1/health | jq . || echo "API not responding"
	@curl -s http://localhost:9200/_cluster/health | jq . || echo "OpenSearch not responding"
	@curl -s http://localhost:11434/api/version | jq . || echo "Ollama not responding"
	@curl -s http://localhost:3000/api/health || echo "Frontend not responding"

# ---------- Backend dev ----------
setup: ## Install Python dependencies with uv
	uv sync

backend: ## Run the FastAPI backend locally (requires infra via compose)
	uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

format: ## Format Python code
	uv run ruff format

lint: ## Lint and type check Python code
	uv run ruff check --fix
	uv run mypy backend/

test: ## Run backend tests
	uv run pytest

test-cov: ## Run backend tests with coverage
	uv run pytest --cov=backend --cov-report=html

# ---------- Frontend dev ----------
frontend-install: ## Install frontend dependencies
	cd frontend && npm install

frontend-dev: ## Run the Next.js frontend in dev mode
	cd frontend && npm run dev

frontend-build: ## Build the Next.js frontend for production
	cd frontend && npm run build

# ---------- Cleanup ----------
clean: ## Nuke containers, volumes, and build caches
	docker compose down -v
	docker system prune -f
