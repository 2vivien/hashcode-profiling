# 27 — Règles d'architecture du code, Clean Code, taille des fichiers et scalabilité

> Ce document définit les règles obligatoires du futur code Python du moteur Otheloo : découpage des fichiers, responsabilités, dépendances, qualité, tests, performance et évolution vers la charge.

## 1. Principe directeur

Le moteur doit être construit comme un système scientifique et industriel, pas comme un prototype Python contenant toute la logique dans quelques fichiers.

Objectifs : lisibilité, modularité, testabilité, faible couplage, forte cohésion, reproductibilité, scalabilité horizontale, observabilité et remplacement facile des algorithmes.

Règle fondamentale :

~~~text
1 fichier = 1 responsabilité principale
1 module = 1 domaine cohérent
1 fonction = 1 opération claire
1 classe = 1 responsabilité principale
1 use case = 1 scénario métier
~~~

## 2. Architecture des dépendances

~~~text
API
 ↓
Application / Use Cases
 ↓
Domain
 ↑
Infrastructure
~~~

API : HTTP, validation, sérialisation, erreurs et appel des use cases. Elle ne calcule pas directement les scores.

Application : orchestration des scénarios métier.

Domain : profil, assessment, psychométrie, skills, matching, scoring, ranking, incertitude, skill gap, exploration et règles scientifiques.

Infrastructure : PostgreSQL, Redis, stockage objet, ESCO, O*NET, vector store, graph store, model registry et observabilité.

Le Domain ne doit jamais dépendre de FastAPI, PostgreSQL, Redis, Neo4j, PyTorch ou d'un SDK externe.

## 3. Règle de taille des fichiers

| Élément | Cible |
|---|---:|
| Fonction | 5–40 lignes |
| Fonction complexe | < 60 lignes |
| Classe | idéalement < 200 lignes |
| Fichier Python | idéalement 100–300 lignes |
| Fichier complexe | seuil de revue à 400 lignes |
| Route FastAPI | idéalement < 30 lignes |
| Use case | idéalement < 150 lignes |
| Test unitaire | généralement < 100 lignes |

Ces nombres sont des seuils d'architecture, pas des lois mécaniques. Un dépassement doit être justifié par la cohésion du module.

Un fichier qui dépasse régulièrement 400–500 lignes doit déclencher une revue et probablement un découpage.

Interdit : un `recommendation.py` de 1 500 lignes contenant profil, embeddings, graphe, ranking, explications et base de données.

## 4. Découpage par responsabilité

Exemple :

~~~text
recommendation/
├── candidate_generator.py
├── constraints.py
├── profile_matching.py
├── skill_matching.py
├── semantic_matching.py
├── graph_matching.py
├── scoring.py
├── ranking.py
├── diversification.py
└── service.py
~~~

`service.py` orchestre. Les autres composants calculent une responsabilité précise.

Ne pas découper uniquement selon le nombre de lignes : découper selon les responsabilités.

## 5. Une fonction = une intention

Éviter une fonction qui charge la DB, construit le profil, calcule les embeddings, parcourt le graphe, score, trie, explique et sauvegarde.

Préférer :

~~~text
generate_recommendations()
 ↓
load_profile()
 ↓
generate_candidates()
 ↓
apply_constraints()
 ↓
compute_scores()
 ↓
rank_candidates()
 ↓
build_explanations()
 ↓
persist_audit()
~~~

Chaque étape doit être testable indépendamment.

## 6. Aucun God Object

Interdire une classe `OrientationEngine` qui contient toute la DB, le profil, l'IRT, les embeddings, le graph, le ML, le ranking et l'audit.

Un orchestrateur peut exister, mais il ne possède pas toutes les responsabilités.

## 7. Interfaces avant implémentations

Les composants susceptibles de changer doivent avoir une abstraction stable.

~~~text
SkillMatcher
├── ExactSkillMatcher
├── HierarchicalSkillMatcher
└── SemanticSkillMatcher

RankingStrategy
├── DeterministicRanker
├── LambdaMARTRanker
└── NeuralRanker (plus tard si justifié)
~~~

Le moteur dépend du contrat, pas de la bibliothèque utilisée pour l'implémentation.

## 8. Typage strict

Règles :
- annotations partout ;
- éviter `Any` ;
- aucun `# type: ignore` sans justification ;
- Pydantic pour les contrats externes ;
- objets de domaine typés ;
- enums pour les états fermés ;
- type-check obligatoire en CI.

## 9. Nommage et commentaires

Utiliser des noms de domaine explicites : `profile_confidence`, `knowledge_version`, `skill_gap`, `candidate_set`, `score_breakdown`.

Éviter `x`, `tmp`, `res`, `data2`, `final2`.

Les commentaires expliquent pourquoi une règle existe, pas ce que fait une ligne évidente. Les règles scientifiques importantes doivent pointer vers la documentation scientifique correspondante.

## 10. Routes très minces

Une route FastAPI doit rester un adaptateur HTTP :

~~~text
POST /recommendations
 ↓
GenerateRecommendationUseCase
 ↓
RecommendationService
~~~

Jamais de gros calcul scientifique directement dans une route.

## 11. Configuration centralisée

Les poids, seuils, tailles de candidats et versions ne doivent pas être dispersés sous forme de magic numbers.

~~~text
configuration/
├── scoring.py
├── assessment.py
├── ranking.py
├── exploration.py
└── settings.py
~~~

Chaque configuration scientifique doit avoir une version enregistrée dans l'audit.

## 12. Séparer code, données et configuration

~~~text
Code       → règles / algorithmes / orchestration
Data       → catalogues / taxonomies / datasets / fixtures
Config     → poids / seuils / paramètres / versions
~~~

Ne jamais mettre des milliers de métiers directement dans un fichier Python.

## 13. Production vs expérimentation

~~~text
src/          → production
scripts/      → ingestion / training / benchmark
tests/        → validation
experiments/  → recherche reproductible
~~~

Un notebook ne doit jamais être nécessaire au fonctionnement de l'API.

## 14. Séparer training et inference

~~~text
TRAINING
data → validation → features → train → evaluate → calibrate → registry

INFERENCE
request → profile snapshot → features → validated model → prediction → ranking
~~~

Le serveur de production ne doit jamais entraîner spontanément un modèle pendant une recommandation.

## 15. Chargement des modèles

Un modèle validé est chargé au démarrage ou via un mécanisme contrôlé de reload.

~~~text
startup
 ↓
load validated model
 ↓
keep in memory
 ↓
serve requests
~~~

Ne jamais recharger le fichier du modèle à chaque requête.

Un nouveau modèle suit : registry → validation → staging → warm-up → activation.

## 16. Scalabilité horizontale

Le moteur API doit être stateless autant que possible.

~~~text
Load Balancer
   ├── Engine 1
   ├── Engine 2
   └── Engine 3
          ↓
 DB / Cache / Object Storage / Model Registry
~~~

Une instance ne doit pas contenir seule un état utilisateur critique en mémoire.

## 17. État durable

Utiliser les systèmes appropriés :
- PostgreSQL pour l'état métier ;
- Redis pour cache et données temporaires ;
- object storage pour datasets et artefacts ;
- registry pour les modèles ;
- snapshots versionnés pour les connaissances.

## 18. Cache

Cache possible : knowledge snapshots, embeddings, modèles, catalogues et calculs coûteux reproductibles.

Une recommandation personnalisée ne doit jamais être mise en cache avec une clé ne contenant pas les versions pertinentes.

Clé minimale conceptuelle :

~~~text
profileVersion + knowledgeVersion + modelVersion + configurationVersion
~~~

## 19. Tâches asynchrones

Les opérations lourdes passent par des workers :
- ingestion ESCO/O*NET ;
- embeddings ;
- entraînement ;
- benchmarks ;
- recalculs graph ;
- génération de datasets.

~~~text
API → Job → Queue → Worker → Artifact / Database
~~~

## 20. Candidate Generation et performance

Ne jamais comparer inutilement chaque élève à tout l'univers des directions.

~~~text
Universe
 ↓
Candidate Generation
 ↓
Hard Constraints
 ↓
Candidate Pool K
 ↓
matching coûteux
 ↓
ranking
~~~

Les étapes coûteuses arrivent après réduction du nombre de candidats.

Chaque composant doit documenter sa complexité temporelle et mémoire ainsi que son comportement quand la volumétrie augmente.

## 21. Knowledge Graph scalable

V1 peut utiliser PostgreSQL avec `knowledge_entities` et `knowledge_relations`.

Le Domain dépend d'une abstraction de graphe et non de Neo4j.

Si les besoins de traversée augmentent, une implémentation Neo4j peut être ajoutée sans réécrire le Domain.

## 22. Embeddings scalables

Ne jamais recalculer tous les embeddings à chaque requête.

~~~text
knowledge change
 ↓
embedding job
 ↓
vector index Vn
 ↓
validation
 ↓
activate index
~~~

## 23. Observabilité

Chaque opération importante doit conserver au minimum :

~~~text
requestId
correlationId
pseudonymousStudentId
profileVersion
modelVersion
knowledgeVersion
configurationVersion
duration
status
~~~

Les logs ne doivent pas exposer inutilement les données personnelles des élèves.

## 24. Métriques techniques

Mesurer au minimum : p50, p95, p99, taux d'erreur, throughput, CPU, mémoire, cache hit rate, temps de chargement du modèle, temps de génération des candidats et temps de ranking.

Les métriques scientifiques restent séparées : Precision@K, Recall@K, NDCG@K, MAP, coverage, diversity, calibration, stabilité, fairness et explanation faithfulness.

Une API rapide n'est pas nécessairement un bon moteur d'orientation.

## 25. Résilience et fallbacks

Un composant secondaire indisponible peut avoir un fallback explicite et testé.

~~~text
semantic service unavailable
 ↓
semantic matching unavailable
 ↓
deterministic fallback
 ↓
audit = degraded_mode
~~~

En revanche, si les données essentielles sont indisponibles, le moteur ne doit pas inventer une recommandation.

Il doit pouvoir retourner `insufficient_evidence`.

## 26. Versionnement pour reconstruction

Une recommandation conserve :

~~~text
codeVersion
profileVersion
assessmentVersion
knowledgeVersion
modelVersion
featureSchemaVersion
configurationVersion
embeddingIndexVersion
randomSeed (si utilisée)
~~~

Le système doit pouvoir reconstruire une décision plusieurs mois plus tard.

## 27. Tests par module

Chaque module doit avoir, selon son rôle :
- unit tests ;
- contract tests ;
- integration tests ;
- regression tests ;
- property tests ;
- golden tests pour les composants scientifiques ;
- numerical tolerance tests pour les calculs numériques.

## 28. Non-régression scientifique

Un changement d'algorithme doit produire un benchmark avant/après :

~~~text
old implementation
       vs
new implementation
       ↓
score diff
ranking diff
explanation diff
metrics diff
       ↓
validation
~~~

Un refactoring ne doit pas modifier silencieusement le comportement scientifique.

## 29. Scalabilité testée

Tester progressivement la charge réelle :

~~~text
1
10
1 000
10 000
100 000+ students
~~~

Mesurer mémoire, latence, throughput, coût, taille des index et temps de traitement.

Les seuils de production seront définis avec l'infrastructure réelle d'Otheloo.

## 30. CI/CD obligatoire

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
regression tests
 ↓
security checks
 ↓
Docker build
 ↓
reproducibility check
~~~

Aucune modification scientifique ne doit contourner cette chaîne.

## 31. Règles Git

Les commits restent petits et spécialisés.

Exemples :

~~~text
feat(profile): add observation aggregation
feat(assessment): add adaptive item selection
feat(recommendation): add deterministic scorer
test(ranking): add ranking regression suite
refactor(skills): isolate taxonomy matcher
fix(audit): persist model version
docs(engine): document candidate generation
~~~

Éviter `update everything`, `final`, `fix stuff` ou les commits géants.

## 32. Pull Requests

Une PR doit expliquer : problème, changement, fichiers touchés, comportement avant/après, tests, métriques scientifiques, impact des contrats, performance, migration et rollback.

## 33. Quand créer un module

Créer un module lorsqu'une responsabilité devient autonome, doit être testée séparément, doit être remplaçable ou possède une frontière métier claire.

Ne pas créer un module uniquement parce qu'un fichier dépasse arbitrairement quelques lignes.

## 34. Quand créer un microservice

V1 doit rester un service moteur modulaire.

Extraire un service seulement lorsqu'un besoin réel existe : scaling indépendant, cycle de déploiement indépendant, isolation de ressources, sécurité différente, charge très différente ou ownership clairement séparé.

Le passage doit suivre :

~~~text
modular monolith
       ↓
frontière stable
       ↓
service extraction
~~~

Les contrats et tests doivent rester identiques.

## 35. Performance : mesurer avant d'optimiser

Ordre obligatoire :
1. mesurer ;
2. identifier le bottleneck ;
3. écrire un benchmark ;
4. optimiser ;
5. comparer ;
6. conserver l'optimisation uniquement si le gain est réel.

Ne pas ajouter Redis, GPU, Neo4j ou Kubernetes simplement parce que la technologie existe.

## 36. GPU et infrastructure avancée

Le moteur V1 doit pouvoir fonctionner sans GPU.

GPU uniquement si un benchmark démontre un besoin pour embeddings massifs, entraînement, inference neuronale ou GNN.

Kubernetes n'est pas une condition de démarrage. Commencer avec Docker + CI/CD + un service déployable.

## 37. Architecture cible à grande échelle

~~~text
                    OTHELOO
                       │
                API / Gateway
                       │
              Orientation Engine
                       │
       ┌───────────────┼────────────────┐
       ▼               ▼                ▼
    Profile       Recommendation     Assessment
       │               │                │
       └───────────────┼────────────────┘
                       ▼
                 Shared Contracts
                       │
       ┌───────────────┼────────────────────┐
       ▼               ▼                    ▼
  PostgreSQL          Redis          Object Storage
       │
       ├── Knowledge
       ├── Profiles
       ├── Audits
       └── Feedback

       Async Workers
       ├── ingestion
       ├── embeddings
       ├── training
       ├── benchmarks
       └── evaluation

       Registries
       ├── Model Registry
       ├── Knowledge Registry
       └── Feature Registry
~~~

Cette architecture permet de passer d'un moteur modulaire unique à une architecture distribuée sans réécrire le domaine.

## 38. Definition of Done d'un fichier

Avant de considérer un composant terminé :

~~~text
Lisible ?
Typé ?
Responsabilité unique ?
Testé ?
Observable ?
Versionné ?
Reproductible ?
Scalable ?
Remplaçable ?
Documenté ?
Rollback possible ?
~~~

Si plusieurs réponses sont non, le composant n'est pas prêt pour production.

## 39. Règle finale

Le futur moteur doit pouvoir grossir de quelques milliers à des centaines de milliers de lignes sans qu'un seul fichier, une seule classe ou un seul service devienne le centre de gravité du système.

**On ne cherche pas à avoir beaucoup de code. On cherche à avoir des frontières claires, des contrats stables et des responsabilités petites.**