.PHONY: install install-dev dev test

install:
	@echo "Installing dependencies..."
	@uv sync --extra dev

dev:
	@echo "Starting Meridian API..."
	@uv run fastapi dev meridian/main.py

test:
	@echo "Running tests..."
	@uv run pytest --cov=meridian --cov-report=term-missing
