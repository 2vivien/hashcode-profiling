install:
	uv sync

test:
	uv run pytest

lint:
	uv run ruff check .

format-check:
	uv run ruff format --check .

typecheck:
	uv run mypy src

check: lint format-check typecheck test

run:
	uv run uvicorn orientation.main:app --reload
