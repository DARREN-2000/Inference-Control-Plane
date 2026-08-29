#!/bin/sh
set -e

echo "Running database migrations..."
alembic upgrade head

echo "Starting application..."
exec uvicorn inference_control_plane.main:app --app-dir src --host 0.0.0.0 --port 8000
