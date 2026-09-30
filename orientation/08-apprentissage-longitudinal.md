# Apprentissage longitudinal

## Objectif

Le moteur doit apprendre à mieux comprendre l'élève.

Il ne doit pas optimiser uniquement :

    clics
    temps d'écran
    engagement

Il doit rechercher :

    information
    apprentissage
    connaissance de soi
    satisfaction
    agency

## Boucle

    profil
      ↓
    hypothèses
      ↓
    exploration
      ↓
    réaction
      ↓
    observation
      ↓
    mise à jour
      ↓
    nouveau profil

## Feedback explicite

- j'aime ;
- je n'aime pas ;
- je veux explorer ;
- je ne me reconnais pas ;
- trop facile ;
- trop difficile ;
- déjà connu.

## Feedback comportemental

- activité commencée ;
- activité terminée ;
- retour ;
- nouvelle exploration ;
- demande d'information.

Un clic n'est jamais une preuve suffisante d'intérêt professionnel.

## Mise à jour bayésienne

Pour une hypothèse H :

    P(H|D) = P(D|H)P(H) / P(D)

Une expérience modifie progressivement la croyance.

## Décroissance temporelle

Une préférence ancienne peut peser moins qu'une observation récente.

Possible :

    w(t) = exp(-λ Δt)

mais λ doit être validé expérimentalement.

## Contextual bandit

Contexte :

    x_t = profil_t

Action :

    a_t = activité_t

Reward :

    r_t = valeur de l'exploration

Reward conceptuel :

    r =
      a*informationGain
      + b*learningGain
      + c*selfKnowledgeGain
      + d*agency

Le reward ne doit pas être uniquement « clic ».

## Thompson Sampling

    θ_a ~ P(θ_a | D)

Puis :

    a_t = argmax_a x_t^T θ_a

## LinUCB

    UCB_a =
      θ̂_a^T x
      + α sqrt(x^T A_a^-1 x)

## Safe exploration

Le bandit ne peut choisir que des expériences :

- réversibles ;
- pédagogiques ;
- adaptées à l'âge ;
- faibles risques ;
- sans conséquence administrative automatique.

## Cold start

Au début :

    profil pauvre
       ↓
    questionnaire court
       ↓
    quelques explorations
       ↓
    feedback
       ↓
    profil enrichi

Ne jamais prétendre à une grande précision avec très peu de données.

## Apprentissage populationnel

Les paramètres globaux servent d'information auxiliaire.

Ils ne deviennent jamais une définition de l'individu :

    modèle populationnel ≠ destin individuel
