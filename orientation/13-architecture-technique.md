# Architecture technique

## Services

    Orientation API
        ↓
    Profile Service
        ↓
    Assessment Service
        ↓
    Recommendation Engine
        ├── Rules
        ├── Scoring
        ├── Semantic
        ├── Graph
        ├── Ranking
        └── Diversification
        ↓
    Explanation Service
        ↓
    Exploration Service
        ↓
    Learning Service

## Recherche ML

Outils possibles :

- NumPy ;
- SciPy ;
- pandas ;
- scikit-learn ;
- PyTorch ;
- PyTorch Geometric ;
- NetworkX ;
- moteur vectoriel.

Le choix dépendra des données et des performances mesurées.

## TypeScript

Conserver côté produit :

- contrats ;
- API ;
- validation ;
- orchestration ;
- droits ;
- intégration Otheloo.

Le calcul ML lourd peut être isolé si nécessaire.

## Vector search

Progression :

    SQL/simple matching
        ↓
    pgvector ou FAISS
        ↓
    moteur spécialisé si nécessaire

## Graph

Prototype :

    NetworkX

Production possible selon besoin :

- PostgreSQL ;
- extension graphe ;
- Neo4j ;
- autre moteur spécialisé.

Le choix doit suivre les requêtes réelles.

## Modèle

Chaque modèle conserve :

    id
    version
    trainingDataVersion
    features
    hyperparameters
    metrics
    status
    createdAt

## Reproductibilité

    inputSnapshot
    + modelVersion
    + knowledgeVersion
    + configuration

doit permettre de reproduire un résultat.

## Tests

### Unit

Formules et transformations.

### Contract

Schémas d'API.

### Integration

Pipeline complet.

### Property-based

Propriétés mathématiques.

### Regression

Profils de référence.

### Fairness

Jeux synthétiques puis données autorisées.

## Observabilité

Mesurer :

- latence ;
- erreurs ;
- drift ;
- distribution des scores ;
- couverture ;
- diversité ;
- changements de version.

## Sécurité

- validation ;
- permissions ;
- isolation des données ;
- audit ;
- secrets hors code ;
- minimisation.
