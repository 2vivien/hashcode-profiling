# Knowledge Graph — métiers, formations, compétences et opportunités

## Objectif

Le graphe doit représenter les chemins possibles, pas seulement des catégories.

## Nœuds

    Student
    Interest
    Ability
    Skill
    Knowledge
    Value
    Direction
    Domain
    Training
    Qualification
    Occupation
    Sector
    Opportunity
    Activity
    Institution

## Relations

    HAS_INTEREST
    HAS_SKILL
    HAS_VALUE
    EXPLORED
    COMPLETED
    REQUIRES_SKILL
    RELATED_TO
    DEVELOPS_SKILL
    REQUIRES_PREREQUISITE
    LEADS_TO
    BELONGS_TO
    AVAILABLE_AT
    TESTS
    DEVELOPS

## ESCO

ESCO est un référentiel particulièrement intéressant pour Otheloo : la Commission européenne le décrit comme une classification multilingue des professions, compétences/connaissances et qualifications, conçue pour être exploitable par des systèmes électroniques. Elle peut notamment servir au matching, à l'orientation et à la gestion de l'apprentissage.

La version courante affichée par la Commission européenne est ESCO v1.2.1, mise à jour le 10 décembre 2025.

## O*NET

O*NET apporte une seconde source structurée avec :

- intérêts ;
- capacités ;
- styles de travail ;
- compétences ;
- connaissances ;
- éducation ;
- expérience ;
- activités ;
- contexte de travail.

## Couche de normalisation

Ne pas fusionner aveuglément les référentiels.

Créer :

    OthelooSkill
      ├── escoId?
      ├── onetId?
      ├── localId?
      ├── aliases
      └── version

## Relations métier

Une profession peut avoir :

- compétences essentielles ;
- compétences optionnelles ;
- connaissances ;
- contexte ;
- formations associées.

## Pathfinding

Exemple :

    profil
      ↓
    compétence à renforcer
      ↓
    formation
      ↓
    qualification
      ↓
    direction

Autre possibilité :

    profil
      ↓
    activité
      ↓
    compétence observée
      ↓
    nouvelle hypothèse

## Accessibilité

Séparer :

    compatibilité

de :

    accessibilité

Une direction peut être compatible mais une formation particulière peut être inaccessible à court terme.

Ajouter progressivement :

- pays ;
- région ;
- conditions d'admission ;
- durée ;
- coût ;
- langue ;
- concours ;
- réglementation ;
- disponibilité ;
- opportunités.

## Versioning

Chaque source possède :

- version ;
- date de collecte ;
- source ;
- pays ;
- période de validité.

Une mise à jour d'un référentiel ne doit pas réécrire silencieusement l'historique.
