# Otheloo Orientation Engine — V1 to V5 implementation status

## V1 — deterministic
Implemented and validated in the existing engine:
- profile and observation contracts
- constraints and candidate generation
- weighted matching
- uncertainty and diversification
- skill gaps and explanation facts
- audit/versioning
- API, tests and CI

## V2 — semantic + knowledge
Implemented as runtime modules:
- ESCO/O*NET/local ingestion contracts
- immutable knowledge snapshots with SHA-256
- multilingual sentence-transformer encoder
- exact vector retrieval with a replaceable index abstraction
- graph relation representation
- canonical mapping review contract

Required real data before production:
- official ESCO release
- official O*NET release
- reviewed local catalogs and mappings
- descriptions/skills corpus
- semantic evaluation set

## Psychometrics
Implemented mathematically:
- 2PL probability and Fisher information
- GRM category probabilities
- CAT result contract

Not yet scientifically validated:
- item calibration
- population validation
- test-retest
- subgroup fairness
- production CAT stopping policy

## V3 — learned ranking
Implemented:
- LambdaMART production wrapper
- explicit training script
- ranking-event schema
- offline ranking metrics

Not yet trained:
- no real Otheloo ranking dataset is present in this repository
- no production labels are asserted
- no learned model artifact is checked in

## Calibration and fairness
The architecture reserves a separate score-to-probability layer and group-metric evaluation. A score becomes a probability only after fitting on independent evaluation data.

## V4 — adaptive exploration
Implemented:
- LinUCB policy
- explicit action/context separation
- propensity field in the event contract

Required before activation:
- historical exploration logs
- well-defined learning/utility outcome
- safety constraints
- offline replay evaluation
- IPS and doubly-robust evaluation
- human rollback path

## V5 — graph learning
Implemented:
- graph abstraction and path scoring
- explicit optional GNN backend contract

Not yet trained:
- the repository contains no sufficiently rich Otheloo graph
- no architecture has been selected based on a benchmark
- no GNN weights are claimed

## Non-negotiable
A module is considered "implemented" when the production code path and contract exist. A model is considered "trained/validated" only when real, versioned data and an evaluation report exist. Documentation alone never changes that status.
