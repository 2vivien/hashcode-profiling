# Sécurité — hashcode.profiling

Service **indépendant** (Python/FastAPI) exposé via le Traefik partagé du VPS.
Objectif : qu'une compromission du service ne puisse pas compromettre le serveur.

## 1. Surface d'exposition

| Élément | Exposition | Règle |
|---|---|---|
| `orientation-engine` (8000) | `127.0.0.1:8000` **uniquement** + Traefik | jamais `0.0.0.0` |
| `postgres` (5432) | **aucun port publié** (réseau interne) | jamais exposé |
| `jupyter` (8888) | `127.0.0.1:8888`, profil `dev` | jamais en prod |
| `proxy` (Traefik) | 80/443 | géré par le VPS |

## 2. Durcissement des conteneurs (déjà appliqué)

- **Non-root** : `USER app` (uid 10001).
- **Rootfs read-only** (`read_only: true`) + `tmpfs` sur `/tmp`.
- **cap_drop: ALL**, **no-new-privileges**.
- **Limites** : `mem_limit: 1g`, `cpus: 1.5`.
- **Healthcheck** intégré (image + compose).
- Réseau **dédié** `hashcodeprofiling-net` ; base isolée.

## 3. Secrets

- Aucun secret par défaut : `POSTGRES_PASSWORD` est **obligatoire** (`:?` → démarrage refusé si absent).
- `.env` est **gitignoré** et en permissions **600**.
- Rotation : régénérer `POSTGRES_PASSWORD` puis `docker compose up -d --force-recreate postgres`.
- **Ne jamais** committer `.env`. Le modèle est `.env.example`.

## 4. Protection de l'API

- **En-têtes de sécurité** (middleware FastAPI + `security-headers@file` Traefik).
- **Rate-limit** Traefik (`rate-limit-api@file`) sur la route publique.
- **Clé d'API optionnelle** : définir `OTHELOO_API_KEY` (non vide) → toutes les routes
  `/v1/*` exigent l'en-tête `X-API-Key`. Vide en local/démo.
  ```bash
  curl -H "X-API-Key: $OTHELOO_API_KEY" https://profiler.otheloo.com/v1/orientation/system/info
  ```
- Comparaison en **temps constant** (`hmac.compare_digest`).

## 5. Données

- Aucune donnée d'élève réelle n'est traitée (V1 baseline, données de démonstration).
- Pseudonymisation obligatoire côté producteur (identifiant technique).
- Séparation identité Otheloo ↔ données ML.

## 6. Checklist avant mise en production

- [ ] `OTHELOO_API_KEY` définie et transmise au(x) consommateur(s).
- [ ] `POSTGRES_PASSWORD` fort et unique ; `.env` en 600.
- [ ] Ports internes non publiés (`docker compose config`).
- [ ] Certificat TLS valide (`curl -I https://profiler.otheloo.com`).
- [ ] `docker compose config` sans secret en clair dans les labels.
- [ ] Sauvegardes `hashcodeprofiling-data` et test de restauration.
- [ ] Veille dépendances : `make audit` (pip-audit) + `make security` (bandit).

## 7. Réponse à incident (base)

1. `docker compose stop orientation-engine` (isole sans couper la base).
2. Conserver les logs : `docker logs hashcodeprofiling-engine`.
3. Rotation des secrets (`POSTGRES_PASSWORD`, `OTHELOO_API_KEY`).
4. Identifier l'entrée : logs Traefik (`/var/log/traefik/access.log`).
