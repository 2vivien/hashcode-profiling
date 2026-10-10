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

## Promotion staging → production

1. `make check` vert + tests de contrat API.
2. `docker compose config` relu (pas de secret dans les labels).
3. Certificat TLS OK + en-têtes de sécurité présents.
4. Clé API transmise aux consommateurs.
5. Tag d'image identique (pas de build ad hoc en prod).
