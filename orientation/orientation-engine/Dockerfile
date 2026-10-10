FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

WORKDIR /app

# Utilisateur non privilégié (principe du moindre privilège).
RUN groupadd --gid 10001 app \
    && useradd --uid 10001 --gid app --create-home --shell /usr/sbin/nologin app

RUN pip install --no-cache-dir uv

# Contexte de build minimal ; uv.lock garantit la reproductibilité.
COPY pyproject.toml .python-version uv.lock ./
COPY src ./src
COPY data ./data

RUN uv sync --no-dev \
    && mkdir -p /app/data/runtime \
    && chown -R app:app /app

USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=15s --retries=3 \
    CMD python -c "import sys,urllib.request; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2).status == 200 else 1)"

CMD ["/app/.venv/bin/uvicorn", "orientation.main:app", "--host", "0.0.0.0", "--port", "8000"]
