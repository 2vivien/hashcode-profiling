# Sources de données externes — état vérifié

Vérifié le **2026-10-10** par tests HTTP réels depuis le serveur de production.
Les commandes reproductibles sont en annexe, en fin de document.

## Verdict sur `cporter202/API-mega-list`

Dépôt réel (7 723 ⭐, créé 2025-12-09, mis à jour 2026-07-23) mais **inexploitable pour ce projet** :

- c'est un catalogue de **liens vers des APIs commerciales de scraping / lead-gen** (Apify Actors en très grande majorité) ;
- aucun jeu de données métier (ESCO, O*NET, ROME, RNCP) n'y est référencé ;
- pas de licence, pas de garantie de fraîcheur, aucune donnée exploitable telle quelle ;
- sur les 1 163 entrées du dossier `jobs-apis`, les seules occurrences de « skill » sont du bruit de marketplace.

**Conclusion : ne pas l'utiliser comme source.** Utile éventuellement comme catalogue d'outils d'enrichissement, pas comme source de vérité.

---

## Sources retenues

| Source | Version | Licence | Auth | Format | État vérifié | Ce qu'elle apporte |
|---|---|---|---|---|---|---|
| **O*NET** | 31.0 | CC BY 4.0 (US DOL) | aucune | zip (Excel, CSV, JSON-LD) | ✅ `HTTP 206` — téléchargement confirmé | ~1 000 occupations, skills, tâches, RIASEC, cognition |
| **ESCO** | 1.2.1 (10/12/2025) | CC BY 4.0 (CE) | aucune | CSV / ODS / RDF / JSON-LD | ✅ page de téléchargement `200` |_taxonomie paneuropéenne **multilingue dont français**, relations métier ↔ compétence |
| **ESCO ↔ O*NET crosswalk** | v6.0.0 | CC BY 4.0 (CE) | aucune | table de correspondance | ✅ page `200` | **le pont officiel** entre les deux taxonomies (exact / narrow / broad / close) |
| **ROME** (France Travail) | juin 2026 | Ouvert (France Travail) | aucune | xlsx | ✅ **925 Ko téléchargé, xlsx valide, 47 entrées** | nomenclature française : métiers, compétences, savoirs, contextes de travail |
| **Wikidata SPARQL** | continu | CC0 | aucune | SPARQL → JSON | ✅ requête testée | désambiguïsation, liens entre métiers/domaines, traductions manquantes |
| **data.gouv.fr API** | continu | Ouvert | aucune | JSON | ✅ recherche ROME validée | datasets publics français, automatisation d'ingestion |

## Sources écartées (et pourquoi)

| Source | Raison de l'écart |
|---|---|
| ONISEP (`www.onisep.fr`, `api.onisep.fr`) | `HTTP 403` / DNS en échec **depuis le serveur**. Pas accessible en production. À réévaluer si un proxy est mis en place. |
| Eurostat API | `HTTP 404` sur les jeux testés depuis ce serveur (API de diffusion). Non critique : ESCO couvre le besoin. |
| ILO SDMX (ISCO-08) | `HTTP 400` sur les endpoints testés ; ISCO-08 reste utile comme **taxonomie** (cf. `taxonomy.py`) mais pas comme source d'ingestion automatique. |
| HuggingFace datasets | recherche `esco`, `onet`, `occupation skills` → **aucun jeu exploitable** (matching par homonymie). À ne pas utiliser. |
| `cporter202/API-mega-list` | voir verdict ci-dessus. |

---

## Ce qui bloque encore l'ingestion

Le socle d'ingestion est **déjà présent et testé** :

- `occupation_knowledge/ingest.py` — lecteur CSV ESCO
- `occupation_knowledge/onet.py` — lecteur CSV O*NET (normalisation des notes 1–7 → 0–1, RIASEC)
- `occupation_knowledge/onet_package.py` — lecteur **zip O*NET** (le format réel publié)
- `infrastructure/knowledge/external_sources.py` — lecteurs `esco_reader` / `onet_reader`
- `scripts/ingest_external_catalog.py` — construit un snapshot versionné **avec SHA-256**
- `external_sources.json` — porte déjà la politique (`store_sha256`, `store_release_metadata`)

Il manque **uniquement** :

1. **Le fetcher** — un script qui télécharge les archives dans `data/raw/`, calcule le SHA-256 et journalise la provenance (`version`, `release_date`, `source_url`). Le script actuel attend des fichiers déjà présents sur disque (`--input`).
2. **Un lecteur ROME xlsx** — `openpyxl` requis ; l'existant ne lit que du CSV.
3. **Le crosswalk ESCO ↔ O*NET** — aucun lecteur pour ce format.

## État de l'ingestion (2026-10-10)

| Étape | État |
|---|---|
| Fetcher (`scripts/fetch_external.py`) | ✅ O*NET 31.0 (91,8 Mo) et ROME (8 fichiers) téléchargés, SHA-256 et provenance journalisés |
| v3 (fiches métiers ROME) | ✅ **1 911 métiers réels** + 24 curés, en base |
| v3 (compétences ROME) | ✅ 19 479 compétences dans `competences.json` |
| Traduction | ✅ chaîne Gemini → Groq branchée (voir `docs/translation.md`) |
| O*NET → base | ⏳ archive téléchargée, pas encore ingérée (attend le crosswalk) |
| ESCO | ⏳ page de téléchargement à suivre manuellement (liens rendus en JS) |
| Genre par métier | ❌ aucune source de répartition en open data |

**Appariement vers les directions : volontairement minimal.** Sur 1 911 fiches,
seules **58** sont rattachées à une direction, et toutes ont été relues à la
main : les 1 853 autres restent dans le catalogue sans être appariées. Une
première version plus permissive en appariait 185 — dont « Analyste de la
performance sportive » classé en *cybersécurité*, via le mot « sécurité ». Le
matching actuel refuse les mots polysémiques (`sécurité`, `service`, `social`…).

## Ordre d'ingestion recommandé

1. **O*NET 31.0** — le meilleur rapport valeur/effort : archive unique, sans clé, ~1 000 occupations, remplace immédiatement la curation de 24 occupations.
2. **ROME (juin 2026)** — indispensable en français : `rome-arborescence-des-competences-juin-2026.xlsx` (feuilles `Définition`, `Macro-compétences`, `Compétences`). Attention : c'est un **xlsx multi-feuilles**, pas un CSV → il faut un lecteur `openpyxl`, le code actuel ne lit que du CSV.
3. **ESCO 1.2.1** — taxonomie de référence paneuropéenne, mais volumineuse : à charger à froid puis à **n'exposer que le nécessaire** (les 3 CSV utiles, pas les 47).
4. **Crosswalk ESCO ↔ O*NET** — à charger en dernier : il n'a de sens qu'une fois les deux taxonomies en base, et il remplace tout travail de mapping manuel.

## Point de vigilance

L'ingestion d'O*NET / ROME / ESCO rend le catalogue **non-curé**. C'est une amélioration (données réelles, traçables) mais cela change la nature du produit :

- le scoring actuel a été calibré sur 24 occupations curées → **il faut revalider** les poids sur le nouveau référentiel ;
- O*NET est en anglais : les libellés français viendront de ROME/ESCO, pas d'O*NET ;
- chaque ligne doit porter sa provenance (source, version, licence) pour rester auditable.

## Annexe — commandes de vérification

```bash
# O*NET 31.0 (sans clé)
curl -sI -r 0-1000 https://www.onetcenter.org/dl_files/database/db_31_0_excel.zip

# ESCO
curl -so /dev/null -w '%{http_code}' https://esco.ec.europa.eu/en/use-esco/download
curl -so /dev/null -w '%{http_code}' https://esco.ec.europa.eu/en/use-esco/other-crosswalks

# ROME — compétences (juin 2026)
curl -sL -o /tmp/rome.xlsx \
  "https://www.francetravail.org/files/live/sites/peorg/files/documents/Statistiques-et-analyses/Open-data/ROME/rome-arborescence-des-competences-juin-2026.xlsx"

# Wikidata SPARQL
curl -sG https://query.wikidata.org/sparql \
  -H "Accept: application/sparql-results+json" \
  --data-urlencode 'query=SELECT ?occ WHERE { ?occ wdt:P31/wdt:P279* wd:Q28640 } LIMIT 1'

# data.gouv.fr
curl -s "https://www.data.gouv.fr/api/1/datasets/?q=ROME"
```