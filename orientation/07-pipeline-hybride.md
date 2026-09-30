# Pipeline hybride de recommandation

## Niveau 0 — collecte

Sources :

- profil ;
- résultats ;
- trajectoire ;
- questionnaires ;
- expériences ;
- feedback ;
- référentiels ;
- formations ;
- opportunités.

## Niveau 1 — contraintes dures

Filtrer seulement les impossibilités objectives :

- prérequis obligatoires ;
- réglementation ;
- disponibilité ;
- contraintes explicitement demandées.

Une contrainte administrative n'est pas un jugement sur le potentiel.

## Niveau 2 — compatibilité

Calculer :

- intérêts ;
- aptitudes ;
- compétences ;
- valeurs ;
- environnement ;
- trajectoire ;
- auto-efficacité ;
- adaptabilité.

## Niveau 3 — sémantique

Encoder les descriptions et profils.

    profileEmbedding ↔ directionEmbedding

Cosine ou recherche vectorielle.

## Niveau 4 — graphe

Rechercher des chemins :

    profil → skill → training → direction

## Niveau 5 — ranking

Apprendre progressivement à ordonner les directions lorsque suffisamment de données existent.

## Niveau 6 — diversification

Appliquer MMR ou équivalent.

Une liste de cinq éléments doit réellement représenter plusieurs possibilités.

## Niveau 7 — explication

Chaque résultat contient :

- pourquoi ;
- forces ;
- incertitudes ;
- skill gaps ;
- expériences ;
- contre-factuels.

## Niveau 8 — feedback

Actions :

- confirmer ;
- contester ;
- explorer ;
- ignorer ;
- terminer ;
- modifier une préférence.

## Pipeline global

    INPUT
      ↓
    VALIDATION
      ↓
    HARD CONSTRAINTS
      ↓
    PROFILE REPRESENTATION
      ↓
    RULES + SCORING
      ↓
    SEMANTIC RETRIEVAL
      ↓
    GRAPH REASONING
      ↓
    RANKING
      ↓
    DIVERSIFICATION
      ↓
    EXPLANATION
      ↓
    EXPLORATION
      ↓
    FEEDBACK
      ↓
    LEARNING

## Pourquoi hybride ?

- règles = transparence ;
- scoring = contrôle ;
- embeddings = sémantique ;
- graphe = relations ;
- ranking = apprentissage du classement ;
- bandit = exploration ;
- humain = décision.
