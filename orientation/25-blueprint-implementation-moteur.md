# 25 — Blueprint d'implémentation du moteur Otheloo

> Ce document transforme la spécification scientifique et architecturale en **plan d'implémentation exécutable**. Il ne constitue pas une implémentation du moteur. Chaque étape ci-dessous doit produire du code, des contrats, des données de test, des métriques et des preuves de validation avant de passer à la suivante.

## 1. Objectif

Le moteur cible doit transformer des observations longitudinales d'un élève en hypothèses d'orientation explorables, sans transformer un score en verdict.

Le système complet est :

```
Observations
   ↓
Student Profile Engine
   ↓
Assessment Engine ─────────┐
   ↓                       │
Psychometrics              │
   ↓                       │
Knowledge Graph             │
   ↓                       │
Candidate Generation ←──────┘
   ↓
Hard Constraints
   ↓
Profile Matching
   ↓
Skill Matching
   ↓
Semantic Matching
   ↓
Graph Matching
   ↓
Hybrid Scoring
   ↓
Uncertainty
   ↓
Diversification
   ↓
Ranking
   ↓
Explanation
   ↓
Skill Gap
   ↓
Exploration Engine
   ↓
Feedback
   ↓
New Observations
   ↓
New Profile Version
```

Une **Recommendation Audit Layer** traverse toute la chaîne.

---

## 2. Ordre d'implémentation obligatoire

L'implémentation ne doit pas commencer par les modèles les plus complexes.

### Phase 0 — Contrats, sécurité et observabilité

À implémenter :

- contrats Pydantic/API versionnés ;
- identifiant technique pseudonyme ;
- séparation identité / données d'orientation ;
- consentements et règles relatives aux mineurs ;
- validation stricte des entrées ;
- gestion des erreurs ;
- corrélation des requêtes ;
- logs sans données sensibles ;
- configuration par environnement ;
- secrets hors dépôt ;
- version du modèle et de la base de connaissances ;
- audit trail append-only.

**Livrables :**
- schemas ;
- conventions d'erreurs ;
- politique de données ;
- tests de contrats ;
- tests de sécurité de base.

**Critère de sortie :** aucune couche métier ne dépend directement d'une donnée d'identité.

---

# 3. Student Profile Engine

## 3.1 Responsabilité

Construire et maintenir un profil longitudinal à partir d'observations hétérogènes.

Pipeline :

```
observation
→ validation
→ normalisation
→ agrégation temporelle
→ signal
→ confiance
→ profil versionné
```

## 3.2 Modèle d'observation

Chaque observation doit au minimum contenir :

- studentId ;
- dimension ;
- value ;
- confidence ;
- source ;
- observedAt ;
- version ;
- provenance ;
- éventuellement context ;
- éventuellement evaluatorId pseudonymisé.

Les sources doivent être distinguées :

- declared ;
- assessment ;
- observed ;
- grade ;
- task ;
- teacher_feedback ;
- exploration ;
- inferred.

## 3.3 Dimensions

Le moteur doit pouvoir représenter séparément :

- intérêts ;
- aptitudes ;
- compétences ;
- valeurs ;
- préférences d'environnement ;
- contraintes ;
- trajectoire ;
- signaux comportementaux autorisés.

Une valeur de compétence inférée ne doit jamais être confondue avec une compétence directement observée.

## 3.4 Agrégation longitudinale

Implémenter progressivement :

1. moyenne pondérée par confiance ;
2. pondération temporelle ;
3. stabilité ;
4. tendance ;
5. volatilité ;
6. récence ;
7. conflit entre sources ;
8. confiance globale.

Chaque agrégat doit conserver sa provenance.

## 3.5 Versionnement

Chaque modification produit :

```
profileVersion
inputObservationIds
previousProfileVersion
newSignals
changedDimensions
timestamp
```

Le profil doit être reconstruisible à partir des observations.

## 3.6 Tests

- observation unique ;
- observations contradictoires ;
- sources différentes ;
- observation ancienne vs récente ;
- confiance faible/forte ;
- relecture d'une version ;
- déterminisme ;
- absence de mutation destructive.

---

# 4. Assessment Engine

## 4.1 Responsabilité

Transformer des réponses à des instruments d'évaluation en estimations psychométriques utilisables par le profil.

Pipeline :

```
Question Bank
→ Instrument
→ Item Selection
→ Response
→ Scoring
→ θ estimate
→ Standard Error
→ Information Gain
→ Stop Rule
→ Profile Update
```

## 4.2 V1

Commencer avec :

- RIASEC ;
- modèle IRT 2PL simplifié ;
- estimation de θ ;
- erreur standard ;
- sélection adaptative élémentaire ;
- règles de terminaison.

Ne pas prétendre avoir un CAT psychométriquement validé tant que les paramètres d'items et la calibration n'ont pas été validés.

## 4.3 V2+

Ajouter ensuite :

- MIRT ;
- calibration réelle des items ;
- banques versionnées ;
- exposition des items ;
- contrôle de sur-exposition ;
- content balancing ;
- shadow testing ;
- simulation CAT ;
- BKT pour apprentissage de compétences.

## 4.4 Critères de validation

- fiabilité ;
- précision de l'estimation ;
- réduction de l'erreur ;
- information moyenne par item ;
- stabilité test-retest ;
- temps moyen ;
- biais par sous-groupes ;
- validité convergente.

---

# 5. Knowledge Graph

## 5.1 Responsabilité

Représenter les relations entre profil, compétences, matières, formations, métiers, secteurs et opportunités.

Graphe cible :

```
Student
 ↓
Interest
 ↓
Skill
 ↓
Subject
 ↓
Formation
 ↓
Occupation
 ↓
Sector
 ↓
Opportunity
```

## 5.2 Types de nœuds

Minimum :

- Interest ;
- Ability ;
- Skill ;
- Subject ;
- Formation ;
- Diploma ;
- Occupation ;
- Sector ;
- Institution ;
- Opportunity ;
- Domain.

## 5.3 Relations

Minimum :

- INTERESTED_IN ;
- POSSESSES ;
- REQUIRES ;
- TEACHES ;
- PREPARES_FOR ;
- BELONGS_TO ;
- RELATED_TO ;
- ACCESSIBLE_IF ;
- ALIGNED_WITH ;
- LEADS_TO ;
- AVAILABLE_AT.

## 5.4 Provenance

Chaque donnée externe doit conserver :

- source ;
- version ;
- date d'import ;
- identifiant externe ;
- transformation appliquée ;
- confiance ;
- licence si nécessaire.

Distinguer explicitement :

**Knowledge Base** = connaissances utilisées pour raisonner.

**Training Dataset** = données utilisées pour apprendre un modèle.

ESCO/O*NET peuvent alimenter la première catégorie ; ils ne constituent pas à eux seuls une vérité terrain permettant de déclarer qu'un métier est approprié à un élève.

## 5.5 Implémentation progressive

V1 :

- modèle typé ;
- stockage relationnel ;
- import ESCO/O*NET ;
- indexation ;
- traversals déterministes.

V2 :

- embeddings ;
- recherche vectorielle ;
- chemins pondérés ;
- graph similarity.

V3+ :

- graphe spécialisé / Neo4j si le volume et les requêtes le justifient ;
- GNN uniquement après preuve de valeur.

---

# 6. Candidate Engine

## 6.1 Responsabilité

Produire un ensemble de directions plausibles avant tout ranking.

Sources :

- intérêts ;
- compétences ;
- matières ;
- formations ;
- occupations ;
- secteurs ;
- opportunités ;
- préférences ;
- contraintes.

## 6.2 Génération

Un candidat peut être généré par :

- relation directe du graphe ;
- similarité de profil ;
- skill overlap ;
- semantic similarity ;
- intérêt ;
- parcours de formation ;
- opportunité disponible.

Le candidate set doit être conservé dans l'audit.

## 6.3 Hard Constraints

Les contraintes bloquantes doivent être séparées du scoring.

Exemples :

- prérequis explicitement obligatoires ;
- formation indisponible dans le contexte demandé ;
- contrainte géographique déclarée ;
- niveau minimal réellement requis ;
- contrainte temporelle explicite.

Une contrainte ne doit jamais être utilisée silencieusement pour modifier un score.

---

# 7. Hybrid Matching Engine

Pour chaque candidat, calculer séparément :

```
InterestFit
AbilityFit
SkillFit
ValueFit
EnvironmentFit
TrajectoryFit
SemanticFit
GraphFit
SkillGapPenalty
ConstraintStatus
```

Ne pas réduire immédiatement ces dimensions à un seul nombre.

## 7.1 Score

Une première forme :

```
S(d|p) =
wI·InterestFit +
wA·AbilityFit +
wS·SkillFit +
wV·ValueFit +
wE·EnvironmentFit +
wT·TrajectoryFit +
wSem·SemanticFit +
wGraph·GraphFit -
wG·SkillGapPenalty
```

Les poids doivent être versionnés.

## 7.2 Confiance

La confiance est calculée séparément à partir notamment de :

- quantité d'évidence ;
- qualité des sources ;
- récence ;
- cohérence ;
- couverture des dimensions ;
- erreur psychométrique.

**Compatibility ≠ Confidence.**

Ne jamais présenter `0.81` comme une probabilité sans calibration statistique explicite.

---

# 8. Uncertainty Engine

Pour chaque recommandation :

```
compatibility
confidence
uncertainty
evidence
missingInformation
skillsToExplore
```

Exemple contractuel :

```json
{
  "direction": "Data Science",
  "compatibility": 0.81,
  "confidence": 0.67,
  "uncertainty": 0.33,
  "evidence": [],
  "missing_information": [],
  "skills_to_explore": []
}
```

L'incertitude doit identifier ce qui manque pour augmenter la confiance.

Exemples :

- trop peu d'observations ;
- intérêts non discriminants ;
- compétence non évaluée ;
- données contradictoires ;
- connaissance du parcours incomplète.

---

# 9. Skill Gap Engine

Pour chaque direction :

```
requiredSkill
vs
observedSkill
→ gap
→ importance
→ action
```

Sortie :

- forces ;
- compétences à renforcer ;
- compétences non observées ;
- skill gap ;
- action recommandée ;
- impact attendu ;
- niveau de confiance.

Le moteur ne doit pas transformer un gap en exclusion automatique.

Un gap peut signifier :

**« à explorer / renforcer »**

et non :

**« impossible »**.

---

# 10. Diversification et Ranking

## 10.1 Ranking

Le ranking intervient après génération et matching.

Il doit recevoir :

- candidats ;
- scores décomposés ;
- contraintes ;
- confiance ;
- diversité ;
- provenance.

## 10.2 Diversification

Éviter de retourner cinq variantes quasi identiques.

Une première stratégie peut utiliser une pénalisation de similarité :

```
MMR = λ·relevance - (1-λ)·similarityToSelected
```

Le paramètre et la version doivent être audités.

## 10.3 Learning-to-Rank

Seulement après constitution d'un dataset de qualité :

- LambdaMART/LightGBM ;
- features versionnées ;
- labels définis ;
- split temporel ;
- offline evaluation ;
- calibration ;
- fairness audit.

---

# 11. Explanation Engine

Chaque recommandation doit pouvoir répondre :

### Pourquoi ?

Quelles observations ont contribué ?

### Qu'est-ce qui est solide ?

Quels signaux ont une forte confiance ?

### Qu'est-ce qui est incertain ?

Quelles informations manquent ?

### Que renforcer ?

Quels skills gaps existent ?

### Que pourrait-on tester ?

Quelle expérience permettrait de mieux informer le profil ?

L'explication doit être produite à partir des mêmes preuves que le moteur, pas inventée après coup par une couche générative.

---

# 12. Exploration Engine

L'objectif n'est plus seulement de recommander.

Le moteur doit aussi proposer des expériences réversibles permettant de réduire l'incertitude.

Exemples :

- mini-projet ;
- quiz ;
- entretien avec un professionnel ;
- visite ;
- activité pratique ;
- cours court ;
- challenge.

Chaque exploration possède :

- id ;
- objectifs ;
- dimensions ciblées ;
- durée ;
- information gain estimé ;
- coût/effort ;
- niveau de risque ;
- action ;
- résultat attendu.

Pipeline :

```
Hypothèse
→ Exploration
→ Réaction
→ Observation
→ Profile Update
→ Nouvelle hypothèse
```

## Bandits

Les bandits contextuels ne doivent arriver qu'après :

- moteur déterministe stable ;
- logging fiable ;
- feedback ;
- offline evaluation ;
- simulations ;
- garde-fous.

Ils servent à choisir une **expérience d'exploration**, pas à choisir directement le métier d'un enfant.

---

# 13. Feedback Engine

Le feedback doit être traité comme une nouvelle observation, pas comme une vérité absolue.

Exemple :

```
exploration completed
→ reaction
→ interest observation
→ skill observation
→ confidence
→ provenance
→ profile version N+1
```

Le système doit conserver :

- feedback brut ;
- interprétation ;
- confiance ;
- source ;
- timestamp ;
- exploration concernée.

---

# 14. Recommendation Audit Layer

C'est une couche obligatoire et transversale.

Chaque recommandation doit conserver :

```
recommendationId
studentId
profileVersion
assessmentVersion
modelVersion
knowledgeVersion
inputSnapshot
candidateSet
constraints
scores
evidence
uncertainty
explanation
rankingReason
timestamp
```

## Reconstruction

À une date ultérieure, le système doit pouvoir répondre :

> Pourquoi cette direction a-t-elle été proposée à cet élève à cette date ?

Il doit pouvoir reconstruire :

1. le profil utilisé ;
2. les réponses disponibles ;
3. la version de la banque de questions ;
4. les connaissances utilisées ;
5. les candidats générés ;
6. les contraintes ;
7. les scores ;
8. le ranking ;
9. la diversification ;
10. l'explication produite.

Une recommandation non reconstructible est considérée comme insuffisamment auditée.

---

# 15. API cible

Le moteur doit exposer progressivement :

```
POST /v1/orientation/profile
POST /v1/orientation/observations
GET  /v1/orientation/profile/{studentId}

POST /v1/orientation/assessments
POST /v1/orientation/assessments/{sessionId}/responses
GET  /v1/orientation/assessments/{sessionId}

POST /v1/orientation/recommendations
GET  /v1/orientation/recommendations/{recommendationId}

POST /v1/orientation/explorations
POST /v1/orientation/feedback

GET /v1/orientation/audit/{recommendationId}
```

Les contrats API doivent être versionnés et testés.

---

# 16. Architecture logicielle cible

Une première implémentation doit rester un **service indépendant unique**, organisé en modules :

```
orientation-engine/
├── api/
├── contracts/
├── profile/
├── assessments/
├── psychometrics/
├── knowledge/
├── candidates/
├── matching/
├── scoring/
├── uncertainty/
├── skills/
├── ranking/
├── diversification/
├── explanations/
├── exploration/
├── feedback/
├── audit/
├── persistence/
└── evaluation/
```

Ne pas créer immédiatement plusieurs microservices.

Le découpage réseau ne doit arriver que lorsqu'une contrainte opérationnelle réelle le justifie.

---

# 17. Persistance minimale

Tables/concepts minimum :

- students ;
- observations ;
- profile_versions ;
- assessment_sessions ;
- assessment_responses ;
- assessment_results ;
- knowledge_entities ;
- knowledge_relations ;
- recommendations ;
- recommendation_audits ;
- explorations ;
- exploration_events ;
- feedback ;
- model_versions ;
- knowledge_versions ;
- consents ;
- fairness_audits.

---

# 18. Évaluation et benchmark

Chaque étape doit être mesurée contre la précédente.

## Matching

- Precision@K ;
- Recall@K ;
- NDCG@K ;
- MAP ;
- coverage.

## Ranking

- NDCG ;
- stability ;
- diversity ;
- novelty.

## Profil

- reliability ;
- test-retest ;
- confidence calibration ;
- drift.

## Psychométrie

- RMSE/MAE sur theta lorsque vérité disponible ;
- standard error ;
- information gain ;
- temps de passation.

## Explicabilité

- factual consistency ;
- evidence coverage ;
- explanation stability.

## Fairness

- métriques par groupes pertinents ;
- calibration ;
- error rates ;
- exposure disparity.

## Produit

- satisfaction ;
- agency ;
- profile clarity ;
- usefulness ;
- exploration completion ;
- qualité du feedback.

---

# 19. Dataset et vérité terrain

Il faut construire progressivement trois catégories de données :

### A. Knowledge Base

ESCO, O*NET, formations, diplômes, institutions, prérequis, opportunités.

### B. Observational Data

Observations réelles d'élèves :

- réponses ;
- compétences ;
- activités ;
- feedback ;
- trajectoires.

### C. Evaluation Labels

Labels nécessaires pour évaluer le moteur :

- pertinence d'une direction ;
- utilité d'une recommandation ;
- qualité d'une exploration ;
- satisfaction ;
- évolution du profil.

Une observation produit ne doit pas automatiquement devenir un label d'apprentissage.

---

# 20. Tests obligatoires

### Unit

Chaque algorithme doit être testé isolément.

### Contract

API et schémas.

### Integration

Profile → Recommendation → Audit.

### Regression

Une modification ne doit pas modifier silencieusement les résultats attendus.

### Property-based

Exemples :

- score borné ;
- confiance entre 0 et 1 ;
- ordre déterministe à entrée identique ;
- aucune contrainte violée ;
- aucune recommandation impossible générée.

### Fairness

Tests par groupes et scénarios synthétiques.

### Reproducibility

Même snapshot + mêmes versions = même décision, à tolérance numérique documentée.

---

# 21. Observabilité

Chaque exécution doit pouvoir être suivie par :

- requestId ;
- student pseudonymous ID ;
- recommendationId ;
- profileVersion ;
- modelVersion ;
- knowledgeVersion ;
- latency ;
- stage timings ;
- errors.

Ne jamais loguer inutilement les réponses personnelles ou données sensibles.

---

# 22. Versionnement scientifique

Versionner indépendamment :

- questionnaireVersion ;
- itemBankVersion ;
- psychometricModelVersion ;
- profileVersion ;
- knowledgeVersion ;
- scoringVersion ;
- rankingVersion ;
- explorationPolicyVersion.

Le système ne doit jamais avoir un unique `modelVersion` opaque pour tout.

---

# 23. Déploiement progressif

### V1 — Deterministic Engine

- profile ;
- assessments simples ;
- knowledge graph relationnel ;
- candidate generation ;
- règles ;
- scoring ;
- uncertainty ;
- skill gap ;
- diversification ;
- explanations ;
- audit.

### V2 — Semantic Engine

- embeddings ;
- vector search ;
- semantic matching ;
- meilleure exploration ;
- graph paths ;
- BKT/MIRT selon validation.

### V3 — Learned Ranking

- dataset ;
- LambdaMART ;
- offline evaluation ;
- calibration ;
- fairness audit.

### V4 — Adaptive Exploration

- contextual bandits ;
- simulation ;
- replay ;
- inverse propensity scoring ;
- doubly robust evaluation.

### V5 — Advanced Graph Learning

- GNN/R-GCN ;
- graph embeddings ;
- reranking explicable ;
- uniquement si benchmark positif.

---

# 24. Definition of Done

Le moteur ne doit pas être considéré comme « implémenté » simplement parce qu'une API répond.

Une phase est terminée uniquement si :

- code présent ;
- contrats présents ;
- tests présents ;
- données de démonstration présentes ;
- métriques définies ;
- résultats reproductibles ;
- audit disponible ;
- versionnement disponible ;
- documentation mise à jour ;
- limites explicitement documentées.

---

# 25. Ordre concret des futurs commits

Pour transformer cette documentation en code, utiliser des commits séparés et vérifiables :

1. `feat: establish orientation engine contracts and security`
2. `feat: implement longitudinal student profile engine`
3. `feat: implement assessment engine baseline`
4. `feat: add psychometric scoring and adaptive item selection`
5. `feat: implement knowledge graph and source ingestion`
6. `feat: implement candidate generation and hard constraints`
7. `feat: implement hybrid profile skill semantic and graph matching`
8. `feat: implement uncertainty and confidence calibration`
9. `feat: implement skill gap analysis`
10. `feat: implement ranking and diversification`
11. `feat: implement explanation engine`
12. `feat: implement recommendation audit layer`
13. `feat: implement exploration and feedback loop`
14. `feat: add persistence and API integration`
15. `test: add evaluation benchmark and reproducibility suite`
16. `docs: document production deployment and model governance`

Cette séquence doit être respectée autant que possible afin que chaque couche puisse être évaluée avant d'alimenter la suivante.

---

## Principe final

Le moteur Otheloo n'est pas un « score de métier ».

C'est un système longitudinal :

```
mesurer
→ estimer
→ relier
→ générer
→ comparer
→ expliquer
→ explorer
→ observer
→ apprendre
```

Le résultat attendu est une **aide à l'exploration**, accompagnée de preuves, d'incertitude et d'une provenance reconstructible.
