.PHONY: setup dev-up mcp-up dev-down api ui worker test lint format typecheck security

setup:
	cp -n .env.example .env || true
	uv python install 3.12
	uv sync --all-groups
	uv run pre-commit install

dev-up:
	docker compose up -d postgres redis minio mcp-document mcp-image

dev-down:
	docker compose down

api:
	uv run uvicorn modelfit.api.main:app --reload --port 8000

ui:
	uv run streamlit run src/modelfit/ui/app.py --server.port 8501

worker:
	uv run celery -A modelfit.worker.celery_app:celery_app worker --loglevel=INFO

test:
	uv run pytest --cov=modelfit --cov-report=term-missing

lint:
	uv run ruff check .

format:
	uv run ruff format .

typecheck:
	uv run mypy src

security:
	uv run bandit -r src

mcp-up:
	docker compose up -d mcp-document mcp-image
