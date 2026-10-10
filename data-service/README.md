# data-service — Drizzle ORM

Source de vérité de la **connaissance** (directions, compétences, occupations, formations,
mappings) et des **données du moteur** (profils, recommandations, feedback, audit, registre de
modèles) pour l'écosystème hashcode.profiling.

## Rôle dans l'architecture

```
Admin / Otheloo (Node/TS) ──Drizzle──► Postgres ◄──SQL/HTTP── Moteur (Python)
```

- **Ce service** possède le schéma (Drizzle + migrations) et le CRUD.
- Le moteur Python **lit** la base (via REST de ce service, ou SQL en direct).
- Otheloo réutilise le même schéma via Drizzle.

## Commandes

```bash
npm install
npm run db:generate   # génère les migrations SQL dans ./drizzle
npm run db:migrate    # applique les migrations
npm run db:seed       # importe data/knowledge/v1 (KNOWLEDGE_DIR)
npm run dev           # http.server sur :4100
npm run typecheck
```

## Endpoints

| Méthode | Chemin | Rôle |
|---|---|---|
| GET | `/health` | état + joignabilité base |
| GET | `/knowledge/versions` | versions de connaissance |
| GET | `/knowledge/directions?version=v1` | directions |
| GET | `/knowledge/skills?version=v1` | compétences |

## Depuis le dépôt (Docker)

```bash
# migrations
docker compose run --rm --no-deps data-service node dist/migrate.js
# seed (monte la connaissance v1)
docker compose run --rm --no-deps \
  -v "$PWD/orientation/orientation-engine/data/knowledge/v1:/seed/knowledge/v1:ro" \
  data-service node dist/seed.js
```

Voir aussi `docs/data-drizzle.md`.
