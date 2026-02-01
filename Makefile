.PHONY: install dev lint typecheck test

install:
	@echo "Installing dependencies..."
	@uv sync --extra dev

dev:
	@echo "Starting Meridian API..."
	@uv run fastapi dev api/main.py

lint:
	@echo "Running ruff..."
	@uv run ruff check . && uv run ruff format --check .

typecheck:
	@echo "Running mypy..."
	@uv run mypy meridian api

test:
	@echo "Running tests..."
	@uv run pytest --cov=meridian --cov-report=term-missing
