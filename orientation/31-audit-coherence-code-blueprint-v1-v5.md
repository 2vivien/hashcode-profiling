# Audit de cohérence — Blueprint ↔ code — V1 → V5

Date de l'audit : 2026-10-01

## Référentiel utilisé

La matrice scientifique `orientation/30-matrice-scientifique-v1-v5-donnees-algorithmes.md` est le référentiel canonique pour V1→V5. Les documents historiques V1→V7 restent de la recherche et ne doivent pas contredire les gates de la matrice 30.

Les documents 18, 26, 27, 28 et 29 ont été confrontés à l'arborescence et aux modules du moteur.

## Résultat

### V1 — cohérent et opérationnel

Le chemin de production reste :

`profile → validation → candidate generation → constraints → matching → score → uncertainty → ranking → diversification → explanation → exploration → audit`.

Le baseline déterministe reste le chemin par défaut.

Corrections appliquées pendant cet audit :

- les poids effectifs utilisent réellement `weight × confidence` ;
- une donnée absente n'est plus transformée en score nul par normalisation du dénominateur ;
- les dimensions `Direction` sont maintenant contraintes à [0,1] ;
- l'état d'une compétence est contraint à `declared|observed|assessed|inferred` ;
- les gaps restent des compétences à renforcer et non des impossibilités.

### V2 — code présent, données réelles encore nécessaires

Présent :

- contrats d'ingestion ESCO/O*NET/local ;
- snapshots hashés ;
- provenance ;
- embeddings multilingues ;
- index vectoriel persistant ;
- matching sémantique ;
- abstraction de graphe ;
- validation des mappings.

Point important : l'ingestion actuelle est un adaptateur tabulaire générique. Elle ne constitue pas encore à elle seule un snapshot ESCO/O*NET exhaustif avec toutes les relations sémantiques et tous les fichiers de chaque release. Les vrais exports doivent donc être ingérés puis contrôlés avant de déclarer la Knowledge Base complète.

Sources attendues :

- ESCO v1.2.1 ;
- O*NET 31.0 ;
- catalogues locaux réellement disponibles ;
- mappings locaux revus.

### Psychométrie — mathématique présente, validation scientifique absente

Présent :

- 2PL ;
- information de Fisher ;
- GRM ;
- MIRT ;
- CAT 2PL/MIRT.

Absent par nature tant que les données ne sont pas disponibles :

- banque d'items calibrée ;
- paramètres calibrés sur population ;
- test-retest ;
- DIF ;
- validation de traduction ;
- validation de l'arrêt CAT.

Le code ne doit pas appeler ces briques « validées » avant ces étapes.

### V3 — infrastructure correcte, entraînement dépendant du dataset

Présent :

- LambdaMART/LambdaRank ;
- groupes de requêtes ;
- sauvegarde/chargement ;
- métriques ranking ;
- split groupé temporel ;
- schéma d'événement.

Corrections appliquées :

- le schéma de features de validation est maintenant exactement celui du train ;
- le modèle refuse une matrice de features de dimension différente ;
- les groupes doivent être positifs et leur somme doit correspondre au nombre d'exemples ;
- l'artefact conserve le schéma de features.

Les scores LambdaMART restent des scores de ranking et ne sont pas des probabilités. La documentation LightGBM confirme le rôle de `group` pour les requêtes de ranking et le comportement de prédiction du ranker. 

Il manque encore, par définition :

- dataset Otheloo réel ;
- définition validée des labels ;
- benchmark contre V1/semantic/graph ;
- artefact entraîné ;
- validation indépendante.

### Calibration — correction importante

Avant l'audit, le script pouvait ajuster puis évaluer le calibrateur sur le même fichier.

C'était incompatible avec le blueprint qui exige des données indépendantes.

Correction :

`--fit-input` et `--evaluation-input` sont maintenant obligatoires.

La couche de calibration ne transforme jamais automatiquement un score de compatibilité ou de ranking en probabilité.

### Fairness

Présent :

- demographic parity gap ;
- equal opportunity gap ;
- métriques par groupe.

La fairness reste un audit et non une variable cachée du score de recommandation.

Aucune métrique unique ne doit être utilisée seule pour conclure.

### V4 — infrastructure algorithmique présente

Présent :

- LinUCB ;
- epsilon-greedy ;
- propensité explicite ;
- update ;
- replay ;
- IPS ;
- doubly robust ;
- effective sample size.

La propensité enregistrée est indispensable pour une évaluation offline crédible.

Il manque uniquement les éléments dépendant des données Otheloo :

- vrais logs d'exploration ;
- politique de logging connue ;
- reward validé ;
- replay réel ;
- IPS/DR réel ;
- safety evaluation ;
- rollback produit.

Le bandit ne doit pas devenir un décideur de trajectoire scolaire. Il sert à sélectionner des explorations réversibles.

### V5 — infrastructure graph learning présente

Présent :

- knowledge graph ;
- relations typées ;
- R-GCN ;
- entraînement ;
- prédiction ;
- artefact de poids.

Corrections appliquées :

- validation correcte du nombre d'arêtes ;
- validation des IDs de relations ;
- validation de la forme des features à l'inférence ;
- rejet des graphes de classification à une seule classe ;
- gestion correcte d'un graphe sans relation.

Il manque volontairement :

- graphe Otheloo suffisamment riche ;
- tâche cible définitive ;
- split sans fuite ;
- benchmark V3 vs V5 ;
- poids entraînés sur données réelles.

## Incohérences corrigées

| Zone | Problème | Correction |
|---|---|---|
| Scoring | confidence présente mais normalisation incorrecte | poids effectif = poids × confiance |
| Missing data | absence pouvait réduire artificiellement la compatibilité | absence = incertitude, pas score nul |
| Direction | dimensions non bornées | validation [0,1] |
| Skill state | `status: str` trop permissif | enum `SourceType` |
| LambdaMART | features validation potentiellement dans un ordre différent | schéma train réutilisé |
| LambdaMART | dimensions de features non vérifiées | validation explicite |
| Calibration | fit et évaluation sur les mêmes observations | datasets indépendants obligatoires |
| R-GCN | validation utilisait la mauvaise dimension pour le nombre d'arêtes | `edges.shape[1]` |
| R-GCN | inférence pouvait recevoir un schéma incompatible | validation du schéma |
| R-GCN | graphe mono-classe accepté | rejet explicite |

## Ce qui reste volontairement séparé

Le moteur V1 n'active pas automatiquement V2/V3/V4/V5 en production.

C'est volontaire :

- V1 = baseline déterministe ;
- V2 = enrichissement sémantique/knowledge ;
- V3 = ranking appris ;
- V4 = exploration ;
- V5 = graph learning.

Chaque niveau doit battre ou apporter une valeur démontrable par rapport à la baseline avant de devenir le chemin de production.

## Gate de vérité

Chaque composant possède quatre états indépendants :

1. Code ;
2. Données ;
3. Entraînement ;
4. Validation.

Donc :

`code présent ≠ données présentes ≠ modèle entraîné ≠ modèle validé`.

C'est désormais la règle de référence du dépôt.
