#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$ROOT_DIR"

echo "[1/6] Installing backend dependencies"
python -m pip install --user uv
uv sync --extra dev --frozen

echo "[2/6] Linting backend"
uv run ruff check src/inference_control_plane tests

echo "[3/6] Running backend tests"
uv run pytest

echo "[4/6] Installing frontend dependencies"
cd frontend
npm ci

echo "[5/6] Linting frontend"
npm run lint

echo "[6/6] Building frontend"
npm run build
