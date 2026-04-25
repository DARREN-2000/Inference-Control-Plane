.PHONY: install install-dev test lint-frontend build-frontend

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt -r requirements-dev.txt

test:
	pytest

lint-frontend:
	cd frontend && npm run lint

build-frontend:
	cd frontend && npm run build
