.PHONY: install install-dev test lint-backend lint-frontend build-frontend migrate migration quality

install:
	uv sync --system --frozen

install-dev:
	uv sync --extra dev --system --frozen

test:
	pytest

lint-backend:
	ruff check src/inference_control_plane tests

lint-frontend:
	cd frontend && npm run lint

build-frontend:
	cd frontend && npm run build

migrate:
	alembic upgrade head

migration:
	alembic revision --autogenerate -m "$(m)"

quality:
	./scripts/quality-check.sh
