#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$ROOT_DIR"

echo "[1/6] Installing backend dependencies"
pip install -r requirements.txt -r requirements-dev.txt

echo "[2/6] Linting backend"
ruff check app tests

echo "[3/6] Running backend tests"
pytest

echo "[4/6] Installing frontend dependencies"
cd frontend
npm ci

echo "[5/6] Linting frontend"
npm run lint

echo "[6/6] Building frontend"
npm run build
