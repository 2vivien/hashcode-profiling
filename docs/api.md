# Référence de l'API

Base : `https://profiler.otheloo.com` · Préfixe : `/v1/orientation`
Documentation interactive : `/docs` · Schéma : `/openapi.json`

Tout est en JSON, sans état côté client. Les réponses sont **versionnées** : la
réponse porte toujours `model_version` et `knowledge_version`, ce qui permet de
savoir exactement avec quoi elle a été calculée.

## Authentification

Aucune par défaut. Si `OTHELOO_API_KEY` est définie côté serveur, toutes les
routes `/v1/orientation/*` exigent l'en-tête `X-API-Key`. `/health` reste
ouvert pour la sonde de disponibilité.

---

## État du service

### `GET /health`

Sonde de disponibilité. Ouverte, ne renvoie rien de sensible.

### `GET /v1/orientation/system/info`

État réel du service. **La source de vérité de l'interface** : le site lit ses
chiffres ici plutôt que d'afficher du texte figé.

```json
{
  "service": "hashcode-profiling engine",
  "code_version": "…", "model_version": "…", "knowledge_version": "v3",
  "knowledge_counts": { "directions": 12, "occupations": 1935, "formations": 20, "competences": 19462 },
  "coverage": { "countries": ["FR"], "country_names": {"FR": "France"}, "type": "national" },
  "engine_layers": [{ "layer": "ranking", "active": false, "reason": "aucun modèle LambdaMART entraîné" }],
  "rag": { "documents": 5967, "by_kind": {"occupation": 1935, "competence": 4000}, "embedder": "hashing-ngram-v1" },
  "uptime_seconds": 21.4,
  "database": { "configured": true, "reachable": true, "latency_ms": 1.6 }
}
```

| Champ | Ce qu'il dit |
|---|---|
| `knowledge_counts` | volumes réels, lus sur disque |
| `coverage` | **périmètre géographique** — ne pas supposer que c'est universel |
| `engine_layers` | état de chaque couche et la raison de son inactivité |
| `rag` | index, répartition par type, fournisseur d'embeddings |

---

## Recommandation

### `POST /v1/orientation/recommendations`

Le point d'entrée principal. Voir [moteur.md](moteur.md) pour le détail du calcul.

**Entrée** — toutes les dimensions sont facultatives, mais le moteur a besoin
d'au moins une pour comparer :

```json
{
  "student_id": "demo-1",
  "interests":  { "investigative": 0.8, "artistic": 0.3 },
  "abilities":  { "logical": 0.9 },
  "subjects":   { "mathematics": 0.8 },
  "skills":     [{ "skill_id": "programming", "level": 0.7,
                   "confidence": 0.6, "source": "declared", "status": "declared" }],
  "values":     { "autonomy": 0.6 },
  "observations": [
    { "dimension": "interests", "value": {"investigative": 0.75},
      "confidence": 0.7, "source": "observed", "state": "known" }
  ]
}
```

**Réponse** :

| Champ | Contenu |
|---|---|
| `candidates[]` | directions proposées, classées |
| `candidates[].score_breakdown` | les 9 dimensions, une par une |
| `candidates[].skill_gaps` | compétences à renforcer |
| `candidates[].occupation_paths` | métiers concrets (ROME) |
| `candidates[].formations` | formations accessibles |
| `candidates[].explanation` | les faits qui ont produit la proposition |
| `layers[]` | **état réel de chaque couche du moteur** |
| `audit` | horodatage, versions, journal |

> `layers` est la partie à ne pas ignorer : sans elle, rien ne distingue un
> score déterministe d'un score produit par un modèle.

### `POST /v1/orientation/feedback`

Signale une interaction (clic, sauvegarde, exploration). Sert à l'évolution du
profil. Un clic seul n'apprend rien : seul un signal d'intention fait évoluer.

### `POST /v1/orientation/assessments`

Enregistre une évaluation et renvoie le profil latent.

---

## Profils

| Route | Effet |
|---|---|
| `POST /v1/orientation/profiles` | crée ou remplace un profil ; écrit aussi ses **observations** en base |
| `GET /v1/orientation/profiles/{student_id}` | relit un profil |
| `GET /v1/orientation/profiles/{student_id}/history` | historique des versions |
| `POST /v1/orientation/profiles/{student_id}/evolve` | fusionne une nouvelle observation |

Les profils sont **pseudonymisés** par `student_ref` : ni un nom, ni un
identifiant scolaire.

---

## Évaluation (assessment V1)

| Route | Effet |
|---|---|
| `GET /v1/orientation/assessment-v1/questions` | questionnaire |
| `POST /v1/orientation/assessment-v1/profile` | profil latent |
| `POST /v1/orientation/assessment-v1/adaptive` | questions adaptées à la progression |
| `POST /v1/orientation/assessment-v1/telemetry` | télémétrie |
| `POST /v1/orientation/assessment-v1/ability` | **estimation psychométrique** |

### `POST /assessment-v1/ability`

```json
{
  "ability": { "method": "heuristic-mean", "calibrated": false, "information": 0.0 },
  "theta": { "investigative": 0.119, "social": 0.5 },
  "standard_error": { "investigative": null },
  "items_used": 3
}
```

`calibrated: false` et `method: "heuristic-mean"` signifient : ce n'est **pas** une
mesure de niveau, c'est une moyenne. L'API le dit plutôt que de renvoyer un
nombre qui aurait l'air.

---

## Connaissance

| Route | Effet |
|---|---|
| `GET /v1/orientation/knowledge/{version}` | manifeste d'une version |
| `GET /v1/orientation/occupation-v2/recommend` | métiers proches d'une description |
| `GET /v1/orientation/occupation-v2/discover` | découverte par mots-clés |
| `GET /v1/orientation/occupation-v2/training` | formation liée à un métier |

---

## Recherche documentaire (RAG)

### `GET /v1/orientation/context`

Assemble le contexte d'une question en langage naturel.

| Paramètre | Défaut | Bornes |
|---|---|---|
| `query` | — | 2 à 500 caractères |
| `k` | 8 | 1 à 25 |
| `budget` | 1200 | 100 à 8000 tokens |

La réponse contient trois choses : `rendered` (le contexte **injectable tel quel**
dans un prompt), `context` (la structure), et `stats`.

Chaque bloc porte sa provenance : `kind`, `doc_id`, `source`, `source_version`.
Si `dropped > 0`, des documents ont été écartés pour le budget — c'est dit.

### `GET /v1/orientation/rag/stats`

Documents indexés, répartition par type, fournisseur d'embeddings, dimensions.

---

## Atlas

### `GET /v1/orientation/atlas`

Périmètre géographique, volumes, et répartitions réelles : métiers par grand
domaine, compétences par domaine, écriture inclusive, langues.

### `GET /v1/orientation/atlas/map.svg`

Carte du monde en SVG, contours réels (Natural Earth). Accepte `?profession=`
pour filtrer sur un métier.

Renvoie **503** si les contours n'ont pas été téléchargés
(`python3 scripts/fetch_world_map.py`).

---

## Erreurs

| Code | Signification |
|---|---|
| 422 | validation : champ manquant ou valeur hors bornes (détail champ par champ) |
| 404 | ressource inconnue (profil, version de connaissance) |
| 503 | dépendance indisponible : RAG non indexé, contours non téléchargés, service de données injoignable |

Les endpoints de persistance (`profiles`, `feedback`, `recommendations`) sont
**best-effort** : un incident de base n'entraîne pas d'erreur HTTP, il est
journalisé et la réponse est servie quand même.

---

## Limites connues

- **Aucune pagination.** `knowledge/occupations` renvoie 1 935 lignes en une
  réponse (suivi en #24).
- **Pas de politique de version d'API** écrite. Une version majeure casserait les
  clients sans prévenir.
- **Pas de tests de contrat** sur les endpoints récents (suivi en #40).