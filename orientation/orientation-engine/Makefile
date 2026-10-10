COMPOSE := docker compose -f ../../docker-compose.yml

install:
	uv sync

test:
	uv run pytest

test-fast:
	uv run pytest -q -x

coverage:
	uv run --with coverage pytest --cov=orientation --cov-report=term-missing

lint:
	uv run ruff check .

format:
	uv run ruff format .

format-check:
	uv run ruff format --check .

typecheck:
	uv run mypy src

check: lint format-check typecheck test

run:
	uv run uvicorn orientation.main:app --reload

# --- Sandbox développeur (notebooks) ---
sandbox:
	$(COMPOSE) --profile dev up -d --build jupyter
	@echo "JupyterLab → http://localhost:8888"

sandbox-down:
	$(COMPOSE) --profile dev down

notebooks-check:
	uv run --with nbqa --with ruff nbqa ruff notebooks/

# --- Sécurité / conformité ---
security:
	uv run --with bandit bandit -r src

audit:
	uv run --with pip-audit pip-audit
