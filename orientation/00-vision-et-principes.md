# Otheloo Orientation Engine — Vision et principes

## Mission

Otheloo ne doit pas répondre « quel métier dois-tu faire ? ».

Il doit construire progressivement une compréhension multidimensionnelle de l'élève et transformer cette compréhension en **directions d'exploration**, accompagnées de preuves, d'incertitudes, de compétences à renforcer et d'expériences permettant d'apprendre davantage.

La boucle fondamentale est :

    observer → mesurer → profiler → hypothétiser → explorer → recevoir du feedback → mettre à jour → recommencer

## Sortie cible

### Profil

Exemple : **Investigateur–Social**

- intérêt élevé pour comprendre les systèmes ;
- goût pour la résolution de problèmes ;
- intérêt élevé pour l'aide aux autres ;
- progression régulière en sciences ;
- curiosité élevée ;
- auto-efficacité mathématique moyenne mais en progression.

### Directions

- sciences et santé ;
- ingénierie et technologies ;
- informatique et données ;
- recherche ;
- enseignement scientifique.

### Pourquoi ?

Chaque direction doit expliquer ses contributions :

- intérêts ;
- aptitudes ;
- compétences ;
- valeurs ;
- environnement préféré ;
- trajectoire scolaire ;
- expériences ;
- incertitudes.

### Comment progresser ?

Le moteur doit proposer :

- compétences à renforcer ;
- expériences à essayer ;
- questions restant ouvertes ;
- informations susceptibles de modifier l'analyse.

## Principes non négociables

1. Pas de verdict professionnel.
2. Pas d'exclusion automatique.
3. Pas de score affiché sans définition.
4. Toute direction doit être explicable.
5. L'incertitude doit être visible.
6. Le profil évolue dans le temps.
7. Une déclaration n'est pas une vérité absolue.
8. Une note scolaire est un signal parmi d'autres.
9. Les algorithmes complexes doivent être comparés à des baselines simples.
10. Les modèles, questionnaires et référentiels sont versionnés.
11. Le système doit augmenter l'autonomie de l'élève.
12. Le système doit augmenter l'espace des possibles, pas le réduire.

## Ce que signifie « apprendre »

Le moteur n'apprend pas seulement « ce que l'élève clique ».

Il apprend quelles hypothèses sur son profil sont :

- confirmées ;
- infirmées ;
- nouvelles ;
- incertaines.

Une expérience peut donc être utile même si l'élève n'aime pas l'activité : elle réduit une incertitude.

## Architecture conceptuelle

    profil longitudinal
           ↓
    moteur de compatibilité
           ↓
    graphe compétences/formations/directions
           ↓
    ranking + diversification
           ↓
    explication
           ↓
    exploration
           ↓
    feedback
           ↓
    apprentissage longitudinal

## État produit

La documentation produit actuelle d'Otheloo décrit l'orientation comme un axe de feuille de route et parle de portrait de l'élève, résultats, assiduité, comportement, goûts, filières, concours et formations. Ce dossier formalise l'architecture de recherche à construire ; il ne doit pas être lu comme la preuve que toutes ces briques algorithmiques existent déjà en production.
