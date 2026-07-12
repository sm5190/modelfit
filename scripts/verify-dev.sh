#!/usr/bin/env bash
set -euo pipefail

git --version
gh --version
uv --version
docker --version
docker compose version
python3 --version || true

uv run ruff check .
uv run pytest

echo "Verification complete."
