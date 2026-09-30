# Catalogue des algorithmes possibles

## Niveau 1 — règles

Avantages :

- transparence ;
- audit ;
- tests simples.

Limites :

- rigidité ;
- maintenance ;
- biais de conception.

À conserver comme baseline.

## Niveau 2 — scoring pondéré

Très bon premier moteur de compatibilité.

Il permet de montrer exactement la contribution des dimensions.

## Niveau 3 — similarité

Méthodes :

- cosine ;
- euclidienne ;
- Mahalanobis ;
- distances pondérées.

## Niveau 4 — kNN

Chercher des profils ou trajectoires comparables.

Attention :

    profils similaires ≠ futurs identiques

Utiliser kNN pour enrichir l'exploration, pas pour imposer un résultat.

## Niveau 5 — matrix factorization

Utile pour les matrices :

    élève × activité
    élève × direction
    élève × exploration

Problème : cold start.

## Niveau 6 — embeddings

Encoder :

- compétences ;
- formations ;
- descriptions ;
- activités ;
- directions.

Puis recherche vectorielle.

## Niveau 7 — Knowledge Graph

Relations explicites :

    élève → compétence → formation → direction

Avantages :

- raisonnement par chemin ;
- explications ;
- intégration de référentiels.

## Niveau 8 — Graph embeddings

Possibilités :

- Node2Vec ;
- DeepWalk ;
- TransE ;
- RotatE.

## Niveau 9 — GNN

Possibilités :

- GraphSAGE ;
- GAT ;
- R-GCN.

Ne pas commencer ici.

Il faut démontrer :

    baseline → graphe → GNN

avec un gain mesuré.

## Niveau 10 — Learning-to-Rank

Familles :

- pointwise ;
- pairwise ;
- listwise ;
- LambdaMART ;
- modèles neuronaux.

Objectif :

    ordonner les directions à explorer

et non :

    prédire une profession.

## Niveau 11 — Bayesian

Chaque hypothèse possède :

- croyance ;
- incertitude ;
- historique.

## Niveau 12 — contextual bandits

Contexte :

    x_t = profil actuel

Action :

    a_t = expérience proposée

Feedback :

    r_t = valeur d'apprentissage

## LinUCB

    a_t = argmax_a [
      θ̂_a^T x_t
      + α sqrt(x_t^T A_a^-1 x_t)
    ]

## Thompson Sampling

    θ_a ~ P(θ_a | D)

puis :

    a = argmax_a x^T θ_a

## UCB

    UCB = μ̂ + α sqrt(ln(t)/n_a)

## Epsilon-greedy

    exploration avec probabilité ε

Très simple, utile comme baseline.

## Niveau 13 — système hybride

Architecture cible :

    hard constraints
       ↓
    rules
       ↓
    skill gap
       ↓
    semantic retrieval
       ↓
    graph reasoning
       ↓
    learning-to-rank
       ↓
    diversification
       ↓
    explanation
       ↓
    exploration

## Ordre de construction

    V1 règles
    V2 scoring
    V3 graphe + sémantique
    V4 ranking
    V5 apprentissage longitudinal
    V6 bandits d'exploration
    V7 GNN si justifié

Le modèle le plus complexe n'est jamais automatiquement le meilleur.
