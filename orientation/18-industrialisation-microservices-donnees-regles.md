# Industrialisation du moteur d'orientation : dépôt, microservice, données et règles

## 1. Décision d'architecture

Le moteur d'orientation doit pouvoir évoluer indépendamment du produit Otheloo.

Décision cible :

    Otheloo
    ├── Frontend : React / TypeScript
    └── Backend produit : Node.js / TypeScript
                 │
                 │ API HTTP
                 ▼
        otheloo-orientation-engine
        └── Python / FastAPI

Le moteur d'orientation est un **service indépendant**, mais il ne doit pas être découpé artificiellement en plusieurs microservices au début.

### Principe

Commencer par :

    1 dépôt
    1 service déployable
    plusieurs modules internes

Puis extraire un service seulement lorsque la charge, le cycle de déploiement, l'isolation des données ou les contraintes techniques le justifient.

## 2. Pourquoi un dépôt séparé ?

Le moteur a un cycle de vie différent du backend Otheloo.

Il pourra évoluer avec :

- des expériences scientifiques ;
- des versions de questionnaires ;
- des modèles ;
- des jeux de données ;
- des benchmarks ;
- des versions du Knowledge Graph ;
- des expérimentations ML ;
- des pipelines d'entraînement ;
- des métriques propres.

Le dépôt séparé permet aussi de ne pas mélanger :

    logique produit
    ≠
    recherche / ML / recommandation

Le dépôt peut être nommé par exemple :

    2vivien/othello-orientation-engine

Le nom définitif doit être choisi avant création du dépôt.

## 3. Pourquoi Python ?

Otheloo reste en Node.js / TypeScript.

Le moteur peut être en Python car son domaine principal est :

- statistiques ;
- psychométrie ;
- machine learning ;
- optimisation ;
- traitement de données ;
- embeddings ;
- graphes ;
- expérimentation scientifique.

Stack initiale recommandée :

- Python ;
- FastAPI ;
- Pydantic ;
- NumPy ;
- SciPy ;
- pandas ;
- scikit-learn.

À ajouter uniquement lorsque le besoin est démontré :

- PyTorch ;
- sentence-transformers ;
- PyTorch Geometric ;
- NetworkX ;
- FAISS ou pgvector ;
- LightGBM ;
- Neo4j.

**Ne pas installer toute la stack dès V1.**

## 4. Contrat entre Otheloo et le moteur

Le moteur ne doit pas dépendre directement des tables Prisma d'Otheloo.

Otheloo transforme ses données internes en un contrat stable.

Exemple conceptuel :

    POST /v1/orientation/profile
    POST /v1/orientation/assessments
    POST /v1/orientation/recommendations
    POST /v1/orientation/feedback
    GET  /v1/orientation/profile/{studentId}

Le moteur reçoit un profil normalisé et renvoie des résultats versionnés.

Exemple de résultat conceptuel :

    {
      direction,
      confidence,
      evidence,
      skillsToExplore,
      explorationIdeas,
      uncertainty,
      modelVersion,
      knowledgeVersion
    }

Le contrat réel devra être défini avec OpenAPI et versionné.

## 5. Identité et confidentialité

Le moteur ne doit pas recevoir plus de données que nécessaire.

À privilégier :

- identifiant technique pseudonymisé ;
- données strictement nécessaires au calcul ;
- séparation entre identité Otheloo et données ML ;
- chiffrement en transit ;
- secrets hors code ;
- journalisation contrôlée ;
- suppression ou anonymisation des données expérimentales selon la politique de conservation.

Ne jamais envoyer dans un dataset d'entraînement :

- mot de passe ;
- token ;
- secret ;
- données personnelles inutiles ;
- données scolaires non nécessaires ;
- identifiants directement exploitables.

Les données de mineurs nécessitent une attention particulière : finalité, minimisation, accès, conservation, consentement et obligations légales doivent être traités avant tout entraînement réel.

## 6. Le moteur n'est pas un modèle unique

L'architecture cible est un pipeline hybride :

    Profil
       ↓
    validation
       ↓
    psychométrie / transformation
       ↓
    règles de sécurité
       ↓
    génération des candidats
       ↓
    scoring
       ↓
    semantic matching
       ↓
    Knowledge Graph
       ↓
    skill matching
       ↓
    ranking
       ↓
    diversification
       ↓
    explication
       ↓
    exploration
       ↓
    feedback
       ↓
    mise à jour du profil

Chaque bloc doit avoir une responsabilité claire.

## 7. Ordre obligatoire de construction

Ne pas commencer par un réseau neuronal.

Ordre recommandé :

### Étape 0 — Contrats et sécurité

Définir :

- schéma du profil ;
- schéma des évaluations ;
- schéma des directions ;
- schéma du feedback ;
- versionnement ;
- règles de sécurité ;
- journal d'audit.

### Étape 1 — Baseline déterministe

Construire :

- règles ;
- normalisation ;
- scoring pondéré ;
- filtrage ;
- diversification ;
- explications.

Cette version doit être entièrement reproductible.

### Étape 2 — Knowledge Graph

Intégrer :

- ESCO ;
- O*NET ;
- compétences ;
- connaissances ;
- professions ;
- formations ;
- relations.

Puis ajouter progressivement les données locales réellement disponibles.

### Étape 3 — Matching sémantique

Ajouter si nécessaire :

- embeddings ;
- recherche vectorielle ;
- similarité sémantique.

Comparer systématiquement au baseline.

### Étape 4 — Ranking appris

Quand un volume de données suffisant existe :

- learning-to-rank ;
- LambdaMART ou autre modèle adapté ;
- validation hors ligne ;
- calibration ;
- audit fairness.

### Étape 5 — Apprentissage longitudinal

Ajouter :

- feedback explicite ;
- historique d'exploration ;
- mise à jour bayésienne ;
- évolution des intérêts ;
- évolution des compétences ;
- évolution de la confiance.

### Étape 6 — Exploration adaptative

Tester :

- Thompson Sampling ;
- LinUCB ;
- UCB.

Uniquement pour choisir des **explorations réversibles et à faible risque**, jamais pour décider automatiquement de la trajectoire scolaire d'un élève.

### Étape 7 — Modèles avancés

Seulement si les données le justifient :

- graph embeddings ;
- GraphSAGE ;
- GAT ;
- R-GCN ;
- modèles multi-objectifs.

## 8. Données : il n'existe pas de dataset unique suffisant

Le moteur ne doit pas chercher un « dataset magique » contenant toute la relation :

    élève → profil → métier réussi

Ce dataset n'est pas le socle réaliste du projet.

Il faut construire plusieurs couches de données.

### 8.1 Données de connaissance

#### ESCO

ESCO constitue une source majeure pour :

- professions ;
- compétences ;
- connaissances ;
- relations entre professions et compétences ;
- classification multilingue.

La documentation de recherche du projet référence ESCO v1.2.1.

ESCO sert principalement de **Knowledge Base**, pas de dataset d'entraînement de notre modèle étudiant.

#### O*NET

O*NET apporte notamment :

- intérêts professionnels ;
- capacités ;
- compétences ;
- connaissances ;
- styles de travail ;
- éducation ;
- expérience ;
- activités et contexte du travail.

O*NET complète donc ESCO.

### 8.2 Données locales

Il faudra progressivement ajouter, selon disponibilité et droit d'utilisation :

- formations accessibles ;
- établissements ;
- diplômes ;
- conditions d'admission ;
- durée ;
- coût ;
- localisation ;
- langues ;
- opportunités ;
- concours ;
- stages ;
- emplois ;
- contexte du marché du travail.

Une profession peut être compatible avec un profil sans être immédiatement accessible à l'élève.

Le moteur doit séparer :

    compatibilité
    accessibilité
    connaissance
    opportunité

### 8.3 Données propriétaires Otheloo

La donnée la plus stratégique viendra progressivement du fonctionnement réel du produit :

    profil
       ↓
    hypothèses
       ↓
    directions proposées
       ↓
    exploration
       ↓
    réaction
       ↓
    feedback
       ↓
    nouvelle observation
       ↓
    profil mis à jour

Exemples de signaux :

- réponse à un questionnaire ;
- intérêt déclaré ;
- compétence évaluée ;
- activité réalisée ;
- feedback après exploration ;
- direction rejetée ;
- direction demandée ;
- évolution d'une confiance ;
- évolution d'un intérêt.

Ces données doivent être collectées avec une finalité claire et une politique de confidentialité adaptée.

## 9. Ne pas confondre Knowledge Base et training dataset

ESCO et O*NET peuvent alimenter le graphe et les représentations.

Ils ne permettent pas à eux seuls d'entraîner un modèle à prédire :

    « ce profil d'élève doit recevoir cette direction ».

Au début, il n'y aura probablement pas de ground truth fiable.

Il faut donc commencer par des baselines explicables et construire progressivement des données d'évaluation.

Le métier finalement choisi ne doit pas être considéré comme l'unique vérité.

Un élève peut :

- changer de voie ;
- explorer plusieurs domaines ;
- réussir dans plusieurs directions ;
- découvrir tardivement un intérêt ;
- choisir une voie pour des raisons qui ne sont pas capturées par le modèle.

## 10. Structure de données recommandée

Chaque signal important doit pouvoir conserver :

    value
    confidence
    source
    timestamp
    version

Exemple :

    interest.science
      value: 0.82
      confidence: 0.76
      source: questionnaire_v2
      timestamp: ...

Les compétences doivent distinguer au minimum :

- déclarée ;
- observée ;
- évaluée ;
- inférée.

Ne pas mélanger ces quatre niveaux.

## 11. Règles strictes du moteur

### Règle 1 — Ne jamais imposer un métier

Le système propose des directions à explorer.

Il ne dit pas :

    « Tu dois devenir X. »

### Règle 2 — Ne jamais fermer une voie automatiquement

Une faible compatibilité actuelle ne signifie pas :

    « impossible ».

### Règle 3 — Ne jamais prédire l'échec d'un enfant

Le système ne doit pas transformer des notes, comportements ou profils en verdict d'avenir.

### Règle 4 — Ne pas transformer un score en identité

Un score est un signal dans un contexte donné.

Il ne définit pas l'enfant.

### Règle 5 — Compatibilité ≠ accessibilité

Une recommandation doit pouvoir distinguer :

- intérêt ;
- compatibilité ;
- compétences à renforcer ;
- accessibilité ;
- opportunités.

### Règle 6 — Toujours conserver l'incertitude

Chaque recommandation importante doit pouvoir indiquer :

- ce qui la soutient ;
- ce qui est incertain ;
- ce qui pourrait modifier l'analyse.

### Règle 7 — Diversifier

Ne pas recommander uniquement des variantes du même métier.

Le moteur doit maintenir plusieurs hypothèses réellement différentes.

### Règle 8 — L'exploration sert à apprendre

Une activité proposée peut avoir deux objectifs :

    découvrir une voie
    +
    obtenir de nouvelles informations sur le profil

### Règle 9 — Le feedback n'est pas une vérité absolue

« Je n'aime pas » est un signal.

Il doit être interprété avec :

- contexte ;
- moment ;
- confiance ;
- historique ;
- autres observations.

### Règle 10 — Ne pas optimiser uniquement le clic

Le moteur ne doit pas apprendre :

    « ce qui génère le plus de clics »

comme objectif unique.

Il faut distinguer :

- engagement ;
- information gagnée ;
- utilité ;
- satisfaction ;
- clarté du profil ;
- agency ;
- qualité de l'exploration.

### Règle 11 — Pas de variable protégée dans le score sans justification

Pour chaque variable sensible :

    modèle ?
    audit ?
    interdite ?
    contrainte légale ?

Une variable peut être utilisée pour auditer un biais sans être utilisée pour calculer une recommandation.

### Règle 12 — Les décisions importantes restent humaines

Le moteur fournit :

- hypothèses ;
- informations ;
- pistes ;
- expériences ;
- explications.

Il ne prend pas seul une décision importante concernant l'élève.

## 12. Règles de recommandation

Une direction peut être évaluée avec un score conceptuel :

    S(d|p) =
        wI * InterestFit
      + wA * AbilityFit
      + wS * SkillFit
      + wV * ValueFit
      + wE * EnvironmentFit
      + wT * TrajectoryFit
      + wC * Confidence
      + wAd * AdaptabilityCompatibility
      - wG * SkillGapPenalty

Les poids initiaux sont des paramètres expérimentaux.

Ils ne doivent pas être présentés comme scientifiquement optimaux sans validation.

Les signaux incertains doivent contribuer avec leur niveau de confiance.

Conceptuellement :

    effectiveWeight = weight × confidence

Le score ne doit pas être présenté comme une probabilité si aucune calibration statistique ne le justifie.

## 13. Diversification

Après le classement, appliquer une diversification.

Principe :

    pertinence
    -
    similarité avec ce qui est déjà sélectionné

L'objectif est d'éviter :

    data analyst
    data scientist
    machine learning engineer
    data engineer
    ...

si le moteur prétend présenter cinq directions différentes.

La diversification doit favoriser l'exploration de plusieurs hypothèses.

## 14. Explication obligatoire

Chaque recommandation doit pouvoir répondre :

### Pourquoi ?

Quels éléments du profil la soutiennent ?

### Quoi explorer ?

Quelle activité peut tester l'hypothèse ?

### Quelles compétences renforcer ?

Quels écarts sont identifiés ?

### Qu'est-ce qui est incertain ?

Quelles informations manquent ?

### Qu'est-ce qui pourrait changer le résultat ?

Présenter des explications déterministes issues des calculs.

Un LLM peut éventuellement reformuler une explication déjà calculée, mais il ne doit pas devenir le moteur caché du classement.

## 15. Apprentissage longitudinal

Le système doit chercher à mieux comprendre l'élève dans le temps.

Boucle :

    observation
       ↓
    profil
       ↓
    hypothèses
       ↓
    exploration
       ↓
    feedback
       ↓
    mise à jour
       ↓
    nouvelles hypothèses

Exemple :

    intérêt initial : robotique faible
    ↓
    mini-projet robotique
    ↓
    intérêt déclaré élevé
    ↓
    confiance scientifique en hausse
    ↓
    nouveau signal
    ↓
    nouvelles directions

L'objectif n'est pas seulement de prédire une préférence.

L'objectif est aussi de **réduire progressivement l'incertitude sur le profil**.

## 16. Contextual bandit : rôle limité

Un contextual bandit peut être utilisé plus tard pour choisir quelle exploration proposer.

Exemple :

    profil actuel
       ↓
    plusieurs explorations possibles
       ↓
    choix d'une exploration
       ↓
    résultat
       ↓
    mise à jour

Il ne doit pas choisir directement :

    « métier final de l'élève »

Les expérimentations doivent être :

- réversibles ;
- peu risquées ;
- explicables ;
- évaluées hors ligne avant déploiement.

Avant utilisation réelle, prévoir notamment :

- replay ;
- inverse propensity scoring ;
- doubly robust estimation ;
- simulation.

## 17. Versionnement obligatoire

Une recommandation doit être reproductible.

Conserver :

    profileVersion
    modelVersion
    knowledgeVersion
    questionnaireVersion
    inputSnapshot
    candidateSet
    ranking
    evidence
    timestamp

Un changement d'algorithme doit produire une nouvelle version.

Ne jamais écraser silencieusement un modèle utilisé auparavant.

## 18. Tests obligatoires

### Unit tests

Tester :

- normalisation ;
- formules ;
- scoring ;
- règles ;
- diversification ;
- transformations.

### Contract tests

Tester :

- API ;
- schémas ;
- compatibilité Node.js ↔ Python.

### Integration tests

Tester :

    profil → recommandation → explication

### Regression tests

Conserver des profils de référence.

Un changement de code ne doit pas modifier silencieusement les résultats attendus sans raison documentée.

### Property-based tests

Tester les propriétés mathématiques importantes.

### Fairness tests

Utiliser des jeux synthétiques puis des données autorisées.

### Model evaluation

Comparer chaque nouveau modèle aux baselines.

## 19. Critères pour passer à l'étape suivante

Une technologie plus complexe ne doit être adoptée que si elle apporte un gain mesurable.

Comparer :

    baseline
       vs
    nouveau modèle

sur :

- Precision@K ;
- Recall@K ;
- NDCG@K ;
- MAP ;
- couverture ;
- diversité ;
- calibration ;
- explicabilité ;
- fairness ;
- clarté du profil ;
- sentiment d'agence ;
- utilité ;
- satisfaction ;
- qualité de l'exploration.

Si le modèle avancé n'améliore pas suffisamment ces critères, conserver le modèle plus simple.

## 20. Structure recommandée du dépôt

    otheloo-orientation-engine/
    ├── README.md
    ├── pyproject.toml
    ├── Dockerfile
    ├── docker-compose.yml
    ├── src/
    │   └── orientation/
    │       ├── api/
    │       ├── profile/
    │       ├── assessments/
    │       ├── psychometrics/
    │       ├── knowledge/
    │       │   ├── esco/
    │       │   ├── onet/
    │       │   └── graph/
    │       ├── recommendation/
    │       │   ├── rules/
    │       │   ├── scoring/
    │       │   ├── similarity/
    │       │   ├── ranking/
    │       │   └── diversification/
    │       ├── learning/
    │       │   ├── feedback/
    │       │   ├── bayesian/
    │       │   └── exploration/
    │       ├── explanation/
    │       └── evaluation/
    ├── data/
    │   ├── raw/
    │   ├── processed/
    │   └── README.md
    ├── models/
    ├── tests/
    └── docs/

Les données brutes externes et les données élèves ne doivent pas être versionnées dans Git si elles contiennent des données personnelles ou si leur licence l'interdit.

## 21. Microservices : quand découper réellement ?

### Au début

    Otheloo
       ↓
    Orientation Engine
       ├── profile
       ├── assessment
       ├── recommendation
       ├── graph
       ├── learning
       └── explanation

Un seul service.

### Plus tard

Découper seulement si une raison existe.

Exemple :

    Otheloo
       ↓
    Orientation API
       ├── Recommendation Service
       ├── Knowledge Service
       └── Training / Evaluation Workers

Les workers peuvent traiter :

- recalculs ;
- embeddings ;
- entraînement ;
- évaluations ;
- import de données.

Le découpage doit répondre à un problème réel et non à une préférence architecturale.

## 22. Communication

V1 :

    REST + JSON

Plus tard, si nécessaire :

- gRPC pour appels internes à fort volume ;
- queue/event bus pour traitements asynchrones ;
- batch jobs pour entraînement et recalculs.

Le moteur ne doit pas bloquer une requête utilisateur pendant un entraînement lourd.

## 23. Entraînement et production

Séparer :

    online inference
    ≠
    offline training

Architecture conceptuelle :

    Otheloo
       ↓
    événements anonymisés/pseudonymisés
       ↓
    data pipeline
       ↓
    dataset versionné
       ↓
    entraînement
       ↓
    validation
       ↓
    modèle approuvé
       ↓
    registry
       ↓
    production

Un modèle expérimental ne doit pas devenir automatiquement le modèle de production.

## 24. Gouvernance des datasets

Pour chaque dataset conserver :

    datasetId
    version
    source
    licence
    dateImport
    transformation
    features
    exclusions
    population
    limites
    checksum si applicable

Pour chaque dataset d'élèves :

- finalité ;
- base légale applicable ;
- politique d'accès ;
- durée de conservation ;
- anonymisation/pseudonymisation ;
- procédure de suppression ;
- journal des usages.

## 25. Stratégie de données recommandée

### Phase A

Pas d'entraînement complexe.

Construire :

    ESCO
    +
    O*NET
    +
    règles
    +
    scoring
    +
    graphe
    +
    explications

### Phase B

Collecter des feedbacks structurés :

    pertinent
    pas pertinent
    intéressant
    pas intéressé
    déjà exploré
    je veux en savoir plus
    je ne comprends pas pourquoi

### Phase C

Construire des datasets d'évaluation.

Exemple :

    profile
    candidateDirections
    studentFeedback
    explorationOutcome
    timestamp

### Phase D

Apprendre le ranking.

### Phase E

Apprendre l'exploration.

### Phase F

Tester les modèles avancés uniquement si le volume et la qualité des données le justifient.

## 26. Ce qu'il ne faut pas faire

Ne pas :

- entraîner un gros modèle dès le début ;
- appeler ESCO un dataset d'entraînement d'élèves ;
- utiliser le métier finalement choisi comme vérité absolue ;
- optimiser uniquement les clics ;
- utiliser un LLM comme juge caché ;
- lancer un bandit sans évaluation offline ;
- déployer une GNN sans volume de données suffisant ;
- créer dix microservices avant d'avoir un problème de scalabilité ;
- mélanger les données personnelles Otheloo avec des datasets publics ;
- afficher un score comme une probabilité sans calibration ;
- supprimer les traces de version d'un modèle ;
- fermer une voie à cause d'un score faible ;
- présenter les résultats expérimentaux comme des faits scientifiques établis.

## 27. Architecture cible finale

    ┌──────────────────────────────┐
    │          Otheloo             │
    │ React + Node.js / TypeScript │
    └──────────────┬───────────────┘
                   │
                   │ REST
                   ▼
    ┌──────────────────────────────┐
    │   Orientation Engine         │
    │   Python + FastAPI           │
    ├──────────────────────────────┤
    │ Profile                      │
    │ Assessments                  │
    │ Psychometrics                │
    │ Rules                        │
    │ Scoring                      │
    │ Semantic Matching            │
    │ Knowledge Graph              │
    │ Ranking                      │
    │ Diversification              │
    │ Explanation                  │
    │ Feedback                     │
    │ Longitudinal Learning        │
    │ Evaluation                   │
    └──────────────┬───────────────┘
                   │
          ┌────────┼─────────┐
          ▼        ▼         ▼
        ESCO     O*NET    Local data
          │        │         │
          └────────┼─────────┘
                   ▼
            Knowledge Base
                   │
                   ▼
            Recommendation
                   │
                   ▼
             Exploration
                   │
                   ▼
               Feedback
                   │
                   ▼
            Learning Loop

## 28. Règle directrice du projet

Le moteur ne doit pas chercher à « deviner le métier de l'enfant ».

Il doit chercher à :

1. mieux comprendre progressivement l'élève ;
2. représenter ce qu'il sait et ce qu'il ne sait pas encore ;
3. générer plusieurs hypothèses ;
4. expliquer ces hypothèses ;
5. proposer des explorations ;
6. apprendre des retours ;
7. réduire progressivement l'incertitude ;
8. préserver la liberté de décision de l'élève, de sa famille et des professionnels qui l'accompagnent.

Cette règle doit rester la référence de toute évolution future du moteur.
