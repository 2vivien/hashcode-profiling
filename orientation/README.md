# Otheloo — Documentation du moteur d'orientation

Cette documentation décrit la conception scientifique, mathématique, algorithmique et technique du futur moteur d'orientation Otheloo.

## Idée centrale

Otheloo ne doit pas recommander un métier unique.

Le moteur doit construire un **profil multidimensionnel et évolutif**, puis présenter plusieurs **directions à explorer**, avec :

- pourquoi elles apparaissent ;
- les éléments du profil qui les soutiennent ;
- les incertitudes ;
- les compétences à renforcer ;
- les expériences permettant de tester les hypothèses ;
- le feedback permettant de mettre à jour le profil.

## Parcours maître

Les documents 00–18 constituent la spécification principale. Les documents 19–24 intègrent la profondeur scientifique et algorithmique de l'ancien `otheloo-orientation-engine/`. Le document 25 transforme l'ensemble en **blueprint d'implémentation** : composants à construire, contrats, données, tests, versionnement, critères de sortie et séquence des futurs commits.

### Spécification et recherche

1. [Vision et principes](./00-vision-et-principes.md)
2. [Fondements scientifiques](./01-fondements-scientifiques.md)
3. [Modèle du profil](./02-modele-profil.md)
4. [Psychométrie IRT/MIRT/CAT](./03-psychometrie-irt-cat.md)
5. [Mathématiques du moteur](./04-mathematiques-du-moteur.md)
6. [Catalogue des algorithmes](./05-catalogue-algorithmes.md)
7. [Knowledge Graph](./06-knowledge-graph.md)
8. [Pipeline hybride](./07-pipeline-hybride.md)
9. [Apprentissage longitudinal](./08-apprentissage-longitudinal.md)
10. [Explicabilité](./09-explicabilite.md)
11. [Fairness et sécurité](./10-fairness-securite.md)
12. [Validation et benchmark](./11-validation-benchmark.md)
13. [Schéma de données](./12-schema-donnees.md)
14. [Architecture technique](./13-architecture-technique.md)
15. [Roadmap V1–V7](./14-roadmap-v1-v7.md)
16. [État de l'art](./15-recherche-etat-de-l-art.md)
17. [Exemple produit](./16-exemple-produit.md)
18. [Bibliographie](./17-bibliographie.md)
19. [Industrialisation, microservices, données et règles](./18-industrialisation-microservices-donnees-regles.md)

### Approfondissements scientifiques et algorithmiques

- [19 — Fondements scientifiques approfondis](./19-fondements-scientifiques-approfondis.md)
- [20 — Moteur mathématique et algorithmique](./20-moteur-mathematique-et-algorithmique.md)
- [21 — Recommandation hybride et Knowledge Graph](./21-recommandation-hybride-et-knowledge-graph.md)
- [22 — Explicabilité, équité et Skill Gap](./22-explicabilite-equite-et-skill-gap.md)
- [23 — État de l'art et références d'implémentation](./23-etat-de-l-art-et-references-implementation.md)
- [24 — Implémentation, roadmap et schéma de données](./24-implementation-roadmap-et-schema-de-donnees.md)

### Blueprint d'implémentation

- [25 — Blueprint complet d'implémentation du moteur](./25-blueprint-implementation-moteur.md)
- [26 — Blueprint technique : code, environnement et modèles](./26-blueprint-technique-code-environnement-modeles.md)

Ce dernier document précise notamment les futurs composants **Student Profile Engine, Assessment Engine, Knowledge Graph, Candidate Engine, Hybrid Matching, Uncertainty, Skill Gap, Ranking, Diversification, Explanation, Exploration, Feedback et Recommendation Audit Layer**.

## Architecture cible

    Données élève
       ↓
    Student Profile Engine
       ↓
    Assessment Engine / Psychometrics
       ↓
    Knowledge Graph
       ↓
    Candidate Generation
       ↓
    Hard Constraints
       ↓
    Hybrid Matching
       ↓
    Uncertainty
       ↓
    Ranking + Diversification
       ↓
    Explanation + Skill Gap
       ↓
    Exploration
       ↓
    Feedback
       ↓
    Longitudinal Profile

La **Recommendation Audit Layer** conserve la provenance de chaque décision tout au long de cette chaîne.

## Règle de développement

    contrats / sécurité
      → profil
      → assessment
      → knowledge graph
      → candidats / contraintes
      → matching hybride
      → incertitude
      → skill gap
      → ranking / diversification
      → explication
      → audit
      → exploration / feedback
      → apprentissage avancé

Chaque étape doit être comparée à la précédente et validée avant d'alimenter la suivante.

## Important

Ce dossier est une **documentation de conception, de recherche et de planification d'implémentation**. Le blueprint ne signifie pas que les composants décrits sont déjà implémentés.

La documentation produit existante reste la source de vérité pour les fonctionnalités effectivement disponibles.
