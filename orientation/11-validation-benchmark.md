# Validation scientifique et benchmark

## Baselines

Comparer au minimum :

1. popularité ;
2. règles expertes ;
3. scoring pondéré ;
4. similarité ;
5. graphe ;
6. hybride ;
7. learning-to-rank ;
8. apprentissage longitudinal.

## Precision@K

    Precision@K = pertinents recommandés / K

## Recall@K

    Recall@K = pertinents récupérés / pertinents disponibles

## NDCG@K

Mesure la qualité du classement en pondérant la position.

## MAP

Mesure la précision moyenne sur les positions pertinentes.

## Coverage

Mesurer :

- couverture des directions ;
- couverture des domaines ;
- couverture des profils.

## Diversity

Une liste :

    data
    data science
    data analyst
    data engineering
    machine learning

peut être très peu diversifiée.

## Calibration

Une confiance doit avoir une définition statistique.

Ne jamais afficher une probabilité simplement parce que le modèle produit un nombre entre 0 et 1.

## Métriques humaines

Mesurer :

- clarté du profil ;
- compréhension du pourquoi ;
- sentiment d'agence ;
- utilité ;
- confiance ;
- motivation à explorer ;
- ouverture perçue.

## Métriques longitudinales

- réduction d'incertitude ;
- nouvelles compétences observées ;
- évolution des intérêts ;
- correction des hypothèses ;
- exploration ;
- satisfaction.

## Ground truth

Le métier finalement choisi ne doit pas être l'unique vérité.

Une trajectoire peut changer.

Un élève peut explorer plusieurs domaines et réussir.

## Bandits

Avant déploiement, prévoir :

- inverse propensity scoring ;
- replay ;
- doubly robust estimation ;
- simulation.

## Validation psychométrique

Pour chaque instrument :

- fiabilité ;
- validité ;
- invariance si nécessaire ;
- DIF ;
- population ;
- traduction ;
- conditions d'utilisation.

## Gate

Un modèle avancé ne passe en production que s'il améliore réellement :

    qualité
    calibration
    diversité
    explicabilité
    fairness
    expérience

Sinon le modèle plus simple reste le modèle de référence.
