# Explicabilité, skill gaps et contrefactuels

## Question centrale

Chaque direction doit répondre à :

> Pourquoi est-ce que tu me montres ça ?

## Exemple

### Sciences et technologies

**Compatibilité actuelle : forte**  
**Confiance : moyenne**

Pourquoi ?

- intérêt scientifique élevé ;
- curiosité élevée ;
- progression en mathématiques ;
- résolution de problèmes ;
- préférence pour comprendre comment les choses fonctionnent.

À renforcer :

- mathématiques avancées ;
- autonomie ;
- exposition à des projets techniques.

À explorer :

- programmation ;
- robotique ;
- expérimentation ;
- analyse de données.

Incertitudes :

- préférence théorie/pratique ;
- expérience réelle de programmation ;
- persistance sur projet long.

## Contributions

Conserver les contributions internes :

    InterestContribution
    SkillContribution
    ValueContribution
    TrajectoryContribution
    EnvironmentContribution
    GapPenalty
    Uncertainty

## SHAP

SHAP peut expliquer localement certaines prédictions de modèles appris.

Mais :

> expliquer un modèle n'est pas démontrer une causalité.

## Contrefactuels

Si :

    score = f(profile)

chercher une petite modification Δ telle que :

    f(profile + Δ) ≥ seuil

La sortie doit rester une simulation :

> « dans le modèle actuel, cette compétence augmente la compatibilité »

et non :

> « si tu fais cela, tu deviendras X ».

## Skill gap

    G_k = max(0, Required_k - Observed_k)

Afficher :

- compétence ;
- niveau observé ;
- niveau requis ;
- confiance ;
- moyen de progression.

## Le gap n'est pas une faiblesse

Un gap signifie :

> « voici une compétence qui pourrait être développée pour explorer cette direction ».

## Expérience comme preuve

Avant :

    programmation = inconnue

Après un projet :

    projet terminé
    intérêt = 0.80
    confiance = 0.66

La nouvelle observation enrichit le profil.

## Contestabilité

L'élève doit pouvoir dire :

> « Cette analyse ne me ressemble pas. »

Puis indiquer :

- intérêt incorrect ;
- compétence sous-estimée ;
- valeur manquante ;
- expérience oubliée ;
- contexte incorrect.

La contestation devient une donnée de mise à jour.

## Interface

Éviter :

    93,71 %

Préférer :

- forte compatibilité ;
- compatible ;
- à explorer ;
- données insuffisantes.

Les nombres internes peuvent rester disponibles pour l'audit.
