# Otheloo Orientation Engine

Moteur V1 déterministe d'orientation et de recommandation.

## Runtime

- Python 3.12
- FastAPI
- Pydantic v2
- NumPy / SciPy
- uv
- pytest / Ruff / mypy

## Run

```bash
uv sync
uv run uvicorn orientation.main:app --reload
```

API : `/docs`

## Tests

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy src
```

La V1 est déterministe : même profil + même knowledge snapshot + même configuration = même résultat.

<!-- final V1 CI checkpoint -->
