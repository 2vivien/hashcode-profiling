# 26 — Blueprint technique : comment coder réellement le moteur Otheloo

> Ce document est le contrat entre la recherche et le futur code. Il précise les langages, versions, fichiers, modules, contrats, modèles, données et cycle d'apprentissage nécessaires pour construire le moteur sans résultats imprévisibles.
>
> Il ne contient pas l'implémentation : il définit exactement ce que l'implémentation devra produire.

## 1. Décision technologique

### Langages
- Produit Otheloo : TypeScript / React et TypeScript / Node.js.
- Moteur : Python 3.12.

### Stack Python V1
- FastAPI
- Pydantic v2
- NumPy
- SciPy
- pandas
- scikit-learn

Ajouter seulement lorsque le besoin est démontré : sentence-transformers, LightGBM, PyTorch, PyTorch Geometric, NetworkX, FAISS/pgvector.

Python 3.12 est volontairement retenu comme base stable. La version doit être figée dans .python-version, pyproject.toml, uv.lock, Dockerfile et CI.

## 2. Environnement reproductible

Utiliser uv pour créer l'environnement, installer les dépendances et produire un lockfile.

~~~text
Python 3.12
    +
pyproject.toml
    +
uv.lock
    +
.python-version
    +
Dockerfile
    ↓
environnement reproductible
~~~

Ne jamais dépendre d'un pip install non verrouillé pour reproduire la production.

## 3. Structure exacte du futur dépôt

~~~text
othello-orientation-engine/
├── README.md
├── pyproject.toml
├── uv.lock
├── .python-version
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── .gitignore
├── src/
│   └── orientation/
│       ├── main.py
│       ├── api/
│       │   ├── routes/
│       │   ├── dependencies.py
│       │   └── errors.py
│       ├── contracts/
│       ├── domain/
│       │   ├── profile/
│       │   ├── assessment/
│       │   ├── skills/
│       │   ├── directions/
│       │   ├── knowledge/
│       │   ├── recommendation/
│       │   ├── exploration/
│       │   └── feedback/
│       ├── application/
│       │   └── use_cases/
│       ├── infrastructure/
│       │   ├── persistence/
│       │   ├── esco/
│       │   ├── onet/
│       │   ├── embeddings/
│       │   ├── graph/
│       │   ├── models/
│       │   └── configuration/
│       ├── recommendation/
│       │   ├── candidate_generation/
│       │   ├── constraints/
│       │   ├── matching/
│       │   ├── scoring/
│       │   ├── ranking/
│       │   └── diversification/
│       ├── psychometrics/
│       │   ├── riasec/
│       │   ├── irt/
│       │   ├── mirt/
│       │   └── cat/
│       ├── learning/
│       │   ├── features/
│       │   ├── training/
│       │   ├── inference/
│       │   ├── calibration/
│       │   └── evaluation/
│       ├── explanation/
│       ├── audit/
│       └── observability/
├── data/
│   ├── schemas/
│   ├── fixtures/
│   ├── catalog/
│   └── README.md
├── models/
│   └── registry/
├── scripts/
│   ├── ingest/
│   ├── validate/
│   ├── benchmark/
│   └── train/
└── tests/
    ├── unit/
    ├── contract/
    ├── integration/
    ├── regression/
    ├── property/
    └── evaluation/
~~~

Le code métier ne doit pas être mélangé avec les scripts d'import, notebooks ou données.

## 4. Architecture interne

~~~text
API
 ↓
Application / Use Cases
 ↓
Domain
 ↑
Infrastructure
~~~

API reçoit les requêtes. Application orchestre les cas d'utilisation. Domain contient les règles scientifiques et métier. Infrastructure fournit DB, graphes, modèles, fichiers et sources externes.

Le domaine ne doit pas dépendre directement de FastAPI, PostgreSQL ou d'un SDK externe.

## 5. Contrats à définir avant les algorithmes

### StudentObservation
~~~text
id, studentId, dimension, value, confidence, source, observedAt, context, version, provenance
~~~

### StudentProfile
~~~text
studentId, profileVersion, interests, abilities, skills, values, preferences, trajectory, constraints, confidence, generatedAt
~~~

### AssessmentResult
~~~text
assessmentId, sessionId, instrumentVersion, traits, theta, standardError, information, responsesCount, completedAt
~~~

### Direction
~~~text
directionId, canonicalName, aliases, taxonomy, skills, abilities, interests, subjects, formations, occupations, sectors, requirements, accessibility, knowledgeVersion
~~~

### Candidate
~~~text
directionId, generationSources, constraintStatus, profileFeatures, knowledgeEvidence
~~~

### ScoreBreakdown
~~~text
interestFit, abilityFit, skillFit, valueFit, trajectoryFit, semanticFit, graphFit, skillGapPenalty, confidence, compatibility
~~~

### Recommendation
~~~text
recommendationId, profileVersion, modelVersion, knowledgeVersion, candidates, ranking, explanations, uncertainty, skillGaps, explorations, createdAt
~~~

## 6. Modèle des compétences

Une compétence ne doit jamais être seulement une chaîne comme « Python ».

Elle doit être normalisée :

~~~text
skillId
canonicalName
aliases
taxonomy
parentSkill
domain
levelScale
source
knowledgeVersion
~~~

Le niveau de l'élève est séparé de l'identité de la compétence :

~~~text
Skill
  +
StudentSkillState

StudentSkillState
  skillId = skill.python
  level = 0.62
  confidence = 0.71
  source = assessment
  timestamp = ...
~~~

## 7. Comparaison des skills

Pipeline :

~~~text
Student Skill
 ↓
canonical skill ID
 ↓
taxonomy / hierarchy
 ↓
required skill
 ↓
level comparison
 ↓
confidence weighting
 ↓
SkillFit
~~~

Cas à distinguer : exact match, parent/child match, related skill, semantic match et unknown.

Unknown ne signifie pas zero. Une compétence non observée ne doit pas être considérée comme absente.

## 8. Modèle des directions

Le moteur ne doit pas contenir une énorme liste codée en dur dans Python.

Créer un Direction Catalog versionné. Une entrée peut représenter un domaine, secteur, famille de métiers, occupation, spécialisation, formation ou opportunité locale.

Les identifiants canoniques doivent être reliés aux taxonomies externes et aux données locales.

## 9. Couverture des métiers et directions

La couverture doit provenir d'une chaîne d'ingestion :

~~~text
ESCO
  +
O*NET
  +
catalogues de formations
  +
taxonomies locales
  +
opportunités Otheloo
       ↓
Canonical Knowledge Model
       ↓
Direction Catalog
~~~

Chaque entrée conserve canonicalId, source, sourceId, aliases, relations, version et statut de validation.

Produire automatiquement des rapports de couverture : métiers non mappés, skills non mappés, formations sans métier associé, métiers sans formation connue, doublons et relations contradictoires.

## 10. Aucun résultat au hasard

Pour une même combinaison :

~~~text
same input snapshot
+ same profile version
+ same knowledge version
+ same model version
+ same configuration
        ↓
same candidate set
same scores
same ranking
same explanation
~~~

Si un algorithme utilise du hasard : seed explicite, seed enregistrée dans l'audit, version du générateur enregistrée et environnement versionné.

La production ne doit jamais dépendre d'un random implicite.

## 11. Pipeline complet de recommandation

~~~text
Load Profile
 ↓
Validate Profile
 ↓
Load Knowledge Snapshot
 ↓
Generate Candidate Universe
 ↓
Apply Hard Constraints
 ↓
Compute Profile Features
 ↓
Compute Skill Matching
 ↓
Compute Semantic Matching
 ↓
Compute Graph Matching
 ↓
Compute Hybrid Score
 ↓
Compute Confidence
 ↓
Compute Uncertainty
 ↓
Rank
 ↓
Diversify
 ↓
Build Evidence
 ↓
Build Skill Gaps
 ↓
Select Explorations
 ↓
Persist Recommendation Audit
 ↓
Return API Response
~~~

Chaque étape doit produire un résultat typé et testable.

## 12. Score entièrement décomposable

Le système doit conserver les contributions séparées :

~~~text
finalScore =
  interestContribution
+ abilityContribution
+ skillContribution
+ valueContribution
+ trajectoryContribution
+ semanticContribution
+ graphContribution
- skillGapPenalty
~~~

Le résultat doit exposer le détail sans prétendre qu'un score est une probabilité non calibrée.

## 13. Le modèle ML n'est pas le moteur entier

Un modèle ML est un composant du pipeline :

~~~text
Profile
 ↓
Feature Builder
 ↓
Model
 ↓
Prediction
 ↓
Calibration
 ↓
Recommendation Pipeline
~~~

Le pipeline ne doit pas dépendre directement de LightGBM, PyTorch ou d'une autre librairie.

Prévoir une interface stable de modèle : fit, predict, predict_with_uncertainty, metadata.

Implémentations possibles : DeterministicBaseline, LambdaMARTModel, puis éventuellement NeuralRanker.

## 14. Model Registry

Chaque modèle doit enregistrer :

~~~text
modelId
modelType
modelVersion
trainingDatasetVersion
featureSchemaVersion
knowledgeVersion
codeCommit
pythonVersion
dependencyLockHash
hyperparameters
metrics
calibration
createdAt
status
~~~

Statuts : candidate, validated, staging, production, retired.

Un modèle ne devient pas production simplement parce qu'il s'est entraîné.

## 15. Training et inference sont séparés

### Training
~~~text
raw data
 ↓
validation
 ↓
feature generation
 ↓
train / validation / test
 ↓
training
 ↓
evaluation
 ↓
calibration
 ↓
model artifact
 ↓
registry
~~~

### Inference
~~~text
API request
 ↓
profile snapshot
 ↓
feature generation
 ↓
validated model
 ↓
prediction
 ↓
ranking
 ↓
explanation
~~~

La production ne doit pas entraîner spontanément un modèle pendant qu'un élève reçoit une recommandation.

## 16. Comment le système apprend

Le « modèle qui apprend tout seul » doit être implémenté comme un pipeline d'apprentissage continu contrôlé :

~~~text
élève
 ↓
profil
 ↓
recommandations
 ↓
exploration
 ↓
feedback
 ↓
nouvelle observation
 ↓
dataset version N+1
 ↓
réentraînement
 ↓
modèle candidat
 ↓
benchmark
 ↓
validation
 ↓
staging
 ↓
production
~~~

Le moteur ne doit pas modifier silencieusement ses paramètres à chaque clic.

## 17. Ce que le modèle peut apprendre

Progressivement :
- pertinence du matching ;
- ordre des directions ;
- pertinence des skills ;
- choix des explorations ;
- calibration de la confiance.

Il ne doit pas apprendre comme objectif direct : élève → métier définitif.

## 18. Features versionnées

Exemples :

~~~text
interest_fit
ability_fit
skill_fit
value_fit
trajectory_fit
semantic_similarity
graph_distance
graph_overlap
skill_gap
profile_confidence
evidence_count
evidence_recency
assessment_error
exploration_history
direction_coverage
~~~

Chaque feature possède un nom, type, source, transformation, version et stratégie de gestion des valeurs manquantes.

## 19. Données manquantes

Ne jamais transformer automatiquement missing en 0.

~~~text
observed zero
      ≠
unknown
~~~

Une compétence jamais évaluée doit rester unknown. Cette incertitude doit pouvoir influencer confidence et exploration, mais pas être interprétée comme une absence.

## 20. Contradictions

Conserver les observations contradictoires avec source, date, confiance et contexte.

Une agrégation peut produire une estimation, mais ne doit pas détruire les observations originales.

Une contradiction est une information utile pour l'incertitude et pour les futures explorations.

## 21. Chaîne de preuve

Chaque recommandation doit pouvoir être reliée à :

~~~text
Recommendation
 ↓
Score component
 ↓
Feature
 ↓
Observation
 ↓
Source
 ↓
Timestamp
~~~

Une recommandation sans preuve traçable doit pouvoir être rejetée ou marquée insufficient_evidence.

## 22. Explication : calcul d'abord, langage ensuite

Architecture :

~~~text
Engine
 ↓
Explanation Facts
 ↓
Explanation Template
 ↓
optional LLM rewriting
 ↓
User
~~~

Explanation Facts contient strongSignals, weakSignals, missingSignals, skillGaps, uncertainties et changeFactors.

Un LLM ne doit jamais inventer une raison absente des calculs.

## 23. Environnement de développement

Le premier commit de code doit créer :
- Python 3.12 ;
- uv ;
- pyproject.toml ;
- uv.lock ;
- Docker ;
- pytest ;
- ruff ;
- mypy ;
- CI.

CI minimale :

~~~text
format
 ↓
lint
 ↓
type-check
 ↓
unit tests
 ↓
contract tests
 ↓
integration tests
 ↓
reproducibility tests
~~~

## 24. Docker et configuration

Le conteneur fixe la version Python, les dépendances du lockfile, les variables d'environnement, un utilisateur non-root, la commande de démarrage et un healthcheck.

Les secrets et URL privées ne doivent jamais être codés en dur.

Utiliser .env.example pour documenter les variables nécessaires.

## 25. Fixtures synthétiques et Golden Profiles

Avant les vraies données élèves, créer des fixtures synthétiques déterministes.

Les Golden Profiles servent à vérifier les propriétés du moteur : génération cohérente, contraintes respectées, explications présentes et incertitude correcte.

Il ne faut pas présenter un Golden Profile comme la vérité d'un métier pour un élève.

## 26. Golden Recommendations

Conserver les sorties de référence : profileVersion, knowledgeVersion, modelVersion, candidateSet, scoreBreakdown, ranking et explanationFacts.

Chaque changement doit pouvoir produire un diff before/after et une raison documentée.

## 27. Couverture mesurable

Publier régulièrement :

~~~text
external occupations
canonical directions
mapped occupations
unmapped occupations
directions with skills
directions with formations
directions with requirements
directions with opportunities
~~~

Les chiffres d'un rapport sont des métriques de couverture et non une promesse que le moteur connaît toutes les possibilités humaines.

## 28. Catalogue hiérarchique

~~~text
Domain
 ↓
Sector
 ↓
Career Family
 ↓
Occupation
 ↓
Specialization
 ↓
Formation
 ↓
Local Opportunity
~~~

Cette hiérarchie permet de conserver une direction utile même lorsque les données fines d'une profession sont incomplètes.

## 29. Hard constraints et soft preferences

Les hard constraints sont des conditions objectives et explicitement définies. Les soft preferences contribuent au matching mais ne doivent pas supprimer silencieusement une direction.

Le code doit séparer ces deux mécanismes.

## 30. Stabilité du ranking

Tester :

~~~text
same profile + same knowledge + same model
                 ↓
             same ranking
~~~

Tester aussi la sensibilité : une petite modification d'une entrée doit produire une variation raisonnable et explicable.

## 31. No random fallback

Si aucune recommandation fiable n'est possible, ne pas choisir aléatoirement.

Retourner un état tel que insufficient_evidence avec les informations manquantes, dimensions à explorer et explorations proposées.

L'absence de résultat fiable est un résultat valide.

## 32. Pipeline d'entraînement complet

~~~text
Raw Observations
 ↓
Data Validation
 ↓
Privacy Filtering
 ↓
Dataset Versioning
 ↓
Feature Generation
 ↓
Temporal Split
 ↓
Train
 ↓
Validation
 ↓
Calibration
 ↓
Test
 ↓
Fairness Audit
 ↓
Explainability Audit
 ↓
Benchmark vs Production
 ↓
Model Registry
 ↓
Staging
 ↓
Production
~~~

Utiliser un split temporel lorsque le problème l'exige afin d'éviter les fuites entre passé et futur.

## 33. Ordre exact des premiers développements

1. Environnement : Python 3.12, uv, lockfile, Docker, tests, lint, types, CI.
2. Contracts : Profile, Observation, Skill, Direction, Candidate, Recommendation, Audit.
3. Student Profile Engine.
4. Assessment Engine baseline.
5. Direction Catalog + Knowledge Model.
6. ESCO/O*NET ingestion.
7. Candidate Generation.
8. Skill Matching.
9. Hybrid Scoring.
10. Uncertainty.
11. Ranking + Diversification.
12. Explanation Facts.
13. Recommendation Audit.
14. API FastAPI.
15. Evaluation + Golden Profiles.
16. Semantic Matching.
17. Machine Learning / Learning-to-Rank après validation des étapes précédentes.

## 34. Ce qui ne doit pas être codé au début

Ne pas commencer par réseau neuronal, GNN, contextual bandit, auto-training permanent, LLM qui décide du ranking, microservices multiples, base graphe complexe, embeddings partout ou optimisation des clics uniquement.

Le premier moteur doit être simple, explicable, testable et reproductible.

## 35. Contrat final du premier moteur

Entrées :

~~~text
Student
+ Observations
+ Assessment Results
+ Knowledge Snapshot
+ Direction Catalog
+ Configuration
~~~

Sorties :

~~~text
Candidate Set
+ Score Breakdown
+ Confidence
+ Uncertainty
+ Skill Gaps
+ Ranking
+ Diversified Directions
+ Explanation Facts
+ Exploration Ideas
+ Audit Snapshot
~~~

## 36. Définition du moteur sérieux

Le premier moteur doit être déterministe, versionné, observable, testable, explicable, auditable, extensible et capable de dire « je ne sais pas ».

Les modèles ML arrivent ensuite dans les parties où les données démontrent un gain réel.

## 37. Architecture finale

~~~text
                 OTHELOO
                    │
             REST / JSON API
                    │
                    ▼
        ┌──────────────────────┐
        │ Orientation Engine   │
        └──────────────────────┘
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
   Profile Engine       Assessment Engine
          │                   │
          └─────────┬─────────┘
                    ▼
             Feature Builder
                    │
                    ▼
          Knowledge Snapshot
                    │
                    ▼
          Candidate Universe
                    │
                    ▼
           Hard Constraints
                    │
                    ▼
          Hybrid Matching
        ┌───────────┼───────────┐
        ▼           ▼           ▼
      Skills     Semantic      Graph
        └───────────┼───────────┘
                    ▼
                 Scoring
                    │
                    ▼
              Confidence
                    │
                    ▼
              Uncertainty
                    │
                    ▼
                 Ranking
                    │
                    ▼
             Diversification
                    │
                    ▼
               Explanation
                    │
                    ▼
                Skill Gap
                    │
                    ▼
               Exploration
                    │
                    ▼
                 Feedback
                    │
                    ▼
           Dataset Version N+1
                    │
                    ▼
          Controlled Training
                    │
                    ▼
              Model Registry
                    │
                    ▼
         Evaluation / Promotion
~~~

**Règle essentielle : aucune recommandation ne doit apparaître sans pouvoir être reliée à un profil, des observations, des compétences, un univers de candidats, des connaissances, des calculs, une version du système et une chaîne d'explication.**