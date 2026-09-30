# 28 — Recherche GitHub : architectures, algorithmes et pratiques à retenir

## 1. Objectif

Ce document transforme une revue ciblée de dépôts GitHub de systèmes de recommandation en décisions d'architecture pour le futur moteur d'orientation Otheloo.

L'objectif n'est pas de copier un dépôt ni de déclarer qu'un algorithme est universellement « le meilleur ». Les dépôts étudiés servent de références d'implémentation, d'architecture, d'évaluation et de reproductibilité.

La règle retenue est :

> **prendre le principe qui résout un problème réel d'Otheloo, le documenter, l'isoler derrière une interface stable, puis le comparer expérimentalement à une baseline avant de le conserver.**

---

## 2. Références GitHub principales étudiées

### 2.1 Microsoft Recommenders

**Référence :** `recommenders-team/recommenders`

Le projet est particulièrement utile comme bibliothèque de pratiques : préparation des données, modèles classiques et deep learning, évaluation offline, sélection/hyperparamètres et opérationnalisation. Il couvre notamment ALS, BPR, LightFM, LightGBM, LightGCN, NCF, modèles séquentiels et modèles utilisant des knowledge graphs.

**Ce qu'Otheloo doit retenir :**

- séparer préparation des données, modèle, évaluation, optimisation et opérationnalisation ;
- conserver plusieurs baselines comparables ;
- ne pas évaluer un modèle uniquement sur une métrique ;
- rendre les expériences reproductibles ;
- traiter les modèles avancés comme des variantes expérimentales, pas comme l'architecture métier elle-même.

**Décision Otheloo :** créer une couche `evaluation/` indépendante des modèles et conserver une baseline déterministe permanente.

---

### 2.2 Architecture en deux étages : retrieval → ranking

**Référence :** `10div10/two-stage-recsys`

Le dépôt montre une architecture très importante :

```
profil
  ↓
retrieval / candidate generation
  ↓
top-K candidats
  ↓
ranking
  ↓
top-N
```

Il utilise Two-Tower + FAISS pour la génération de candidats et LambdaMART/XGBoost pour le reranking.

**Ce qu'Otheloo doit retenir :**

- ne jamais comparer tous les métiers/formations avec un modèle coûteux si le catalogue devient grand ;
- séparer la génération de candidats du ranking ;
- permettre à plusieurs générateurs de produire des candidats ;
- utiliser ensuite un ranker plus riche ;
- garder un post-processing explicite pour contraintes, diversité et règles de sécurité.

**Décision Otheloo :**

```
Candidate generators
    ├── rule-based
    ├── skill-based
    ├── semantic
    ├── graph
    └── exploration
          ↓
Candidate Set
          ↓
Feature extraction
          ↓
Hybrid ranking
          ↓
Diversification
          ↓
Explanation
```

Pour Otheloo, le retrieval n'a pas besoin d'être neuronal au départ. Une génération déterministe par taxonomie, compétences, intérêts et graph peut déjà produire un excellent Candidate Set.

---

## 3. Architecture hybride recommandée

L'étude des systèmes de recommandation montre qu'un moteur robuste ne doit pas dépendre d'une seule famille d'algorithmes.

Otheloo doit combiner plusieurs signaux indépendants :

### 3.1 Matching explicite

Mesure directe entre le profil et une direction :

- intérêts ↔ intérêts ;
- compétences ↔ compétences ;
- aptitudes ↔ aptitudes ;
- valeurs ↔ valeurs ;
- matières ↔ matières ;
- préférences ↔ environnement ;
- trajectoire ↔ exigences.

Algorithmes possibles :

- cosine similarity pondérée ;
- distance euclidienne normalisée ;
- distance de Mahalanobis si la covariance est correctement estimée ;
- scores pondérés par dimension.

**V1 :** cosine + score pondéré explicable.

---

### 3.2 Skill matching

Le profil ne doit pas être représenté uniquement par des scores psychométriques.

Chaque compétence doit avoir :

```
skillId
level
confidence
source
observedAt
status
```

Le statut doit distinguer :

- declared ;
- assessed ;
- observed ;
- inferred.

Le moteur calcule :

```
skillFit
skillGap
skillConfidence
readiness
```

**Règle importante :**

> compétence inconnue ≠ compétence absente.

---

### 3.3 Semantic matching

Les embeddings peuvent rapprocher :

- une description libre d'élève ;
- une compétence ;
- une activité ;
- une formation ;
- une profession ;
- un secteur ;
- une opportunité.

Pipeline :

```
texte
 ↓
embedding versionné
 ↓
vector index
 ↓
semantic candidates
 ↓
semantic score
```

**V1 :** le semantic matching doit rester secondaire et ne doit jamais remplacer les signaux structurés.

**V2/V3 :** sentence-transformers + FAISS/pgvector après benchmark.

---

## 4. Knowledge Graph

### 4.1 Référence KGAT

**Référence :** `xiangwang1223/knowledge_graph_attention_network`

KGAT montre comment les relations de haut niveau d'un knowledge graph peuvent enrichir la recommandation.

Le principe intéressant pour Otheloo n'est pas de copier KGAT tel quel.

Le principe est :

> une direction peut être recommandée parce qu'elle est reliée à plusieurs éléments cohérents du profil, pas seulement parce qu'un vecteur est proche.

Exemple :

```
Élève
 ├── INTERESTED_IN → programmation
 ├── POSSESSES → logique
 ├── POSSESSES → résolution de problèmes
 ├── LIKES → projets techniques
 │
 └── potentiel
       ↓
    ingénierie logicielle
       ↓
    REQUIRES
       ├── algorithmique
       ├── programmation
       └── résolution de problèmes
```

Le graphe fournit donc de l'**evidence structurelle**.

---

### 4.2 Architecture KG Otheloo

Le graphe doit contenir au minimum :

- Student ;
- Interest ;
- Skill ;
- Ability ;
- Value ;
- Subject ;
- Occupation ;
- Formation ;
- Domain ;
- Sector ;
- Institution ;
- Opportunity ;
- ExplorationActivity.

Relations :

- INTERESTED_IN ;
- POSSESSES ;
- REQUIRES ;
- TEACHES ;
- PREPARES_FOR ;
- BELONGS_TO ;
- ALIGNED_WITH ;
- ACCESSIBLE_IF ;
- RELATED_TO ;
- EXPLORES ;
- COMPLETED ;
- REJECTED ;
- PREFERRED.

Le graphe doit être versionné comme une donnée scientifique.

---

## 5. Career recommendation et ESCO

Des projets GitHub orientés carrière montrent une approche simple et utile : weighted scoring + skill comparison + skill-gap analysis.

**Références :**

- `Oyebintan/Career-Recommender`
- `AnahadhBirdh/career-recommender`
- `Y4SSERk/SkillAlign`

Le dépôt SkillAlign est particulièrement intéressant pour le rapprochement entre :

- ESCO ;
- compétences ;
- embeddings ;
- recherche vectorielle ;
- knowledge graph ;
- skill gap.

**Ce qu'Otheloo doit retenir :**

- utiliser ESCO comme taxonomie de référence, pas comme vérité sur le choix individuel ;
- conserver des IDs canoniques ;
- mapper les synonymes ;
- relier compétences → occupations → formations ;
- calculer explicitement les écarts de compétences ;
- produire une justification traçable.

**Ce qu'Otheloo ne doit pas reprendre aveuglément :**

- des pourcentages de compatibilité présentés comme des probabilités ;
- des poids arbitraires non validés ;
- un petit catalogue codé directement dans le code ;
- une recommandation basée uniquement sur le texte d'un CV.

---

# 6. Learning-to-Rank

Une fois qu'Otheloo aura suffisamment de données de feedback fiables, le problème devient :

```
profil + candidat + contexte
        ↓
feature vector
        ↓
score de ranking
        ↓
ordre des directions
```

### Algorithmes à tester

Ordre recommandé :

1. Linear / weighted ranking baseline ;
2. Logistic/linear ranking ;
3. LightGBM LambdaMART ;
4. XGBoost ranking ;
5. modèle neural seulement si le benchmark le justifie.

### Pourquoi LambdaMART en premier modèle appris ?

Parce qu'un modèle d'arbres de ranking permet :

- interactions non linéaires ;
- features hétérogènes ;
- apprentissage du ranking ;
- coût raisonnable ;
- analyse des features ;
- déploiement CPU possible ;
- comparaison claire avec la baseline.

**Décision Otheloo :**

Le modèle appris ne remplace pas les règles métier.

Il devient une composante :

```
candidate
  ↓
features
  ↓
learned ranker
  ↓
policy / constraints
  ↓
diversification
```

---

# 7. Deux-Tower et recherche vectorielle

Les architectures Two-Tower sont pertinentes lorsqu'il faut retrouver rapidement un petit ensemble de candidats dans un catalogue très large.

Structure :

```
Student Tower → student embedding
Direction Tower → direction embedding

student embedding
        ↓
ANN search
        ↓
candidate directions
```

FAISS peut servir d'index local/versionné.

**Mais :**

Otheloo ne doit pas commencer par Two-Tower.

Tant que le catalogue est maîtrisable, le coût et la complexité d'un modèle neuronal de retrieval ne sont pas justifiés.

Il devient intéressant si :

- le nombre de directions/opportunités devient très élevé ;
- les recherches sémantiques deviennent coûteuses ;
- les benchmarks montrent un gain ;
- le cold-start et la qualité du retrieval sont correctement traités.

---

# 8. Collaborative filtering : attention au problème Otheloo

Les systèmes classiques utilisent :

- ALS ;
- BPR ;
- Matrix Factorization ;
- LightGCN ;
- UserKNN ;
- ItemKNN.

Ces méthodes sont excellentes pour des systèmes où l'on possède beaucoup d'interactions utilisateur-item.

Mais Otheloo ne doit pas considérer :

```
clic sur métier X
=
métier X adapté à l'élève
```

Un clic peut signifier :

- curiosité ;
- hasard ;
- exploration ;
- popularité ;
- influence externe ;
- simple lecture.

Le feedback doit donc être typé.

Exemple :

```
VIEW
OPEN_DETAILS
SAVE
EXPLORE
START_ACTIVITY
COMPLETE_ACTIVITY
LIKE
DISLIKE
REJECT
REQUEST_MORE
CONFIRM_INTEREST
CONFIRM_DISINTEREST
```

Chaque événement possède une force et une interprétation différente.

---

# 9. Exploration et contextual bandits

**Référence :** `bagheri365/PolicyRecLab`

Cette référence est importante pour une raison plus fondamentale que l'algorithme lui-même :

> avant d'évaluer une politique offline, il faut vérifier que les données observées permettent réellement d'identifier cette politique.

Les méthodes pertinentes comprennent :

- IPS ;
- SNIPS ;
- Direct Method ;
- Doubly Robust ;
- clipping ;
- diagnostics de support ;
- effective sample size ;
- analyse de propensity.

### Pour Otheloo

Un contextual bandit ne doit pas choisir directement :

> « ton métier est X ».

Il doit choisir une **expérience réversible** :

- activité ;
- mini-projet ;
- découverte d'une formation ;
- entretien avec un professionnel ;
- exercice ;
- simulation ;
- contenu à explorer.

Puis observer :

```
recommendation
 ↓
exploration
 ↓
feedback
 ↓
new observation
 ↓
profile update
```

C'est une différence fondamentale entre **recommandation d'exploration** et **décision d'orientation**.

---

# 10. Off-policy evaluation

Otheloo doit documenter le logging policy.

Chaque recommandation doit pouvoir conserver :

```
candidateSet
policyVersion
modelVersion
scores
propensities si disponibles
selectedItems
context
timestamp
feedback
```

Sans cela, il sera impossible de comprendre correctement les biais de sélection.

### Règle

Ne jamais écrire :

> « le nouveau modèle est meilleur »

uniquement parce que son score offline augmente.

Il faut connaître :

- le dataset ;
- la politique qui a généré les observations ;
- la couverture ;
- le support ;
- les métriques ;
- les intervalles/incertitudes ;
- les effets sur diversité ;
- les effets sur calibration ;
- les effets sur fairness ;
- les effets sur l'explicabilité.

---

# 11. Feature Store et zéro train/serve skew

Les architectures modernes de production insistent sur un problème critique :

> une feature calculée différemment pendant l'entraînement et en production peut rendre les résultats incohérents.

Le pattern à retenir :

```
Feature definition
       ↓
offline computation
       ↓
training dataset

même définition
       ↓
online computation
       ↓
inference
```

Le même transformateur doit être utilisé lorsque cela est possible.

### Otheloo

Créer une couche :

```
FeatureDefinition
FeatureProcessor
FeatureSnapshot
FeatureSchemaVersion
```

Une feature doit être traçable :

```
featureName
version
source
formula
timestamp
dependencies
```

---

# 12. Frozen artifacts

Les architectures modernes étudiées montrent une bonne pratique importante :

avant entraînement/serving, produire des artefacts immuables :

- vocabularies ;
- normalization statistics ;
- feature schema ;
- popularity statistics si utilisées ;
- embedding index ;
- knowledge snapshot ;
- model artifact ;
- configuration snapshot.

Cela permet de reconstruire exactement une recommandation passée.

### Contrat de reproductibilité

```
same profile snapshot
+ same assessment version
+ same feature version
+ same knowledge snapshot
+ same model
+ same configuration
+ same random seed
=
same recommendation
```

S'il existe une exception, elle doit être explicitement documentée.

---

# 13. Multi-stage ranking recommandé

L'architecture cible Otheloo devient :

```
┌─────────────────────────────┐
│ Student Profile             │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│ Candidate Generation        │
│ rules / skills / semantic   │
│ graph / exploration         │
└──────────────┬──────────────┘
               ↓
        Candidate Set
               ↓
┌─────────────────────────────┐
│ Feature Construction        │
│ profile × candidate × graph │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│ Base / Hybrid Scoring       │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│ Learned Ranking             │
│ LambdaMART when validated   │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│ Policy + Safety Constraints │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│ Diversification             │
│ MMR / similarity penalties  │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│ Explanation + Skill Gap     │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│ Exploration Opportunities   │
└──────────────┬──────────────┘
               ↓
         Final response
```

---

# 14. Algorithmes retenus par phase

| Phase | V1 | V2 | V3 | V4+ |
|---|---|---|---|---|
| Candidate generation | règles + taxonomie | semantic retrieval | ANN / Two-Tower | multi-retriever learned |
| Interest matching | weighted cosine | calibrated similarity | learned features | neural representation |
| Skill matching | exact + taxonomy | semantic skill matching | learned skill relevance | graph/neural |
| Ranking | deterministic weighted score | calibrated hybrid | LambdaMART | neural ranker si prouvé |
| Graph | traversal/rules | graph scoring | embeddings | GNN/R-GCN |
| Diversity | MMR | contextual MMR | learned reranking | constrained optimization |
| Uncertainty | confidence + propagation | calibration | probabilistic models | advanced uncertainty |
| Exploration | rules | safe experiments | contextual bandit | policy learning |
| Feedback | typed events | Bayesian updates | learned signals | longitudinal policy |
| Retrieval | full/filtered catalog | vector index | Two-Tower | multi-stage retrieval |

---

# 15. Ce qu'il ne faut surtout pas faire

Les recherches GitHub montrent aussi des anti-patterns fréquents.

### 15.1 Commencer directement par un gros modèle

À éviter :

```
GNN + Transformer + embeddings + bandit
```

sans baseline.

Otheloo doit d'abord savoir répondre :

> est-ce que la nouvelle méthode améliore réellement la qualité ?

---

### 15.2 Confondre score et probabilité

```
0.82 compatibility
```

ne signifie pas automatiquement :

```
82% probability that this career is right
```

Une probabilité exige une définition statistique et une calibration appropriée.

---

### 15.3 Utiliser le feedback comme vérité absolue

Un élève peut :

- aimer une activité mais ne pas vouloir en faire un métier ;
- rejeter une profession sans l'avoir réellement découverte ;
- changer d'avis ;
- répondre sous influence.

Le feedback doit devenir une observation contextualisée.

---

### 15.4 Optimiser uniquement le clic

Si le moteur apprend uniquement :

```
maximize click
```

il risque de favoriser :

- les métiers populaires ;
- les contenus sensationnels ;
- les choix déjà connus ;
- les boucles de renforcement.

Otheloo doit mesurer aussi :

- qualité d'exploration ;
- diversité ;
- calibration ;
- satisfaction ;
- compréhension ;
- progression ;
- agency ;
- qualité du feedback ;
- skill development.

---

# 16. Benchmark obligatoire des algorithmes

Chaque nouvel algorithme doit être comparé à une baseline.

### Dataset

Séparer :

```
train
validation
test
```

et privilégier les splits temporels lorsque les interactions sont longitudinales.

### Métriques ranking

- Precision@K ;
- Recall@K ;
- NDCG@K ;
- MAP ;
- MRR ;
- coverage ;
- diversity ;
- novelty.

### Métriques probabilistes

- Brier score ;
- log loss ;
- calibration error ;
- reliability curves.

### Métriques système

- p50 ;
- p95 ;
- p99 ;
- throughput ;
- mémoire ;
- coût ;
- taille des index.

### Métriques Otheloo

- explanation accuracy ;
- explanation completeness ;
- uncertainty quality ;
- skill-gap usefulness ;
- exploration usefulness ;
- profile clarity ;
- agency ;
- fairness ;
- stabilité longitudinale.

---

# 17. Architecture expérimentale

Chaque expérience doit produire un artefact versionné :

```
experimentId
datasetVersion
featureSchemaVersion
knowledgeVersion
modelVersion
configurationVersion
codeVersion
randomSeed
metrics
artifacts
decision
```

Et une décision :

- ACCEPTED ;
- REJECTED ;
- INCONCLUSIVE ;
- DEPRECATED.

Une expérience rejetée reste documentée.

Cela évite de refaire les mêmes erreurs et permet de comprendre pourquoi une méthode a été abandonnée.

---

# 18. Registre des algorithmes

Créer un registre :

```
AlgorithmRegistry
```

Chaque algorithme doit déclarer :

```
algorithmId
family
version
inputSchema
outputSchema
trainingRequired
deterministic
supportsUncertainty
explainabilityLevel
computationalCost
dataRequirements
coldStartBehavior
status
```

Exemples :

```
deterministic_hybrid_v1
weighted_cosine_v1
skill_matcher_v1
semantic_retriever_v1
lambdamart_ranker_v1
graph_ranker_v1
contextual_bandit_v1
```

---

# 19. Architecture finale recommandée pour Otheloo

```
                    OTHELOO
                       │
                 Student Profile
                       │
             ┌─────────┴─────────┐
             │                   │
        Assessments          Observations
             │                   │
             └─────────┬─────────┘
                       ↓
              Feature Construction
                       │
        ┌──────────────┼──────────────┐
        ↓              ↓              ↓
   Knowledge       Skill Engine   Psychometrics
     Graph
        │              │              │
        └──────────────┼──────────────┘
                       ↓
              Candidate Generation
                       │
        ┌──────────────┼──────────────┐
        ↓              ↓              ↓
      Rules         Semantic        Graph
        │              │              │
        └──────────────┼──────────────┘
                       ↓
                 Candidate Set
                       ↓
                Feature Builder
                       ↓
               Hybrid Scoring
                       ↓
                Learned Ranking
                 (future/validated)
                       ↓
             Safety / Constraints
                       ↓
                Diversification
                       ↓
              Uncertainty Engine
                       ↓
           Explanation + Skill Gap
                       ↓
             Exploration Engine
                       ↓
                Recommendation
                       ↓
                  Feedback
                       ↓
             Longitudinal Profile
                       ↺
```

---

# 20. Ce que nous devons réellement implémenter en premier

La recherche ne change pas la règle fondamentale du projet.

### Phase A — déterministe

Construire :

1. StudentProfile ;
2. AssessmentResult ;
3. Direction Catalog ;
4. Knowledge Snapshot ;
5. Skill model ;
6. Candidate generation ;
7. weighted matching ;
8. uncertainty ;
9. ranking ;
10. diversification ;
11. skill gap ;
12. explanation facts ;
13. audit snapshot.

### Phase B — semantic

Ajouter :

1. embeddings ;
2. vector index ;
3. semantic candidate generation ;
4. semantic matching ;
5. benchmark contre V1.

### Phase C — learned ranking

Ajouter :

1. feature dataset ;
2. point-in-time correct features ;
3. LambdaMART ;
4. calibration ;
5. offline evaluation ;
6. model registry ;
7. shadow inference ;
8. comparaison V1 vs learned model.

### Phase D — graph learning

Ajouter seulement si le benchmark montre une valeur :

1. graph embeddings ;
2. graph ranking ;
3. GNN/R-GCN ;
4. re-ranking explicable ;
5. comparaison contre graph rules.

### Phase E — exploration

Ajouter :

1. typed feedback ;
2. exploration policies ;
3. off-policy evaluation ;
4. safe contextual bandits ;
5. longitudinal evaluation.

---

# 21. Décisions d'architecture consolidées

Après confrontation avec les références GitHub étudiées, les décisions suivantes deviennent des règles du projet :

### Règle 1 — Hybrid first

Otheloo est un moteur hybride, pas un modèle unique.

### Règle 2 — Retrieval puis ranking

La génération de candidats et le ranking sont deux problèmes différents.

### Règle 3 — Explainability by construction

Les faits d'explication sont produits par les mêmes composants qui calculent les signaux.

### Règle 4 — Model behind interface

Aucun modèle ne doit être directement couplé à l'API.

### Règle 5 — Data and model versioning

Aucune recommandation importante ne doit être impossible à reconstruire.

### Règle 6 — Offline before online learning

Tout nouveau modèle doit être validé offline avant exposition.

### Règle 7 — Exploration ≠ orientation finale

Le bandit peut sélectionner des expériences ; il ne décide pas du métier d'un élève.

### Règle 8 — No implicit truth from clicks

Les interactions sont des observations contextualisées.

### Règle 9 — Baseline never deleted

La baseline déterministe reste disponible pour comparaison et fallback.

### Règle 10 — Complexity must earn its place

Une nouvelle technologie n'entre dans le moteur que si une mesure montre qu'elle apporte un bénéfice supérieur à son coût et à sa complexité.

---

# 22. Sources GitHub étudiées

- Microsoft Recommenders — `recommenders-team/recommenders`
- Two-Stage Recommender — `10div10/two-stage-recsys`
- KGAT — `xiangwang1223/knowledge_graph_attention_network`
- SkillAlign — `Y4SSERk/SkillAlign`
- CareerRecommender — `Oyebintan/Career-Recommender`
- Career Recommender — `AnahadhBirdh/career-recommender`
- PolicyRecLab — `bagheri365/PolicyRecLab`
- Two-Tower / MMoE reference — `tanaysd/mmoe-recsys`
- Production recommendation architecture — `girijesh-ai/ai-interview-codex`
- Recommendation system design — `hitman-abhi/system-design-guide`
- NVIDIA Merlin — `NVIDIA-Merlin/Merlin`

Ces références doivent être utilisées comme **sources d'architecture et d'implémentation**, avec validation scientifique indépendante pour toute décision d'Otheloo.

---

# 23. Conclusion

La conclusion importante de cette recherche n'est pas qu'Otheloo doit utiliser le modèle le plus complexe.

Le pattern qui ressort est beaucoup plus solide :

```
GOOD DATA
   ↓
GOOD FEATURES
   ↓
CANDIDATE GENERATION
   ↓
HYBRID MATCHING
   ↓
LEARNED RANKING
   ↓
POLICY / CONSTRAINTS
   ↓
DIVERSIFICATION
   ↓
EXPLANATION
   ↓
EXPLORATION
   ↓
FEEDBACK
   ↓
LONGITUDINAL LEARNING
```

La complexité doit être introduite progressivement, avec une baseline permanente, des expériences reproductibles et des critères mesurables.

**Otheloo doit donc être construit comme un système de recommandation scientifique et évolutif, et non comme une simple fonction `recommend()`.**
