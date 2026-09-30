# Otheloo — Documentation du moteur d'orientation

Cette documentation décrit la conception scientifique, mathématique, algorithmique et technique du futur moteur d'orientation Otheloo.

## Idée centrale

Otheloo ne doit pas recommander un métier unique.

Le moteur doit construire un **profil multidimensionnel et évolutif**, puis présenter plusieurs **directions à explorer**, avec :

- pourquoi elles apparaissent ;
- les éléments du profil qui les soutiennent ;
- les incertitudes ;
- les compétences à renforcer ;
- les expériences permettant de tester les hypothèses ;
- le feedback permettant de mettre à jour le profil.

## Parcours

1. [Vision et principes](./00-vision-et-principes.md)
2. [Fondements scientifiques](./01-fondements-scientifiques.md)
3. [Modèle du profil](./02-modele-profil.md)
4. [Psychométrie IRT/MIRT/CAT](./03-psychometrie-irt-cat.md)
5. [Mathématiques du moteur](./04-mathematiques-du-moteur.md)
6. [Catalogue des algorithmes](./05-catalogue-algorithmes.md)
7. [Knowledge Graph](./06-knowledge-graph.md)
8. [Pipeline hybride](./07-pipeline-hybride.md)
9. [Apprentissage longitudinal](./08-apprentissage-longitudinal.md)
10. [Explicabilité](./09-explicabilite.md)
11. [Fairness et sécurité](./10-fairness-securite.md)
12. [Validation et benchmark](./11-validation-benchmark.md)
13. [Schéma de données](./12-schema-donnees.md)
14. [Architecture technique](./13-architecture-technique.md)
15. [Roadmap V1–V7](./14-roadmap-v1-v7.md)
16. [État de l'art](./15-recherche-etat-de-l-art.md)
17. [Exemple produit](./16-exemple-produit.md)
18. [Bibliographie](./17-bibliographie.md)
19. [Industrialisation, microservices, données et règles](./18-industrialisation-microservices-donnees-regles.md)

## Architecture cible

    Données élève
       ↓
    Profil longitudinal
       ↓
    Psychométrie + trajectoire
       ↓
    Rules / scoring
       ↓
    Semantic matching
       ↓
    Knowledge Graph
       ↓
    Learning-to-Rank
       ↓
    Diversification
       ↓
    Explication
       ↓
    Expériences d'exploration
       ↓
    Feedback
       ↓
    Mise à jour du profil

## Algorithmes couverts

- règles expertes ;
- scoring multicritère ;
- cosine similarity ;
- distances euclidiennes ;
- distance de Mahalanobis ;
- régression de tendance ;
- variance, volatilité et vélocité ;
- entropie ;
- MMR ;
- Bayesian updating ;
- IRT, MIRT et CAT ;
- kNN ;
- matrix factorization ;
- embeddings et vector search ;
- Knowledge Graph ;
- Node2Vec, DeepWalk, TransE ;
- GraphSAGE, GAT, R-GCN ;
- Learning-to-Rank et LambdaMART ;
- contextual bandits ;
- LinUCB ;
- Thompson Sampling ;
- UCB ;
- epsilon-greedy ;
- systèmes hybrides ;
- SHAP ;
- explications contrefactuelles.

## Référentiels

- ESCO ;
- O*NET ;
- référentiels de formation ;
- données locales ;
- opportunités.

## Règle de développement

    règles
      → scoring
      → graphe + sémantique
      → ranking
      → apprentissage longitudinal
      → bandits
      → GNN si justifié

Chaque étape doit être comparée à la précédente.

## Important

Ce dossier est une **documentation de conception et de recherche**. Il ne prétend pas que tous les algorithmes décrits sont déjà implémentés dans Otheloo.

La documentation produit existante reste la source de vérité pour les fonctionnalités effectivement disponibles.
