.PHONY: install install-dev test lint-backend lint-frontend build-frontend migrate migration quality

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt -r requirements-dev.txt

test:
	pytest

lint-backend:
	ruff check app tests

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
