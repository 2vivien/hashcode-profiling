# Architecture

Vue d'ensemble : ce qui existe, comment les pièces s'articulent, et pourquoi
c'est ainsi. Pour le détail d'un morceau, le document est indiqué.

## Les trois services

```
Internet
   │  HTTPS (TLS, Traefik)
   ▼
┌─────────────────────────────────────────────┐
│  orientation-engine  (Python, FastAPI)      │
│  profil → directions, RAG, explication      │
└──────────────┬──────────────────────────────┘
               │ REST interne
               ▼
┌─────────────────────────────────────────────┐
│  data-service  (Node, TypeScript, Fastify)  │
│  écriture, lecture, seed, migrations        │
└──────────────┬──────────────────────────────┘
               │ SQL
               ▼
┌─────────────────────────────────────────────┐
│  postgres  (PostgreSQL)                     │
│  15 tables                                    │
└─────────────────────────────────────────────┘
```

## Où est la vérité

| Donnée | Source de vérité | Repli |
|---|---|---|
| Connaissance (métiers, compétences, directions) | **la base**, versionnée | fichiers JSON sur disque |
| Profils, recommandations, observations, audit | la base | mémoire du processus |
| Secrets | `.env` (mode 600, gitignoré) | — |
| Modèles entraînés | `data/runtime/models/` | la couche est inactive |

> Le repli JSON existe pour que le moteur survive à une panne du data-service.
> Il a aussi un effet secondaire utiles : il permet de vérifier que les deux
> chemins donnent le même résultat.

## Comment la connaissance arrive dans le moteur

```
data/catalog/external_sources.json   ← catalogue des sources déclarées
        │
        ├─ fetch_external.py          télécharge, SHA-256, manifeste
        ├─ fetch_world_map.py         contours Natural Earth
        │
        ▼
data/raw/<source>/                    archives (hors dépôt) + manifestes (dans le dépôt)
        │
        ├─ build_knowledge_v3.py      ROME → connaissance v3
        ▼
data/knowledge/v3/                   manifest.json + données
        │
        ├─ db-init.sh v3             migrations + seed
        ▼
PostgreSQL ────────────────────────► data-service ──► moteur
```

Une version de connaissance est **atomique** : on ne mélange jamais du v2 et du v3.

## À l'intérieur du moteur

| Couche | Rôle | Où |
|---|---|---|
| **API** | routes, sécurité, rendu | `api/` |
| **Application** | le cas d'usage de recommandation | `application/use_cases/` |
| **Domaine** | profil, compétences, scores | `domain/` |
| **Infrastructure** | base, connaissance, traduction, géographie, persistance | `infrastructure/` |
| **RAG** | documents, recherche, contexte | `rag/` |
| **Pile** | couches de scoring et leur état | `engine/` |
| **Occupation knowledge** | modèles métier, ingestion | `occupation_knowledge/` |

## Le chemin d'une requête

```
POST /recommendations
  │
  ├─ validation du profil (pydantic)
  ├─ chargement de la connaissance      base ──▶ repli JSON
  ├─ validation du manifeste            SHA-256
  ├─ génération des candidats           4 générateurs
  ├─ filtres                            accessibilité, exigences, qualité
  ├─ comparaison                        9 dimensions × confiance
  ├─ écarts de compétences              feuille de route
  ├─ score                              HybridScorer
  ├─ pile                               calibration, ranking, graphe, bandit, équité
  ├─ classement + diversification       MMR
  ├─ explication, métiers, formations, explorations
  ├─ écriture en base                   profil, reco, observations, audit
  └─ réponse + état des couches
```

## Les décisions structurantes

### Dépendances minimales

Le contrat de dépendances du moteur est volontairement court. Deux exemples de
conséquences :

- **BM25 et RRF sont écrits à la main** (~150 lignes) plutôt qu'importés ;
- **Le RAG indexe en local** par défaut, parce que l'offre gratuite de Gemini
  se fait throttler dès quelques centaines de documents.

Ce n'est pas de la purté de principe : chaque dépendance est un point de panne et
un risque de sécurité au moment de l'installation.

### Pas de dépendance JavaScript pour la carte

La carte du monde est tracée en Python et servie en SVG. Pas de bibliothèque
côté navigateur : rendu net à toute taille, et le fichier reste diffable — ce
qu'une carte dessinée en JS ne permet pas (on ne voit pas ce qui a changé d'un
commit à l'autre).

### Écriture best-effort

Un incident de base n'entraîne pas d'erreur HTTP. Le résultat est servi, l'échec
est journalisé. Choix assumé : pour un outil d'orientation, mieux vaut une
recommandation sans sauvegarde qu'une page d'erreur.

### Le RAG ne.score pas

La récupération documentaire **n'entre pas dans le calcul de compatibilité**. Le
baseline est calibré sur les occupations curées de v2 ; y brancher du retrieval
changerait les scores sans revalidation. Le RAG sert à répondre en langage
naturel et à sourcer les explications.

### Le moteur dit ce qu'il ne fait pas

C'est le fil conducteur de l'architecture. `layers` dans chaque réponse,
`coverage` dans l'état du système, `/etat` alimenté par l'API plutôt que par du
texte figé. Un composant qui n'est pas prêt doit le dire.

## Le front

| Fichier | Rôle |
|---|---|
| `templates/` | pages, Jinja simple avec `{{include:…}}` |
| `static/js/app.js` | socle : API, helpers, révélations au scroll, démo |
| `static/js/dev.js` | page développeur, bandeau d'état |
| `static/js/atlas.js` | carte et répartitions |
| `static/js/motion.js` | primitives d'animation (compteurs, cascade) |

Scripts classiques chargés dans l'ordre, donc les helpers globaux de `app.js`
sont disponibles dans les autres. Tout respecte `prefers-reduced-motion` — sans
quoi les graphiques devenaient invisibles pour les personnes qui le demandent.

## Ce qui n'est pas en place

Honnêteté architecturale :

- **Pas d'injection de dépendances** au sens propre : `GenerateRecommendation` est
  instancié globalement (suivi en #13).
- **Pas de bus d'événements** ni de workers séparés (suivis en #14 et #15).
- **Pas de pagination** sur les grandes collections (suivi en #24).
- **78 modules hors chemin de production** (suivi en #44).