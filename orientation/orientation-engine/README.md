# Otheloo Orientation Engine

Moteur d'orientation modulaire V1→V5.

## Runtime

- Python 3.12
- FastAPI / Pydantic v2
- NumPy / SciPy / pandas / scikit-learn
- uv
- pytest / Ruff / mypy

Les dépendances lourdes V2+ sont séparées dans requirements-v2-ml.txt.

## Niveaux implémentés

### V1
- profil multidimensionnel
- contraintes
- candidate generation
- matching pondéré
- score confidence-weighted
- uncertainty
- ranking déterministe
- diversification MMR
- skill gaps
- explications
- audit/versioning

### V2
- ingestion ESCO/O*NET/local
- snapshots hashés
- embeddings Sentence Transformers
- recherche vectorielle
- graphe de connaissances
- mappings canoniques revus

### Psychométrie
- 2PL
- GRM
- MIRT
- CAT adaptatif par information

Le code psychométrique n'est pas présenté comme scientifiquement validé sans banque d'items calibrée et données de validation.

### V3
- LambdaMART
- dataset de ranking
- split temporel groupé
- Precision@K / Recall@K / MAP / NDCG

Aucun modèle Otheloo entraîné n'est livré sans dataset réel.

### Calibration / fairness
- sigmoid / isotonic calibration
- Brier / log loss
- demographic parity gap
- equal opportunity gap

### V4
- LinUCB
- exploration epsilon-greedy avec propensités enregistrées
- replay
- IPS
- doubly robust

### V5
- graphe relationnel
- R-GCN entraînable
- façade GNN stable

Aucun poids GNN n'est considéré validé sans graphe Otheloo réel et benchmark contre V3.

## Données externes

Le registre data/catalog/external_sources.json conserve les versions des référentiels attendus.

ESCO fournit actuellement la version v1.2.1. O*NET fournit actuellement la release 31.0. Les fichiers téléchargés doivent être conservés comme artefacts externes versionnés avec leur SHA-256 et leur provenance.

## Ingestion

    uv run python scripts/ingest_external_catalog.py --source esco --input /path/to/esco.csv --output data/catalog/esco/snapshot.json --version esco-1.2.1

    uv run python scripts/ingest_external_catalog.py --source onet --input /path/to/onet.tsv --delimiter TAB --output data/catalog/onet/snapshot.json --version onet-31.0

Les exports Otheloo locaux utilisent le même pipeline avec --source local.

## Entraînement LambdaMART

    uv run python scripts/train_lambdamart.py --input /path/to/ranking.jsonl --output models/registry/lambdamart.joblib --report reports/lambdamart.json

Le dataset doit contenir des événements réels, des features versionnées, des labels définis et des timestamps.

## Tests

    uv sync
    uv run pytest
    uv run ruff check .
    uv run ruff format --check .
    uv run mypy src

## Règle de vérité

Un composant possède quatre états indépendants :

1. code implémenté ;
2. données réelles disponibles ;
3. modèle entraîné ;
4. validation scientifique réalisée.

Le dépôt ne confond jamais ces états.
