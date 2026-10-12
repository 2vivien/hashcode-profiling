# Déploiement et exploitation

Comment faire tourner la pile, la mettre à jour, et savoir si ça va.

## Ce qu'il faut avant de commencer

| Outil | Pourquoi |
|---|---|
| Docker + Compose | toute la pile |
| `make` (ou les commandes ci-dessous) | raccourcis |
| un nom de domaine | le TLS est géré par Traefik |

Secrets dans `.env`, **jamais commités**, mode `600`.

## Démarrer

```bash
cp .env.example .env      # puis compléter les secrets
chmod 600 .env

docker compose up -d      # base + data-service + moteur
./scripts/db-init.sh v3   # migrations + connaissance
```

Ouverture : <https://profiler.otheloo.com>

## Déployer une mise à jour

```bash
./scripts/deploy.sh            # build + up + migrations + vérifications
./scripts/deploy.sh --pull     # idem, après un git pull --ff-only
./scripts/deploy.sh --seed v3  # en plus, (re)charge la connaissance v3
```

Le script est **idempotent** : sans changement de code, rien n'est recréé ; les
migrations déjà appliquées sont ignorées (suivi dans `drizzle.__drizzle_migrations`).
Il échoue proprement si la base, le data-service ou le moteur ne deviennent pas
`healthy`, ou si `system/info` indique `database.reachable=false`.

## Les commandes utiles

```bash
# État
docker compose ps
curl -s https://profiler.otheloo.com/v1/orientation/system/info | jq

# Redémarrer un seul service
docker compose restart orientation-engine

# Reconstruire après une modification de code
docker compose up -d --build orientation-engine

# Recharger la connaissance (après un nouveau build_knowledge_vN.py)
./scripts/db-init.sh v3

# Journaux
docker logs -f hashcodeprofiling-engine --tail 100

# Qualité (à lancer AVANT tout déploiement)
docker run --rm --user root \
  -e RUFF_CACHE_DIR=/tmp/ruff \
  -v "$PWD/orientation/orientation-engine:/app" -w /app \
  hashcodeprofiling-orientation-engine:latest \
  sh -c "uv run ruff check . && uv run mypy src && uv run pytest -q"
```

> Le `--user root` n'est pas un oubli : le conteneur de production tourne en
> non-root et ne peut pas écrire le cache ruff.

## Mettre à jour la connaissance

1. Télécharger les sources :
   ```bash
   cd orientation/orientation-engine
   uv run python scripts/fetch_external.py
   uv run python scripts/fetch_world_map.py
   ```
2. Reconstruire la version :
   ```bash
   uv run python scripts/build_knowledge_v3.py
   ```
3. Charger en base :
   ```bash
   ./scripts/db-init.sh v3
   ```
4. Redémarrer, puis **vérifier** :
   ```bash
   curl -s https://profiler.otheloo.com/v1/orientation/system/info | jq .knowledge_counts
   ```

## Changer la version de connaissance

Modifier `KNOWLEDGE_VERSION` dans `.env`, puis :

```bash
docker compose up -d --force-recreate orientation-engine
./scripts/db-init.sh <nouvelle-version>
```

> Docker Compose v5 n'interpole pas une variable qui se référence à elle-même
> dans une liste `environment:` : la valeur retombe silencieusement sur le
> défaut. C'est pourquoi la variable source s'appelle `KNOWLEDGE_VERSION` et
> non `OTHELLOO_KNOWLEDGE_VERSION`. **Toujours vérifier après avoir changé.**

## Surveiller

| Signal | Où | Anormal si |
|---|---|---|
| Le service répond | `GET /health` | non-200 |
| Le moteur est à jour | `system/info.knowledge_version` | ≠ la version attendue |
| Les couches actives | `system/info.engine_layers` | passe à 0 — régression silencieuse |
| Le RAG est indexé | `system/info.rag.indexed` | `false` |
| Le périmètre | `system/info.coverage.countries` | moins que prévu |
| La base répond | `system/info.database.reachable` | `false` |

Un **`system/info` qui renvoie 500** empêche l'interface d'afficher l'état — c'est
le premier endroit à regarder si la page `/etat` est vide.

## Performance mesurée

| Action | Temps |
|---|---|
| Index RAG à froid (après redémarrage) | 1,5 s |
| Requête RAG suivante | 67 ms |
| 1re requête `/context` après redémarrage | 2,5 s |
| `POST /recommendations` | 0,27 s |
| Reconstruction d'une version de connaissance | 1 min |

## En cas de panne

| Symptôme | Cause probable | Action |
|---|---|---|
| Le site ne répond pas | moteur arrêté | `docker compose ps`, `docker logs` |
| `/health` OK mais les reco échouent | data-service injoignable | vérifier le repli JSON |
| `/etat` vide | `/system/info` en erreur | `docker logs --tail 50` |
| Carte absente | contours non téléchargés | `scripts/fetch_world_map.py` |
| Connaissances incohérentes | version pas rechargée | `./scripts/db-init.sh <version>` |
| Layers à 0 | modèle retiré du registre | vérifier `data/runtime/models/` |

## Sauvegardes

> **Aucune sauvegarde automatique n'est en place.** C'est le risque le plus élevé
> du projet, suivi en #39. En attendant, à faire à la main :
>
> ```bash
> docker exec hashcodeprofiling-db pg_dump -U postgres postgres | gzip > sauvegarde-$(date +%F).sql.gz
> ```
>
> Et **tester la restauration**, pas seulement la sauvegarde.

## Secrets

Ne jamais commiter un secret. Le PAT GitHub exposé a été révoqué et un autre
credential a été trouvé dans `~/.git-credentials` (suivi en #48) : c'est
exactement le genre de sortie à éviter.

En cas de fuite :

1. Révoquer immédiatement.
2. Vérifier les journaux du fournisseur.
3. Régénérer.
4. Ne pas se contenter de supprimer le fichier du dépôt : l'historique le garde.