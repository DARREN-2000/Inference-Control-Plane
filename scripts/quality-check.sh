#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$ROOT_DIR"

echo "[1/5] Installing backend dependencies"
pip install -r requirements.txt -r requirements-dev.txt

echo "[2/5] Running backend tests"
pytest

echo "[3/5] Installing frontend dependencies"
cd frontend
npm ci

echo "[4/5] Linting frontend"
npm run lint

echo "[5/5] Building frontend"
npm run build
