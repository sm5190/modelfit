FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app
RUN uv pip install --system "mlflow>=3.0"
