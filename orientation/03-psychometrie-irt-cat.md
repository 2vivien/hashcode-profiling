# Psychométrie avancée — IRT, MIRT et CAT

## Pourquoi IRT ?

L'Item Response Theory modélise le lien entre un trait latent et la probabilité d'une réponse.

Modèle logistique 2PL :

    P(X_i=1 | θ) = 1 / (1 + exp(-a_i(θ-b_i)))

où :

- θ = niveau latent ;
- a_i = discrimination ;
- b_i = paramètre de localisation/difficulté.

## MIRT

Le profil Otheloo est naturellement multidimensionnel.

On peut représenter :

    θ = [
      Investigative,
      Social,
      Quantitative,
      Creative,
      Autonomy,
      Curiosity,
      ...
    ]

Un item peut charger sur plusieurs dimensions.

## CAT

Computerized Adaptive Testing :

    profil latent courant
          ↓
    sélectionner l'item informatif
          ↓
    réponse
          ↓
    mettre à jour θ
          ↓
    sélectionner le prochain item

L'objectif est de poser moins de questions sans perdre l'information utile.

## Information

Pour une dimension :

    I_i(θ) = E[- ∂² log L_i(θ) / ∂θ²]

Une stratégie peut choisir :

    i* = argmax_i I_i(θ)

Une autre peut maximiser l'information attendue :

    IG(X;Y) = H(X) - H(X|Y)

## Banque d'items

Avant un CAT réel, il faut :

1. banque d'items ;
2. calibration ;
3. paramètres psychométriques ;
4. analyse des items ;
5. contrôle d'exposition ;
6. validation ;
7. surveillance.

## DIF

Le Differential Item Functioning doit être étudié pour vérifier qu'un item ne fonctionne pas différemment entre groupes comparables sur le trait mesuré.

## Stopping rules

Prévoir :

- minimum d'items ;
- maximum d'items ;
- précision cible ;
- couverture de contenu ;
- contraintes d'exposition.

## Principe

Ne jamais appeler « psychométrique » un questionnaire maison simplement parce qu'il produit des nombres.

Pour chaque instrument :

- source ;
- population ;
- fiabilité ;
- validité ;
- traduction ;
- conditions d'utilisation ;
- limites ;
- version.

## Recommandation

Phase initiale :

    questionnaire court + règles + validation

Phase scientifique :

    IRT/MIRT + CAT + validation psychométrique

L'IRT est un outil de mesure ; elle ne décide pas des directions à la place du moteur d'orientation.
