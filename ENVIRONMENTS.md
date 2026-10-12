# Environnements — hashcode.profiling

## Modèle

| Environnement | But | Base de données | Exposé |
|---|---|---|---|
| **local** | développer | `postgres` local (compose) | `127.0.0.1` |
| **sandbox** | notebooks, algos | idem local | `127.0.0.1:8888` (profil `dev`) |
| **staging** | valider avant prod | base dédiée | sous-domaine + clé API |
| **production** | servir | base dédiée + sauvegardes | `profiler.otheloo.com` + clé API |

## Commandes

```bash
# Local (service + base)
docker compose up -d --build

# Sandbox développeur (JupyterLab)
make sandbox            # dans orientation/orientation-engine
# → http://localhost:8888

# Qualité
cd orientation/orientation-engine
make check              # ruff + format + mypy + pytest
make coverage           # couverture
make security           # bandit
make audit              # pip-audit
```

## Isolation

- Réseau `hashcodeprofiling-net` : contient **tous** les services du moteur.
  `docker network inspect hashcodeprofiling-net`
- Réseau `proxy` : **uniquement** pour le routage Traefik.
- Un environnement = un fichier `.env` (jamais partagé) + un volume dédié.

## Variables d'environnement

| Variable | Rôle | Défaut |
|---|---|---|
| `DOMAIN` | domaine public | `profiler.otheloo.com` |
| `POSTGRES_USER/PASSWORD/DB` | base | password **obligatoire** |
| `OTHELOO_API_KEY` | auth API (vide = désactivée) | vide |
| `KNOWLEDGE_VERSION` | version de connaissance déployée (pilote compose) | `v2` |
| `OTHELLOO_GEMINI_API_KEY` | traduction primaire (vide = pas de traduction) | vide |
| `OTHELLOO_GROQ_API_KEY` | traduction de repli quand Gemini sature | vide |
| `OTHELLOO_TRANSLATION_MODEL` | modèle Gemini | `gemini-2.5-flash` |
| `OTHELLOO_GROQ_TRANSLATION_MODEL` | modèle Groq | `qwen/qwen3.8-27b` |
| `DATA_PATH` | racine connaissance (dérivée dans compose) | `/app/data/knowledge/v<KNOWLEDGE_VERSION>` |
| `OTHELOO_RAG_EMBEDDER` | embeddings RAG : `auto` / `hashing` / `gemini` | `auto` (= local) |

> **Pourquoi `KNOWLEDGE_VERSION` et pas `OTHELLOO_KNOWLEDGE_VERSION` comme source ?**
> Docker Compose v5 n'interpole pas correctement une variable qui fait référence
> à elle-même dans une liste `environment:` : la valeur retombe silencieusement
> sur le défaut. La variable source porte donc un nom distinct, et
> `OTHELOO_KNOWLEDGE_VERSION` est calculée à partir d'elle.

Les clés d'API vivent uniquement dans `.env` (gitignoré, mode 600). Elles ne sont
jamais journalisées : le code les place dans un en-tête (`x-goog-api-key`,
`Authorization`) et jamais dans une URL.

## Base de données

- **Image** : `postgres:15-alpine` (PostgreSQL amont officiel), service Compose
  `postgres`, conteneur `hashcodeprofiling-db`.
- **Pourquoi pas `supabase/postgres`** : le code n'utilise **aucune** brique
  Supabase — pas de client, pas de PostgREST/GoTrue (Auth)/Storage/Realtime, et
  **aucune extension** dans les migrations (`data-service/drizzle/*.sql` : que du
  `jsonb` et des types standard). L'image Supabase était donc plus lourde, plus
  ancienne (PG 15.1) et laissait croire à une dépendance inexistante.
- **Si la recherche vectorielle en base devient nécessaire** plus tard : passer à
  `pgvector/pgvector:pg15` (Postgres standard + pgvector) plutôt que de revenir à
  l'image Supabase.
- Le volume nommé reste **`hashcodeprofiling-data`**.

### Migration depuis l'image Supabase (dump/restore)

L'ancien datadir peut référencer dans `postgresql.conf` des bibliothèques
préchargées absentes d'Alpine (`shared_preload_libraries`), ce qui empêcherait le
démarrage. On **ne réutilise donc pas** le volume : on sauvegarde, on repart d'un
volume neuf, on restaure. À exécuter sur le VPS, **avant** `docker compose up -d` :

```bash
cd /chemin/vers/hashcode-profiling

PG_USER="$(grep -E '^POSTGRES_USER=' .env | cut -d= -f2-)"
PG_PASSWORD="$(grep -E '^POSTGRES_PASSWORD=' .env | cut -d= -f2-)"

# 1. Arrêter le moteur, le data-service et la base
docker compose stop orientation-engine data-service 2>/dev/null || true
docker stop hashcodeprofiling-db 2>/dev/null || true

# 2. Sauvegarder depuis l'ancienne base (image Supabase, même volume)
mkdir -p backups
DUMP="backups/dump-$(date +%F-%H%M).sql"
docker run -d --name hcp-pgdump-tmp \
  -v hashcodeprofiling-data:/var/lib/postgresql/data \
  -e POSTGRES_USER="$PG_USER" -e POSTGRES_PASSWORD="$PG_PASSWORD" -e POSTGRES_DB=postgres \
  supabase/postgres:15.1.0.117
until docker exec hcp-pgdump-tmp pg_isready -U "$PG_USER" >/dev/null 2>&1; do sleep 2; done
docker exec hcp-pgdump-tmp pg_dumpall -U "$PG_USER" > "$DUMP"
docker rm -f hcp-pgdump-tmp
echo "Sauvegarde : $DUMP"

# 3. Repartir d'un volume neuf (datadir créé par Supabase supprimé)
docker compose down
docker volume rm hashcodeprofiling-data

# 4. Démarrer le Postgres officiel et attendre qu'il soit healthy
docker compose up -d postgres
until [ "$(docker inspect -f '{{.State.Health.Status}}' hashcodeprofiling-db)" = "healthy" ]; do sleep 2; done

# 5. Restaurer
docker exec -i hashcodeprofiling-db psql -U "$PG_USER" -d postgres < "$DUMP"
docker exec hashcodeprofiling-db psql -U "$PG_USER" -d postgres -c "ANALYZE;"

# 6. Relancer la pile complète, puis re-seed si la base était vide
docker compose up -d
./scripts/db-init.sh "${KNOWLEDGE_VERSION:-v3}"
```

> Vérifier après restauration : `docker compose exec postgres psql -U "$PG_USER"
> -d postgres -c '\dt'` doit montrer les 15 tables, et
> `curl -s https://profiler.otheloo.com/v1/orientation/system/info` doit répondre
> avec la base `reachable: true`.

## Promotion staging → production

1. `make check` vert + tests de contrat API.
2. `docker compose config` relu (pas de secret dans les labels).
3. Certificat TLS OK + en-têtes de sécurité présents.
4. Clé API transmise aux consommateurs.
5. Tag d'image identique (pas de build ad hoc en prod).
