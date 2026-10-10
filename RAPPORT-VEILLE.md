# Rapport de veille — hashcode.profiling

**Date :** 2026-10-10 · **Périmètre :** moteur d'orientation (Python) + data-service (Drizzle) + site public
**État global :** service opérationnel en production-like, chaîne V1 complète et dynamique, données de démonstration uniquement.

---

## 1. Résumé exécutif

Le projet est passé d'une **spécification documentaire** à un **service réellement déployé** : moteur déterministe, base de données alimentée, boucle longitudinale fermée, site public, et outillage de développement.

Ce qui est **vrai** aujourd'hui :
- une API REST publique et versionnée qui transforme un profil en directions expliquées ;
- une base Postgres **réellement utilisée** (connaissance, profils, recommandations, feedback) ;
- une **boucle d'apprentissage** : observation → profil → recommandation → feedback → profil mis à jour ;
- une chaîne qualité verte (tests, lint, types, sécurité statique) ;
- un durcissement serveur (non-root, rootfs read-only, secrets obligatoires, en-têtes, rate-limit).

Ce qui n'est **pas** vrai (à garder en tête) : aucun modèle **entraîné**, aucun jeu de données **réel** d'élèves, ESCO/O*NET **non ingérés**, conformité RGPD **non formalisée**.

---

## 2. Architecture en production

```
Otheloo / tout consommateur  ──REST/JSON (X-API-Key)──►  https://profiler.otheloo.com
                                                            (Traefik partagé, TLS LE)
                                                                  │
                                    ┌─────────────────────────────┴──────────────────────────┐
                                    ▼                                                        ▼
        hashcodeprofiling-engine  (FastAPI, uid 10001, read-only)          hashcodeprofiling-data (Node/TS, Drizzle)
                                    │                                                        │
                                    └──────────────────► hashcodeprofiling-db (Postgres) ◄──────┘
                                          réseau hashcodeprofiling-net (interne)
```

| Service | Rôle | Exposition | Santé |
|---|---|---|---|
| `hashcodeprofiling-engine` | Moteur d'orientation (Python/FastAPI) | 127.0.0.1:8000 + Traefik | ✅ healthy |
| `hashcodeprofiling-data` | Source de vérité (Drizzle ORM) | **interne** :4100 | ✅ healthy |
| `hashcodeprofiling-db` | Postgres (Supabase self-hosted) | **aucun port publié** | ✅ healthy |
| `hashcodeprofiling-jupyter` | Sandbox notebooks (profil `dev`) | 127.0.0.1:8888 | non déployé |

---

## 3. Surface API (16 endpoints)

| Domaine | Endpoints |
|---|---|
| Santé / système | `GET /health`, `GET /v1/orientation/system/info` |
| Profil | `POST /profiles`, `GET /profiles/{id}`, `POST /profiles/{id}/evolve`, `GET /profiles/{id}/history` |
| Recommandation | `POST /recommendations`, `POST /occupation-v2/recommend` |
| Évaluation | `POST /assessments`, `/assessment-v1/{questions,adaptive,profile,telemetry}` |
| Boucle | `POST /feedback` |
| Connaissance | `GET /knowledge/{version}` |
| Site | `/`, `/moteur`, `/principes`, `/etat`, `/developers`, `/docs`, `/redoc`, `/openapi.json` |

Documentation interactive : `/docs` (Swagger) et `/redoc`.

---

## 4. Données (mesuré en base)

| Table | Lignes | Contenu |
|---|---|---|
| `knowledge_version` | 2 | v1, v2 |
| `direction` | 24 | 12 (v1) + 12 (v2 enrichies) |
| `occupation` | 24 | curation interne |
| `formation` | 20 | curation interne |
| `mapping` | 44 | direction → métier / formation |
| `skill` | 22 | 11 × 2 versions |
| `profile` | 7 | profils de démonstration |
| `recommendation` / `_item` | 5 / 49 | traces de calcul |
| `feedback` | 2 | signaux d'apprentissage |

### Provenance — point d'honnêteté
La connaissance **v2** (occupations, formations) est une **curation pédagogique interne**, pas de l'ESCO ni de l'O*NET. C'est porté dans les données (`source: "curated"`), dans le manifest et dans `data/knowledge/README.md`. Les(confiances) affichées sont **volontairement basses** (`evidence_count: 1`, `data_completeness: 0.55`) pour ne pas sur-vendre la donnée.

---

## 5. Capacités du moteur

| Capacité | État | Détail |
|---|---|---|
| Baseline déterministe | ✅ | 12 directions, scoring hybride, diversification MMR, explications, explorations |
| Lecture connaissance dynamique | ✅ | Base d'abord, repli JSON automatique (service arrêté → résultat identique) |
| **Évolution du profil** | ✅ | Fusion pondérée par la précision, confiance en bruit-OR, fiabilité par source |
| **Boucle feedback** | ✅ | Signal faible et réversible ; un clic (`view`) n'apprend rien |
| **Voies métier** | ✅ | Jusqu'à 3 métiers scorés + classés + compétences clés par direction |
| **Formations** | ✅ | Triées par accessibilité croissante |
| Persistance | ✅ | Profils, recommandations, feedback, audit (best-effort) |
| Modèles entraînés (V3–V5) | ❌ | Infra (LightGBM, R-GCN, bandits) présente, **non entraînée ni validée** |
| Psychométrie calibrée | ❌ | 2PL/GRM/MIRT/CAT codés, **banque d'items non calibrée** |

---

## 6. Site public

- Pages : accueil, moteur, principes, état, développeur (composants réutilisables : `base.html` + partials).
- Motion : aurora, scroll-reveal, View Transitions API, tilt 3D, boutons magnétiques, toasts animés, modale accessible.
- Robustesse : toasts (succès/info/attention/erreur + action « Annuler »), gestion d'erreurs API typée (422/404/429/5xx), skeletons, validation JSON live, `prefers-reduced-motion` respecté.
- Démo live : appel réel à l'API, score-ring animé, détail par direction.

---

## 7. Sécurité

| Contrôle | État |
|---|---|
| Conteneur non-root | ✅ uid 10001 |
| Rootfs read-only + tmpfs | ✅ |
| `cap_drop: ALL` + `no-new-privileges` | ✅ |
| Mot de passe DB obligatoire (démarrage refusé sinon) | ✅ |
| `.env` gitignoré, permissions 600, secrets rotatés | ✅ |
| Base jamais publiée | ✅ |
| En-têtes de sécurité + rate-limit (Traefik) | ✅ |
| Clé d'API optionnelle `X-API-Key` | ✅ (désactivée en local) |

---

## 8. Qualité et outillage

| Indicateur | Valeur |
|---|---|
| Tests | **58 passés** (20 fichiers) |
| Lint (ruff) | ✅ 0 erreur |
| Format (ruff) | ✅ 216 fichiers |
| Types (mypy strict) | ✅ 0 erreur / 180 fichiers |
| Sécurité statique (bandit) | ✅ exit 0 |
| CI GitHub Actions | ruff · format · mypy · pytest+cov · bandit · pip-audit · build |
| Sandbox développeur | `make sandbox` (JupyterLab + jupytext) |
| Outils ajoutés | hypothesis, pytest-benchmark/xdist, pandera, pre-commit, bandit, pip-audit |

---

## 9. Suivi (issues)

**2 clôturées** · **21 ouvertes**

| Priorité | Issues |
|---|---|
| Fondations | #29 bus/workers, #28 (fait) |
| Exploitation | #18 observabilité, #19 durcissement restant, #31 readiness/registry |
| Données | #21 ingestion ESCO/O*NET (partiel), #20 admin UI |
| Conformité | #22 RGPD/mineurs, #26 accessibilité, #27 pages légales |
| Qualité | #23 CI/CD + staging, #24 pagination/version API, #25 charge/sécurité/Dependabot, #30 docs |

---

## 10. Risques et angles morts

1. **Données de démonstration** — aucun élève réel ; les recommandations ne sont pas validées cliniquement.
2. **Provenance occupations** — curation interne, pas sourcée ; à remplacer par ESCO/O*NET (#21).
3. **Modèle** — baseline déterministe uniquement ; V3–V5 non entraînés (#31).
4. **RGPD** — aucune formalisation DPIA/conservation/effacement (#22).
5. **Auth API désactivée** — à activer en prod avec diffusion de la clé aux consommateurs (#19).
6. **Single point of failure** — Postgres local ; sauvegardes automatiques non encore en place (#19).
7. **Changements non commités** — ~67 fichiers modifiés/nouveaux à versionner.

---

## 11. Feuille de route immédiate

1. **Versionner** les changements (commit + PR) — le socle est vert.
2. **#18 Observabilité** : métriques, logs structurés, alertes.
3. **#19 Durcissement** : activer la clé API, CORS, quotas, sauvegardes.
4. **#21 Terminer** : ingestion ESCO/O*NET avec snapshots et mesure d'écart.
5. **#20 Admin UI** : gestion de la connaissance via Drizzle.