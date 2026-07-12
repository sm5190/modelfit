FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV PYTHONUNBUFFERED=1

COPY pyproject.toml README.md ./
COPY src ./src
RUN uv sync --no-dev

ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8501

CMD ["streamlit", "run", "src/modelfit/ui/app.py", "--server.address=0.0.0.0", "--server.port=8501"]
