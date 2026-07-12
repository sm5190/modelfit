# Architecture

The repository is a modular monolith with separately deployable processes:

- Streamlit UI
- FastAPI API
- Celery worker
- optional MLflow server
- external or self-hosted vLLM endpoints

Shared business logic stays under `src/modelfit`. This prevents duplication while preserving a clean path to independent services later.
