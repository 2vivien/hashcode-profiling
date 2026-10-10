# Environnements — hashcode.profiling

## Modèle

| Environnement | But | Base de données | Exposé |
|---|---|---|---|
| **local** | développer | `supabase-db` local (compose) | `127.0.0.1` |
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
| `DATA_PATH` | racine connaissance | `/app/data/knowledge/v1` |

## Promotion staging → production

1. `make check` vert + tests de contrat API.
2. `docker compose config` relu (pas de secret dans les labels).
3. Certificat TLS OK + en-têtes de sécurité présents.
4. Clé API transmise aux consommateurs.
5. Tag d'image identique (pas de build ad hoc en prod).
