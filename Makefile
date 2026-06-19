.PHONY: help install codegen lint format typecheck test check docs docs-serve build clean

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

install:  ## Sync the dev environment (uv)
	uv sync --all-extras

codegen:  ## Regenerate Pydantic models from the vendored openapi.json
	uv run python scripts/gen_models.py

fetch-spec:  ## Refresh the vendored openapi.json from production
	curl -fsSL https://tesseralytics.dev/v1/openapi.json -o openapi.json

lint:  ## Lint with ruff
	uv run ruff check .

format:  ## Format with ruff
	uv run ruff format .

typecheck:  ## Type-check with pyright
	uv run pyright

test:  ## Run the test suite
	uv run pytest

check: lint typecheck test  ## Lint + typecheck + test

docs:  ## Build the docs site
	uv run --group docs mkdocs build --strict

docs-serve:  ## Serve docs locally with live reload
	uv run --group docs mkdocs serve

build:  ## Build sdist + wheel
	uv build

clean:  ## Remove build artefacts
	rm -rf dist build site .pytest_cache .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
