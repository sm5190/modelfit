# ModelFit

ModelFit is a business-friendly LLM evaluation sandbox. It lets users run the same realistic task across multiple models, inspect the original responses, and compare communication quality, task quality, operational behavior, and supporting evidence.

## Architecture baseline

- UI: Streamlit
- API: FastAPI
- Workflow: LangGraph
- Tool protocol: governed MCP client and internal MCP servers
- Jobs: Celery
- Broker/cache: Redis
- Database: PostgreSQL + pgvector
- Object storage: MinIO
- Experiment tracking: MLflow
- Model serving: vLLM
- Local deployment: Docker Compose
- Production deployment: Kubernetes + Helm

## Prerequisites

- WSL 2 with Ubuntu
- VS Code with the WSL extension
- Git and GitHub CLI
- Docker Engine or Docker Desktop with WSL integration
- uv

## First-time setup

```bash
cp .env.example .env
uv python install 3.12
uv sync --all-groups
uv run pre-commit install
docker compose up -d postgres redis minio mcp-document mcp-image
```

Run the services in separate terminals:

```bash
uv run uvicorn modelfit.api.main:app --reload --port 8000
uv run celery -A modelfit.worker.celery_app:celery_app worker --loglevel=INFO
uv run streamlit run src/modelfit/ui/app.py --server.port 8501
```

Open:

- UI: http://localhost:8501
- API docs: http://localhost:8000/docs
- MinIO console: http://localhost:9001

## Docker-based startup

```bash
cp .env.example .env
docker compose up --build
```

## Quality commands

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest
uv run bandit -r src
```

## Repository principles

- Keep deployable services thin.
- Put business logic under `src/modelfit`.
- Add models through `configs/models.yaml`, not UI conditionals.
- Version prompts and rubrics as files.
- PostgreSQL is durable truth; Redis is temporary coordination.
- MinIO stores large artifacts; PostgreSQL stores metadata and object references.
- Candidate-model failures stay visible in comparisons.
- Every score must carry evidence, confidence, and evaluator provenance.

## MCP development

Start the read-only document and image MCP servers:

```bash
docker compose up -d mcp-document mcp-image
```

Enable the web-search server only after an approved provider is configured:

```bash
docker compose --profile web-tools up -d mcp-web
```

Production rules:

- do not accept arbitrary MCP URLs from users
- filter discovered tools through the policy gateway
- require approval for sensitive or external actions
- record arguments, results, latency, server version, and permission decisions
