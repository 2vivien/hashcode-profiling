# Données & base — vers un moteur dynamique (et où intervient Drizzle)

## État actuel

- La connaissance est en **JSON** : `orientation/orientation-engine/data/knowledge/v1/*.json`
  (`directions`, `occupations`, `skills`, `formations`, `mappings`, `manifest`).
- Le moteur charge ces fichiers via `KnowledgeLoader` (lecture seule).
- **Postgres (image officielle `postgres:15-alpine`) tourne déjà** mais n'est **pas encore utilisé** par le moteur.

## Objectif

Rendre le moteur **dynamique** : gérer la connaissance, les profils, les recommandations,
le feedback et l'audit en base, avec **versionnage**, sans redéployer à chaque changement.

## Point important : Python ≠ Drizzle

**Drizzle ORM est TypeScript uniquement.** Il ne peut pas piloter directement notre moteur
**Python/FastAPI**. Deux chemins cohérents :

### Option A (recommandée) — Postgres = source de vérité, Drizzle côté Node

```
Admin / Otheloo (Node/TS) ──Drizzle──► Postgres ◄──SQLAlchemy/asyncpg── Engine (Python)
```

- **Drizzle** vit dans un service Node/TS (le backend Otheloo ou un `data-service` dédié) :
  schéma, migrations, CRUD admin.
- Le moteur Python **lit** Postgres via **SQLAlchemy 2.0 + Alembic** (ou `asyncpg`).
- Un seul schéma, deux clients ; pas de duplication.

### Option B — Python propriétaire du schéma

- **SQLAlchemy + Alembic** définissent et migrent le schéma ; Drizzle n'intervient pas côté moteur.

> **Question ouverte** : où veux-tu que Drizzle vive ? (voir décision en bas)

## Schéma proposé (Postgres)

| Table | Contenu |
|---|---|
| `knowledge_version` | versions (v1, v2…), hash, date, statut |
| `direction` | directions (id, nom, taxonomie, **connu dans une version**) |
| `skill` / `occupation` / `formation` | référentiels |
| `direction_skill` / `direction_occupation` / `mapping` | relations typées |
| `profile` | profil versionné (dimensions en JSONB) |
| `observation` | signaux datés/sourcés (value, confidence, source) |
| `recommendation` + `recommendation_item` | sorties versionnées + audit |
| `feedback` | retours élève (signal, pas vérité) |
| `audit_event` | journal d'audit |
| `model_registry` | modèle, features, métriques, statut |

Le moteur cible une **version de connaissance** ; changer de version = une ligne, pas un déploiement.

## Migration JSON → base

1. Schéma + migrations.
2. **Seed** : importer `data/knowledge/v1/*.json` (script idempotent, `knowledge_version=v1`).
3. Le moteur lit d'abord la base, avec **cache** et repli sur les JSON (transition sans coupure).
4. Une fois validé : les JSON deviennent des **fixtures de test**, pas la source.

## Garde-fous

- Toute écriture en base passe par des **migrations** (jamais à la main).
- Le schéma est **versionné** avec le code.
- Les données sensibles restent **pseudonymisées**.
- Rien de personnel dans les tables de connaissance.

## Décision à prendre

1. **Option A** : un `data-service` Node/TS avec **Drizzle** (migrations + CRUD), le moteur Python lit la base.
2. **Option B** : le moteur Python possède le schéma (**SQLAlchemy/Alembic**), pas de Drizzle.
3. **Hybride** : Drizzle pour les tables produit/Otheloo, SQLAlchemy pour la connaissance.

## ✅ Décision retenue : Option A — implémentée

- `data-service/` (Node/TS + **Drizzle ORM**) : schéma, migrations, seed, API REST.
- Schéma : 13 tables (connaissance + profils + recommandations + feedback + audit + registre modèles).
- Migrations générées : `data-service/drizzle/`.
- Seed JSON → base : `orientation-engine/data/knowledge/v1` → `knowledge_version`/`direction`/`skill`.
- Conteneur durci : `hashcodeprofiling-data` (réseau interne, non exposé, read-only).
- Initialisation : `./scripts/db-init.sh v1`.

## ✅ Moteur branché (lecture base)

- `RemoteKnowledge` (urllib + cache TTL) lit `GET /knowledge/directions` du data-service.
- `OTHELOO_DATA_SERVICE_URL` active la lecture distante ; **repli JSON** automatique si indisponible.
- Vérifié : 12 directions via le data-service ; service arrêté → repli JSON, résultat identique.

**Reste à faire** : admin UI.

## ✅ Boucle d'écriture + évolution longitudinale

**data-service (écriture)** : `POST /profiles`, `POST /recommendations`, `POST /feedback`,
`GET /profiles/{studentRef}` (validation zod, upsert Drizzle).

**moteur (lecture/écriture)** :
- `POST /v1/orientation/profiles` → profil mémorisé (cache mémoire + base)
- `POST /v1/orientation/recommendations` → recommandation + profil persistés (best-effort)
- `POST /v1/orientation/feedback` → feedback persisté **et** profil évolué
- `POST /v1/orientation/profiles/{id}/evolve` → application d'observations
- `GET /v1/orientation/profiles/{id}/history` → versions du profil

**Règles appliquées** :
- fusion des observations **pondérée par la précision** (confiance × fiabilité de la source) ;
- état `unknown` / `contradictory` ignoré (l'absence reste de l'incertitude) ;
- feedback = **signal faible** (pas ±1,0 mais un petit pas réversible) ;
- un simple `view` (clic) **n'apprend rien** ;
- les écritures sont **best-effort** : une base indisponible ne casse jamais une réponse.

