#!/bin/sh
set -e

echo "Running database migrations..."
alembic upgrade head || echo "WARNING: Migrations failed. Continuing anyway..."

echo "Starting application..."
PORT=${PORT:-8000}
exec uvicorn inference_control_plane.main:app --app-dir src --host 0.0.0.0 --port $PORT
