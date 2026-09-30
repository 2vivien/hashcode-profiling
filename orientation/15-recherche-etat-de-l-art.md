# État de l'art et ressources techniques

## ESCO

ESCO est une classification multilingue des professions, aptitudes, compétences et qualifications. La Commission européenne indique qu'elle est conçue pour être comprise par des systèmes électroniques et pour des usages comme le matching, l'orientation et la gestion de l'apprentissage. Version courante affichée : v1.2.1, mise à jour du 10 décembre 2025.

Ressources :
- https://esco.ec.europa.eu/en/classification
- https://esco.ec.europa.eu/fr/use-esco

## O*NET

Le Content Model O*NET organise les informations sur le travailleur et le travail : intérêts, capacités, styles de travail, compétences, connaissances, éducation, expérience, activités et contexte.

Ressources :
- https://www.onetcenter.org/content.html
- https://www.onetcenter.org/database.html

## IRT / CAT

Les recherches IRT/CAT montrent comment sélectionner adaptativement les items, contrôler leur exposition et obtenir une mesure plus efficace. Des travaux existent aussi spécifiquement sur les tests adaptatifs d'intérêts professionnels.

Références :
- https://pmc.ncbi.nlm.nih.gov/articles/PMC6745011/
- https://pmc.ncbi.nlm.nih.gov/articles/PMC9118927/

## Contextual bandits

Référence fondatrice : Li, Chu, Langford & Schapire, 2010.

https://doi.org/10.1145/1772690.1772758

Références d'implémentation :
- https://github.com/KKeishiro/Yahoo_recommendation
- https://github.com/fidelity/mab2rec
- https://github.com/dhfromkorea/contextual-bandit-recommender

Ces dépôts sont des références d'ingénierie, pas des preuves de validité du moteur d'orientation.

## Knowledge graph et parcours

OpenPathway illustre un graphe occupation → compétences → formations → parcours, avec normalisation ESCO.

https://github.com/coolchang/openpathway

SkillAlign illustre une combinaison ESCO + Neo4j + embeddings + FAISS.

https://github.com/Y4SSERk/SkillAlign

## Ce qu'il reste à approfondir

- psychométrie adolescente ;
- validité interculturelle ;
- orientation dans les contextes africains ;
- données de formations locales ;
- marchés du travail locaux ;
- causal inference ;
- safe exploration ;
- offline policy evaluation ;
- fairness ;
- explicabilité des systèmes hybrides ;
- effets longitudinaux.

## Méthode de recherche

Pour chaque technologie :

    théorie
    → article fondateur
    → revue/méta-analyse
    → benchmark
    → implémentation
    → expérimentation
    → validation
    → décision

Un repository GitHub ne suffit jamais à justifier une décision scientifique.
