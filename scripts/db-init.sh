#!/usr/bin/env bash
# Initialise la base du moteur : migrations Drizzle + seed de la connaissance v1.
# Usage : ./scripts/db-init.sh [version_knowledge]
set -euo pipefail
cd "$(dirname "$0")/.."

VERSION="${1:-v1}"
KNOWLEDGE_DIR="$PWD/orientation/orientation-engine/data/knowledge/$VERSION"

if [ ! -d "$KNOWLEDGE_DIR" ]; then
  echo "Connaissance introuvable : $KNOWLEDGE_DIR" >&2
  exit 1
fi

echo "[db-init] migrations…"
docker compose run --rm --no-deps data-service node dist/migrate.js

echo "[db-init] seed $VERSION…"
docker compose run --rm --no-deps \
  -v "$KNOWLEDGE_DIR:/seed/knowledge/$VERSION:ro" \
  -e KNOWLEDGE_DIR="/seed/knowledge/$VERSION" \
  data-service node dist/seed.js

echo "[db-init] terminé."
