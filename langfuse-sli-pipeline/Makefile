.DEFAULT_GOAL := help
.PHONY: help install install-dev test test-offline lint format typecheck all clean run demo demo-runaway docker-build compose-up compose-down

PYTHON ?= python3
PYTHONPATH := src
export PYTHONPATH

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-16s\033[0m %s\n", $$1, $$2}'

install: ## Install the package (runtime only; stdlib, no deps)
	$(PYTHON) -m pip install -e .

install-dev: ## Install with dev extras (pytest, ruff, mypy)
	$(PYTHON) -m pip install -e '.[dev]'

test: ## Run the test suite with pytest
	pytest -q

test-offline: ## Run the same tests with the zero-dependency runner (air-gapped)
	$(PYTHON) run_tests.py

lint: ## Lint with ruff
	ruff check .

format: ## Auto-format with ruff
	ruff format .

typecheck: ## Type-check with mypy
	mypy src

all: lint typecheck test ## Lint + type-check + test

demo: ## Run the console exporter on the sample fixture
	$(PYTHON) -m gateway_sli.cli --source data/sample_traces.json --emit console \
		--window-end 2026-01-15T11:46:00Z

demo-runaway: ## Run the synthetic DevAgent runaway example
	$(PYTHON) -m gateway_sli.cli --source data/demo_runaway_traces.json --emit console \
		--window-end 2026-01-15T11:46:00Z

run: ## Alias for demo
	@$(MAKE) demo

docker-build: ## Build the container image
	docker build -t gateway-sli:local .

compose-up: ## Start app + local OTel collector
	docker compose up --build

compose-down: ## Stop the local stack
	docker compose down -v

clean: ## Remove caches and build artifacts
	rm -rf .pytest_cache .mypy_cache .ruff_cache build dist *.egg-info
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
