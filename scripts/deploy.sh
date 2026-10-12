#!/usr/bin/env bash
# Déploiement de la pile hashcode.profiling (base + data-service + moteur).
#
# Usage :
#   ./scripts/deploy.sh              # build + up + migrations + vérifications
#   ./scripts/deploy.sh --pull       # git pull --ff-only avant de déployer
#   ./scripts/deploy.sh --seed v3    # migrations + (re)seed de la connaissance
#   ./scripts/deploy.sh --no-build   # réutilise les images existantes
#
# Idempotent : sans changement de code, `up` ne recrée rien ; les migrations
# déjà appliquées sont ignorées (suivi dans drizzle.__drizzle_migrations).
set -euo pipefail

cd "$(dirname "$0")/.."

# ---------- options ----------
DO_PULL=0
DO_BUILD=1
SEED_VERSION=""
while [ $# -gt 0 ]; do
  case "$1" in
    --pull) DO_PULL=1 ;;
    --no-build) DO_BUILD=0 ;;
    --seed) SEED_VERSION="${2:-}"; shift ;;
    -h|--help) sed -n '2,12p' "$0"; exit 0 ;;
    *) echo "Option inconnue : $1" >&2; exit 2 ;;
  esac
  shift
done

step() { printf '\n\033[1m==> %s\033[0m\n' "$1"; }
fail() { printf '\n\033[31mÉCHEC : %s\033[0m\n' "$1" >&2; exit 1; }

wait_healthy() { # nom_conteneur, secondes_max
  local name="$1" max="${2:-120}" i=0 status
  while [ "$i" -lt "$max" ]; do
    status="$(docker inspect -f '{{.State.Health.Status}}' "$name" 2>/dev/null || echo missing)"
    [ "$status" = "healthy" ] && return 0
    [ "$status" = "missing" ] && { echo "  conteneur $name absent"; return 1; }
    sleep 2; i=$((i + 2))
  done
  echo "  $name toujours '$status' après ${max}s"; return 1
}

# ---------- pré-requis ----------
step "Pré-requis"
[ -f .env ] || fail ".env manquant (cf. ENVIRONMENTS.md / .env.example)"
docker compose config >/dev/null || fail "docker compose config invalide"
echo "  .env présent, compose valide"

if [ "$DO_PULL" -eq 1 ]; then
  step "git pull --ff-only"
  git pull --ff-only || fail "git pull (dépôt non propre ou non fast-forward)"
fi

# ---------- build ----------
if [ "$DO_BUILD" -eq 1 ]; then
  step "Build des images"
  docker compose build || fail "build"
fi

# ---------- démarrage ----------
step "Démarrage de la base et attente healthy"
docker compose up -d postgres || fail "up postgres"
wait_healthy hashcodeprofiling-db 120 || fail "base non healthy"

step "Migrations Drizzle"
docker compose run --rm --no-deps data-service node dist/migrate.js || fail "migrations"

if [ -n "$SEED_VERSION" ]; then
  step "Seed de la connaissance $SEED_VERSION"
  KNOWLEDGE_DIR="$PWD/orientation/orientation-engine/data/knowledge/$SEED_VERSION"
  [ -d "$KNOWLEDGE_DIR" ] || fail "connaissance introuvable : $KNOWLEDGE_DIR"
  docker compose run --rm --no-deps \
    -v "$KNOWLEDGE_DIR:/seed/knowledge/$SEED_VERSION:ro" \
    -e KNOWLEDGE_DIR="/seed/knowledge/$SEED_VERSION" \
    data-service node dist/seed.js || fail "seed"
fi

step "Démarrage de la pile complète"
docker compose up -d || fail "up"

step "Attente des services"
wait_healthy hashcodeprofiling-data 120 || fail "data-service non healthy"
wait_healthy hashcodeprofiling-engine 180 || fail "moteur non healthy"

# ---------- vérifications ----------
step "Vérifications"
curl -fsS -m 10 http://127.0.0.1:8000/health >/dev/null || fail "GET /health (local)"
echo "  moteur /health : OK"

INFO="$(curl -fsS -m 20 http://127.0.0.1:8000/v1/orientation/system/info)" \
  || fail "GET system/info"
DB="$(printf '%s' "$INFO" | python3 -c 'import sys,json;print(json.load(sys.stdin)["database"]["reachable"])' 2>/dev/null || echo "?")"
[ "$DB" = "True" ] || fail "base non joignable depuis le moteur (database.reachable=$DB)"
echo "  base joignable depuis le moteur : OK"

PUBLIC="$(curl -s -o /dev/null -w '%{http_code}' -m 20 https://profiler.otheloo.com/health || echo 000)"
[ "$PUBLIC" = "200" ] && echo "  public https://profiler.otheloo.com/health : ${PUBLIC}" \
  || echo "  [avertissement] public /health = ${PUBLIC} (DNS/TLS/proxy ?)"

step "Déploiement terminé"
docker compose ps --format 'table {{.Name}}\t{{.Image}}\t{{.Status}}'
