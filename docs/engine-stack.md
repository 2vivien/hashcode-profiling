# Pile de recommandation : ce qui tourne, et ce qui ne tourne pas

## Pourquoi cette page existe

Le dépôt contenait V1 (déterministe), V3 (LambdaMART), V4 (bandits), V5 (R-GCN),
la calibration et l'équité — **écrits, testés unitairement, et jamais reliés au
chemin de requête**. Le `model_registry` ne contenait qu'une seule ligne, le
baseline. Le risque n'était pas un modèle faux : c'était un dépôt qui laisse
croire qu'il y en a six.

La pile rend cette situation visible à chaque requête.

## Le principe

Chaque couche est **indépendante et rapportable**. Elle s'active seulement si son
artefact existe, et sinon elle dit pourquoi elle n'a pas joué.

```
Recommandation
   └─ RecommendationStack.apply(...)
        ├─ calibration  ← artifact « calibration »
        ├─ ranking      ← artifact « lamdamart »
        ├─ graph        ← artifact « rgcn »
        ├─ bandit       ← artifact « bandit » + exploration autorisée
        └─ fairness     ← statistique de genre du ROME (mesure, pas feature)
```

Réponse réelle en production aujourd'hui :

```
model_version : deterministic-baseline-v1
 [inactif] calibration  aucun calibrateur entraîné
 [inactif] ranking      aucun modèle LambdaMART entraîné : l'ordre déterministe est conservé
 [inactif] graph        aucun R-GCN entraîné
 [inactif] bandit       aucun bandit entraîné : pas d'exploration
 [inactif] fairness     donnée de genre de marché inconnue pour ces directions
```

C'est la vérité. Le jour où un modèle est entraîné, la ligne bascule et
`model_version` devient `deterministic-baseline-v1+ranking`.

## Artefacts de modèle

Un modèle appris est un **résultat reproductible**, pas du code : il vit dans
`data/runtime/models/<tâche>.json` avec un `<tâche>.meta.json` (version, date,
taille d'échantillon, métriques, version de connaissance).

```
engine/registry.py   → ModelRegistry : découverte, métadonnées, inscription
engine/stack.py      → RecommendationStack, FairnessGuard, LayerOutcome
```

Une couche est inactivée si l'artefact est absent, et la calibration exige en
outre **au moins 20 observations alignées** — en dessous, elle se déclare
inactive plutôt que de produire une probabilité inventée.

## Équité : ce qui est mesuré, et ce qui ne l'est pas

Le ROME publie la répartition de genre **par métier**. C'est une statistique de
marché, pas une caractéristique de la personne. L'utiliser comme feature de
scoring discriminerait ; le code l'interdit par construction :

- `FairnessGuard` **ne lit que** le genre des métiers ;
- il agit par **pondération symétrique** sur la fréquence de sortie, jamais sur
  le score d'un élève ;
- sans donnée disponible, il se déclare **inactif** — se dire « actif » sans
  avoir rien mesuré serait une fausse garantie ;
- le genre de l'élève n'entre nulle part dans le calcul.

## Psychométrie branchée

L'évaluation V1 faisait de l'agrégation heuristique : des moyennes de valeurs
auto-déclarées. `psychometrics/bridge.py` la relie au MIRT 2PL :

- **banque calibrée** → niveaux latents + erreur standard ;
- **banque absente** (notre cas) → `method: "heuristic-mean"`, `calibrated: false`,
  `standard_error: null`. Le client sait qu'il n'a pas une mesure, il a une moyenne.

Endpoint : `POST /v1/orientation/assessment-v1/ability`

```
{"ability": {"method": "heuristic-mean", "calibrated": false, "information": 0.0},
 "theta": {"realistic": 0.119, "social": 0.5, ...},
 "standard_error": {"realistic": null, ...},
 "items_used": 3}
```

**Réserve assumée** : l'IRT implémenté prend une difficulté **scalaire** par item,
nous moyennons donc les difficultés par dimension. Ce n'est pas un modèle
vectoriel complet.

## Traçabilité

L'état des couches est écrit dans `audit_event.detail.layers` : on peut, six mois
plus tard, dire qu'une recommandation donnée a été produite **sans** LambdaMART.

## Ce qui reste à faire, et ce qui bloque

| Couche | Manque | Pourquoi |
|---|---|---|
| calibration | ≥ 20 observations étiquetées | 2 feedbacks en base |
| LambdaMART | jeu de requêtes + clics | aucune interaction enregistrée |
| R-GCN | graphe + labels d'arêtes | le graphe existe, les labels non |
| bandit | trafic + feedback | exploration risquée sans volume |

Le code est prêt ; ce qui manque n'est pas du développement, c'est de la donnée
d'usage. Un moteur d'orientation ne peut pas s'évaluer sans élèves qui l'utilisent.