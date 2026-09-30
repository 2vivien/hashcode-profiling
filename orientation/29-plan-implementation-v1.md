# 29 — Plan d'implémentation V1 — ordre exact, fichiers, contrats et critères de sortie

## 1. Objectif

Ce document transforme les documents 25–28 en plan d'exécution concret de la V1.

Il ne contient pas l'implémentation Python elle-même. Il définit précisément quoi créer, où le créer, dans quel ordre, quelles responsabilités donner à chaque module, quelles données sont nécessaires, quels tests doivent exister, comment valider chaque étape et quand la V1 est terminée.

La V1 doit produire un moteur déterministe, explicable, versionné, testable et exploitable, sans dépendre d'un modèle ML entraîné.

## 2. Définition exacte de la V1

Entrées :

- StudentProfile
- AssessmentResults
- StudentSkills
- DirectionCatalog
- KnowledgeSnapshot
- Configuration

Sorties :

- CandidateSet
- ScoreBreakdown
- Ranking
- DiversifiedRecommendations
- Confidence
- Uncertainty
- SkillGaps
- ExplanationFacts
- ExplorationIdeas
- AuditSnapshot

La V1 doit répondre à : parmi les directions connues par la version actuelle du catalogue et des connaissances, lesquelles sont cohérentes avec ce profil, pourquoi, avec quel niveau de confiance, quelles compétences explorer et quelles expériences permettraient de mieux tester cette hypothèse ?

Elle ne doit jamais transformer le résultat en verdict du type « ce métier est ton métier ».

## 3. Dans la V1

Obligatoire :

- Python 3.12
- FastAPI
- Pydantic v2
- NumPy
- SciPy
- pandas lorsque nécessaire pour les pipelines/data tooling
- scikit-learn lorsque nécessaire
- uv
- pytest
- Ruff
- mypy
- Docker
- CI
- contrats typés
- profil étudiant
- observations
- résultats d'assessment
- compétences
- catalogue de directions versionné
- snapshot de knowledge
- génération de candidats
- contraintes
- matching intérêts
- matching aptitudes
- matching compétences
- matching matières
- score hybride déterministe
- confiance
- incertitude
- ranking
- diversification
- skill gap
- facts d'explication
- exploration ideas
- audit
- golden profiles
- golden recommendations
- reproductibilité

Hors périmètre V1 :

- LambdaMART
- XGBoost ranking
- Two-Tower
- GNN/R-GCN
- contextual bandits
- auto-training
- reinforcement learning
- LLM ranking
- LLM decision making
- Kubernetes
- microservices multiples
- Neo4j obligatoire
- GPU obligatoire
- entraînement en production
- collaborative filtering comme signal principal
- recommandation basée uniquement sur les clics

## 4. Ordre obligatoire

00 Environment
→ 01 Contracts
→ 02 Domain primitives
→ 03 Student Profile
→ 04 Assessment baseline
→ 05 Skills
→ 06 Direction Catalog
→ 07 Knowledge Snapshot
→ 08 Candidate Generation
→ 09 Constraints
→ 10 Matching
→ 11 Hybrid Scoring
→ 12 Confidence / Uncertainty
→ 13 Ranking
→ 14 Diversification
→ 15 Skill Gap
→ 16 Explanation Facts
→ 17 Exploration
→ 18 Audit
→ 19 Recommendation Use Case
→ 20 API
→ 21 Golden tests
→ 22 Evaluation benchmark
→ 23 Docker / CI / release

Aucune couche supérieure ne doit contenir la logique d'une couche inférieure.

## 5. Étape 00 — Environnement

Fichiers :

- pyproject.toml
- uv.lock
- .python-version
- Dockerfile
- .dockerignore
- .env.example
- .gitignore
- Makefile
- README.md

Une machine propre doit pouvoir effectuer clone → install → test → lint → type-check → build sans intervention manuelle non documentée.

## 6. Étape 01 — Contrats

Créer :

src/orientation/contracts/
- profile.py
- assessment.py
- skill.py
- direction.py
- candidate.py
- scoring.py
- recommendation.py
- explanation.py
- exploration.py
- audit.py
- common.py

Les contrats sont les frontières stables du système. Ils ne contiennent pas d'algorithme.

## 7. Étape 02 — Primitives de domaine

Créer :

src/orientation/domain/
- profile/
- assessment/
- skills/
- directions/
- knowledge/
- recommendation/
- exploration/
- feedback/

Primitives :

- StudentId
- DirectionId
- SkillId
- KnowledgeVersion
- ProfileVersion
- Confidence
- Score
- Uncertainty
- Observation

Le domaine ne dépend pas de FastAPI, PostgreSQL, Redis ou des bibliothèques ML.

## 8. Étape 03 — Student Profile

Créer :

src/orientation/domain/profile/
- entities.py
- observations.py
- trajectory.py
- confidence.py
- service.py

Responsabilités :

- construire un profil
- fusionner des observations
- conserver leur provenance
- distinguer déclaré, observé, évalué et inféré
- calculer les dimensions disponibles
- calculer la complétude
- calculer la confiance par dimension

Règle critique : unknown != 0.

## 9. Étape 04 — Assessment baseline

Créer :

src/orientation/domain/assessment/
- entities.py
- scoring.py
- instruments.py
- service.py

Interface stable permettant plus tard :

- BaselineAssessment
- IRTAssessment
- MIRTAssessment
- CATAssessment

La V1 peut commencer avec des scores normalisés issus d'un instrument versionné.

Chaque résultat conserve assessmentId, instrumentVersion, responses, traits, confidence, standardError si disponible et completedAt.

## 10. Étape 05 — Skill Engine

Créer :

src/orientation/domain/skills/
- entities.py
- taxonomy.py
- matching.py
- gaps.py
- service.py

Chaque StudentSkill possède :

- skillId
- level
- confidence
- source
- status
- observedAt

Status : declared, assessed, observed, inferred.

V1 : exact matching, hiérarchie de compétences, niveau, confiance et skill gap.

## 11. Étape 06 — Direction Catalog

Créer :

data/catalog/
- directions/
- occupations/
- formations/
- skills/
- mappings/

Le catalogue ne doit pas être codé dans Python.

Chaque direction possède au minimum :

- directionId
- canonicalName
- aliases
- taxonomy
- interests
- abilities
- skills
- subjects
- values
- formations
- occupations
- requirements
- accessibility
- knowledgeVersion

Le catalogue est versionné.

## 12. Étape 07 — Knowledge Snapshot

Créer :

src/orientation/infrastructure/knowledge/
- loader.py
- validator.py
- snapshot.py
- repository.py

Sources possibles :

- ESCO
- O*NET
- catalogues de formations
- taxonomies locales
- données Otheloo

Snapshot immuable :

data/knowledge/v1/
- occupations.json
- skills.json
- formations.json
- mappings.json
- manifest.json

Le manifest conserve version, source, date, hash, nombre d'éléments et règles de transformation.

## 13. Étape 08 — Candidate Generation

Créer :

src/orientation/recommendation/candidate_generation/
- base.py
- interest_candidates.py
- skill_candidates.py
- subject_candidates.py
- graph_candidates.py
- service.py

Chaque générateur retourne des candidats et leur provenance.

Le générateur ne décide pas du classement final.

## 14. Étape 09 — Hard Constraints

Créer :

src/orientation/recommendation/constraints/
- base.py
- accessibility.py
- requirements.py
- data_quality.py
- service.py

Une contrainte retourne PASS, FAIL ou UNKNOWN.

UNKNOWN != FAIL.

Les contraintes sont auditables.

## 15. Étape 10 — Matching

Créer :

src/orientation/recommendation/matching/
- base.py
- interest.py
- ability.py
- skill.py
- subject.py
- value.py
- trajectory.py

Chaque matcher retourne :

- score
- confidence
- evidence
- missingData

Les mêmes faits servent ensuite à l'explication.

## 16. Étape 11 — Hybrid Scoring

Créer :

src/orientation/recommendation/scoring/
- weights.py
- components.py
- hybrid_score.py
- calibration.py

Score V1 :

S =
wI * InterestFit
+ wA * AbilityFit
+ wS * SkillFit
+ wV * ValueFit
+ wT * TrajectoryFit
+ wM * SubjectFit
- wG * SkillGapPenalty

Les poids sont externalisés, versionnés, validés et présents dans l'audit.

Le score est un score de compatibilité, pas une probabilité.

## 17. Étape 12 — Confidence / Uncertainty

Créer :

src/orientation/recommendation/uncertainty/
- confidence.py
- propagation.py
- completeness.py
- service.py

Prendre en compte :

- qualité des données
- quantité d'information
- provenance
- ancienneté
- cohérence
- incertitude des assessments

Un score élevé avec peu d'information peut avoir une confiance faible.

## 18. Étape 13 — Ranking

Créer :

src/orientation/recommendation/ranking/
- base.py
- deterministic.py
- service.py

Interface : RankingStrategy.

V1 : DeterministicRanking.

Plus tard : LambdaMARTRanking et NeuralRanking.

Le RecommendationEngine ne connaît pas l'algorithme concret.

## 19. Étape 14 — Diversification

Créer :

src/orientation/recommendation/diversification/
- base.py
- mmr.py
- service.py

Objectif : ne pas retourner dix directions quasiment identiques.

V1 peut utiliser une similarité structurée simple.

## 20. Étape 15 — Skill Gap

Créer ou compléter :

src/orientation/domain/skills/
- gaps.py
- readiness.py

Pour chaque direction :

- requiredSkill
- currentLevel
- requiredLevel
- gap
- confidence
- priority

Le résultat indique quoi renforcer ou explorer ; il ne constitue pas un verdict de capacité.

## 21. Étape 16 — Explanation Facts

Créer :

src/orientation/explanation/
- facts.py
- evidence.py
- templates.py
- service.py

Les faits viennent des calculs réels.

Aucun LLM n'est nécessaire en V1.

Si un LLM est ajouté plus tard, il ne pourra reformuler que les faits autorisés.

## 22. Étape 17 — Exploration Engine

Créer :

src/orientation/exploration/
- entities.py
- activities.py
- selector.py
- service.py

V1 utilise des règles.

Exemples :

- mini-projet
- activité
- contenu
- exercice
- découverte de formation
- entretien avec professionnel
- simulation

L'objectif est d'obtenir de nouvelles informations sur le profil.

## 23. Étape 18 — Audit

Créer :

src/orientation/audit/
- snapshot.py
- provenance.py
- versions.py
- service.py

Chaque recommandation conserve :

- requestId
- studentId pseudonymisé
- profileVersion
- assessmentVersion
- knowledgeVersion
- configurationVersion
- featureVersion
- modelVersion
- candidateSet
- scores
- ranking
- constraints
- explanations
- uncertainty
- timestamp

Même sans ML, modelVersion doit exister, par exemple deterministic-baseline-v1.

## 24. Étape 19 — Recommendation Use Case

Créer :

src/orientation/application/use_cases/
- generate_recommendation.py

Flux :

load profile
→ validate
→ load assessment
→ load knowledge
→ generate candidates
→ apply constraints
→ calculate matches
→ calculate hybrid score
→ calculate confidence
→ rank
→ diversify
→ calculate skill gaps
→ generate explanation facts
→ generate exploration ideas
→ build audit
→ return recommendation

Le use case orchestre les services et ne contient pas les formules.

## 25. Étape 20 — API

Créer :

src/orientation/api/
- routes/health.py
- routes/profiles.py
- routes/assessments.py
- routes/recommendations.py
- dependencies.py
- errors.py
- response.py

Endpoint principal :

POST /v1/orientation/recommendations

Secondaires :

POST /v1/orientation/profiles
POST /v1/orientation/assessments
GET /v1/orientation/profiles/{studentId}
GET /v1/orientation/knowledge/{version}
GET /health

La route fait seulement HTTP → validation → use case → response.

## 26. Étape 21 — Tests

Structure :

tests/
- unit/
- contract/
- integration/
- regression/
- property/
- golden/
- evaluation/

Unit : cosine, weighted score, confidence, skill gap, constraints, ranking, diversification, explanation facts.

Contract : schémas API et Pydantic.

Integration : profile → knowledge → recommendation.

Property-based : score borné, confidence bornée, aucune direction inconnue, déterminisme, absence de NaN et ranking stable.

## 27. Golden Profiles

Créer :

tests/golden/
- profiles/
- recommendations/
- expected/

Profils minimum :

- technique
- artistique
- social
- scientifique
- mixte
- incomplet
- contradictoire
- sans compétence déclarée
- forte incertitude

Chaque profil devient un garde-fou du moteur.

## 28. Déterminisme obligatoire

Test fondamental :

run(profile, knowledge_v1, config_v1) = run(profile, knowledge_v1, config_v1)

Les résultats doivent être identiques pour candidats, scores, ranking, explications, skill gaps et versions.

Si une opération aléatoire apparaît plus tard, randomSeed est enregistré.

## 29. Données manquantes

Distinguer :

- KNOWN
- UNKNOWN
- NOT_APPLICABLE
- CONTRADICTORY

Une absence de réponse n'est jamais automatiquement convertie en zéro.

## 30. Contradictions

Exemple :

2026-01 : intérêt déclaré faible pour les mathématiques
2026-05 : assessment quantitatif élevé
2026-06 : projet de mathématiques terminé

Ne pas écraser automatiquement les anciennes données.

Conserver source, date, contexte, confiance et type d'observation.

La contradiction peut elle-même devenir une information d'exploration.

## 31. Configuration V1

Créer :

src/orientation/config/
- settings.py
- scoring.py
- recommendation.py
- versions.py

Exemple :

configurationVersion = v1

topK = 20
finalK = 8

weights:
- interest
- ability
- skill
- value
- subject
- trajectory
- skillGap

diversification:
- enabled
- lambda

confidence:
- minimumEvidence

Aucune valeur scientifique importante ne doit être cachée dans une fonction.

## 32. Performance V1

Le moteur doit :

- filtrer les candidats tôt ;
- charger le knowledge snapshot une fois ;
- pré-calculer les structures statiques ;
- éviter les appels réseau dans la boucle de ranking ;
- vectoriser les opérations numériques lorsque pertinent.

Pas de Redis, GPU, FAISS ou Kubernetes sans benchmark démontrant leur nécessité.

## 33. Chargement

Au démarrage :

- configuration
- knowledge snapshot
- catalogues
- index statiques

À chaque requête :

student input → profile → candidate generation → scoring → ranking

Le catalogue ne doit pas être rechargé entièrement à chaque requête.

## 34. Observabilité

Chaque requête doit être reliée à :

- requestId
- profileVersion
- knowledgeVersion
- configurationVersion
- modelVersion
- duration
- status

Logs structurés uniquement.

Ne jamais logger inutilement des données personnelles, des réponses sensibles ou des secrets.

## 35. CI V1

Chaque Pull Request exécute :

- ruff format --check
- ruff check
- mypy
- pytest
- contract tests
- integration tests
- regression tests
- Docker build

Les tests golden sont obligatoires.

Un changement de ranking qui modifie les golden results doit produire une différence explicite et documentée.

## 36. Benchmark V1

Créer :

scripts/
- validate_catalog.py
- benchmark_recommendation.py
- compare_runs.py

Mesurer :

Qualité :
- Precision@K lorsque le ground truth existe
- Recall@K
- NDCG@K
- coverage
- diversity
- calibration lorsque applicable
- stabilité

Système :
- p50
- p95
- p99
- mémoire
- throughput

Otheloo :
- qualité des explications
- couverture des compétences
- qualité des skill gaps
- diversité des directions
- taux de données inconnues
- stabilité longitudinale

## 37. Critères de sortie V1

Architecture :
- séparation domain/application/infrastructure/api
- aucune logique métier importante dans les routes
- aucun catalogue métier géant hardcodé
- interfaces stables

Données :
- catalogue versionné
- knowledge snapshot versionné
- provenance conservée
- contradictions conservées

Algorithmes :
- candidate generation
- constraints
- matching
- hybrid scoring
- confidence
- uncertainty
- ranking
- diversification
- skill gap
- explanation facts
- exploration

Reproductibilité :
- code version
- profile version
- knowledge version
- configuration version
- algorithm version
- résultat reconstructible

Qualité :
- unit tests
- contract tests
- integration tests
- property tests
- golden tests
- regression tests
- benchmark

Production :
- Docker
- CI
- health endpoint
- logs structurés
- erreurs typées
- configuration externalisée

## 38. Séquence des futurs commits

feat(engine): initialize python 3.12 environment
feat(engine): add domain contracts
feat(engine): add profile domain
feat(engine): add assessment baseline
feat(engine): add skill engine
feat(engine): add direction catalog
feat(engine): add knowledge snapshot loader
feat(engine): add candidate generation
feat(engine): add hard constraints
feat(engine): add deterministic matching
feat(engine): add hybrid scoring
feat(engine): add uncertainty engine
feat(engine): add deterministic ranking
feat(engine): add diversification
feat(engine): add skill gap analysis
feat(engine): add explanation facts
feat(engine): add exploration engine
feat(engine): add recommendation audit
feat(engine): add recommendation use case
feat(engine): add FastAPI endpoints
test(engine): add golden recommendation profiles
test(engine): add property and regression tests
perf(engine): benchmark recommendation pipeline
ci(engine): add quality and reproducibility checks

Chaque commit doit rester compréhensible et réversible.

## 39. Évolution après V1

Après validation :

V1 deterministic
→ semantic retrieval
→ better skill embeddings
→ calibration
→ feature dataset
→ LambdaMART
→ shadow evaluation
→ production candidate model

Puis seulement si les benchmarks le justifient :

- graph learning
- Two-Tower
- contextual bandits
- longitudinal learning
- advanced psychometrics

## 40. Architecture finale des fichiers V1

otheloo-orientation-engine/
- pyproject.toml
- uv.lock
- .python-version
- Dockerfile
- .env.example
- Makefile
- README.md
- src/orientation/main.py
- src/orientation/api/
- src/orientation/contracts/
- src/orientation/config/
- src/orientation/domain/profile/
- src/orientation/domain/assessment/
- src/orientation/domain/skills/
- src/orientation/domain/directions/
- src/orientation/domain/knowledge/
- src/orientation/domain/recommendation/
- src/orientation/domain/exploration/
- src/orientation/domain/feedback/
- src/orientation/application/use_cases/
- src/orientation/recommendation/candidate_generation/
- src/orientation/recommendation/constraints/
- src/orientation/recommendation/matching/
- src/orientation/recommendation/scoring/
- src/orientation/recommendation/uncertainty/
- src/orientation/recommendation/ranking/
- src/orientation/recommendation/diversification/
- src/orientation/explanation/
- src/orientation/audit/
- src/orientation/infrastructure/knowledge/
- src/orientation/infrastructure/persistence/
- data/catalog/
- data/knowledge/
- data/fixtures/
- tests/unit/
- tests/contract/
- tests/integration/
- tests/regression/
- tests/property/
- tests/golden/
- tests/evaluation/
- scripts/

Cette structure est une cible d'implémentation. Les dossiers sont créés au fur et à mesure des étapes, pas artificiellement tous au premier commit.

## 41. Règle finale

La V1 doit être jugée sur une question :

« Peut-on prendre exactement le même profil, les mêmes connaissances et la même configuration et reconstruire exactement pourquoi les mêmes directions ont été produites ? »

Si oui, nous avons un socle scientifique et logiciel solide sur lequel les modèles avancés pourront être ajoutés.

Si non, il est trop tôt pour ajouter du deep learning, du bandit ou du GNN.

La V1 n'est donc pas « le modèle le plus intelligent ».

La V1 est le socle déterministe, explicable, versionné et mesurable qui permettra ensuite de prouver qu'un modèle plus intelligent apporte réellement quelque chose.
