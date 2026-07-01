.PHONY: install install-dev test lint-backend lint-frontend build-frontend migrate migration quality

install:
	uv sync --frozen

install-dev:
	uv sync --extra dev --frozen

test:
	uv run pytest

lint-backend:
	uv run ruff check src/inference_control_plane tests

lint-frontend:
	cd frontend && pnpm lint

build-frontend:
	cd frontend && pnpm build

migrate:
	alembic upgrade head

migration:
	alembic revision --autogenerate -m "$(m)"

quality:
	./scripts/quality-check.sh
