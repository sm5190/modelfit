FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV PYTHONUNBUFFERED=1

COPY pyproject.toml README.md ./
COPY src ./src
COPY configs ./configs
RUN uv sync --no-dev --group documents --group evaluation --group mlops

ENV PATH="/app/.venv/bin:$PATH"

CMD ["celery", "-A", "modelfit.worker.celery_app:celery_app", "worker", "--loglevel=INFO"]
