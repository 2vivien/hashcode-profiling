# Guide administrateur

## 1. Architecture en une minute

```
Otheloo (Node/TS) ──REST/JSON──► profiler.otheloo.com (Traefik)
                                      │
                                      ▼
                          hashcodeprofiling-engine (FastAPI)
                                      │ réseau hashcodeprofiling-net
                                      ▼
                          hashcodeprofiling-db (Postgres)
```

Le moteur est **indépendant**. Aucun code n'est partagé avec Otheloo : tout passe par l'API.

## 2. Déployer / mettre à jour

```bash
cd /home/audest/hashcode-profiling
docker compose up -d --build orientation-engine
docker compose ps
```

Vérifications :
```bash
curl -s https://profiler.otheloo.com/health
curl -s https://profiler.otheloo.com/v1/orientation/system/info
```

## 3. Exploiter

| Action | Commande |
|---|---|
| Logs moteur | `docker logs -f hashcodeprofiling-engine` |
| Logs base | `docker logs -f hashcodeprofiling-db` |
| État santé | `docker compose ps` (colonne healthy) |
| Réseau du moteur | `docker network inspect hashcodeprofiling-net` |
| Redémarrer | `docker compose restart orientation-engine` |

## 4. Surveiller

- **Healthcheck** conteneur (30 s) → `docker inspect hashcodeprofiling-engine`.
- **/health** : statut + version.
- **/v1/orientation/system/info** : versions (code, modèle, connaissance), uptime, joignabilité DB.
- Logs Traefik : `/var/log/traefik/access.log` (json).

## 5. Sauvegardes

```bash
# Dump base
docker exec hashcodeprofiling-db pg_dump -U postgres postgres > backup_$(date +%F).sql
# Restauration
cat backup_YYYY-MM-DD.sql | docker exec -i hashcodeprofiling-db psql -U postgres postgres
```

## 6. Sécurité

Voir [SECURITY.md](../SECURITY.md). Points clés :
- `.env` en **600**, jamais commité.
- `OTHELOO_API_KEY` définie en production.
- Ports internes jamais publiés.
- Rotation des secrets après tout doute.

## 7. Incidents

| Symptôme | Piste |
|---|---|
| `502` au démarrage | conteneur pas encore prêt (~10 s) ; vérifier `docker compose ps` |
| `401` sur `/v1/*` | `X-API-Key` manquante/invalide |
| `422` | corps JSON incomplet (voir message détaillé) |
| DB injoignable | `system/info` → `database.reachable: false` ; vérifier `hashcodeprofiling-db` |
