#!/usr/bin/env bash
set -euo pipefail

if [[ ! -f .env ]]; then
  cp .env.example .env
fi

uv python install 3.12
uv sync --group dev
uv run pre-commit install
uv lock

echo "ModelFit development environment is ready."
echo "Next: docker compose up -d postgres redis minio"
