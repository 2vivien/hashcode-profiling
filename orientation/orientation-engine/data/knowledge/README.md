# Connaissance — provenance et versions

## v1 — catalogue curaté initial

- 12 directions, 11 compétences.
- Source : curation interne Otheloo.
- Occupations / formations / mappings : **vides**.

## v2 — occupations + formations (curation interne)

Généré par `scripts/build_knowledge_v2.py` (reproductible, déterministe).

- 12 directions enrichies (`occupations`, `formations` renseignés).
- 24 occupations, 20 formations, 44 mappings direction→métier/formation.
- **Provenance honnête** : `source: "curated"` — ce n'est **ni ESCO ni O*NET**.
  `evidence_count` volontairement bas (1) et `data_completeness` à 0.55, donc la
  confiance affichée est faible : c'est voulu.
- Les identifiants sont des slugs stables (`software-dev`, `licence-info`…).

## Ce qu'il reste (issue #21)

- Ingestion des exports **réels** ESCO v1.2.1 / O*NET 31.0 dans une version ultérieure,
  avec snapshots hashés, provenance et contrôles qualité.
- Remplacer la curation dérivée par des données sourcées, puis mesurer l'écart.

## Règles

- Toute nouvelle version passe par un script versionné (pas d'édition manuelle).
- `manifest.json` porte le `sha256` de `directions.json` (vérifié au chargement).
- Une version donnée reste **immuable** : on crée v3, on ne réécrit pas v2.
- Les dimensions sont normalisées dans [0,1] ; une donnée absente reste une incertitude.

## Usage

```bash
python3 scripts/build_knowledge_v2.py          # régénère v2
./scripts/db-init.sh v2                        # migrations + seed base
```

Le moteur lit la base (data-service) et **replie** sur ces fichiers JSON si la base est indisponible.