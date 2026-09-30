# hashcode-profiling

Documentation de conception du moteur d'orientation Otheloo — construction d'un profil multidimensionnel et évolutif, puis restitution de plusieurs directions à explorer (et non d'un métier unique).

## Structure consolidée

Le dépôt utilise désormais un seul dossier canonique : orientation/.

La fusion conserve la colonne vertébrale architecture/industrialisation de orientation/ et y intègre les six dossiers techniques et scientifiques issus de otheloo-orientation-engine/.

| Document | Rôle |
|---|---|
| orientation/00-18 | Spécification maîtresse : vision, profil, psychométrie, algorithmes, graphe, pipeline, longitudinal, explicabilité, fairness, validation, données, architecture, roadmap, état de l'art, produit, industrialisation et règles. |
| [19 — Fondements scientifiques approfondis](./orientation/19-fondements-scientifiques-approfondis.md) | RIASEC, SCCT, Career Construction, auto-efficacité, valeurs, personnalité, Person–Environment Fit et profil longitudinal. |
| [20 — Moteur mathématique et algorithmique](./orientation/20-moteur-mathematique-et-algorithmique.md) | Matching, scoring, incertitude, MMR, Bayesian updating, BKT, ranking, bandits et règles de conception. |
| [21 — Recommandation hybride et Knowledge Graph](./orientation/21-recommandation-hybride-et-knowledge-graph.md) | Génération de candidats, contraintes, sémantique, graphe, trajectoires et architecture hybride. |
| [22 — Explicabilité, équité et Skill Gap](./orientation/22-explicabilite-equite-et-skill-gap.md) | Explications, fairness, skill gaps, contrefactuels, sécurité et audit. |
| [23 — État de l'art et références d'implémentation](./orientation/23-etat-de-l-art-et-references-implementation.md) | Recherche, bibliographie technique et références open source. |
| [24 — Implémentation, roadmap et schéma de données](./orientation/24-implementation-roadmap-et-schema-de-donnees.md) | JSON Schema, PostgreSQL, graphe, validation et roadmap V1 → V4. |
| [25 — Blueprint d'implémentation du moteur](./orientation/25-blueprint-implementation-moteur.md) | Plan concret de transformation de la spécification en moteur : composants, contrats, données, API, tests, audit, versionnement, critères de sortie et ordre des futurs commits. |

## Point d'entrée

Commencer par orientation/README.md, puis orientation/25-blueprint-implementation-moteur.md, puis orientation/18-industrialisation-microservices-donnees-regles.md.

## État

Projet de recherche, conception et planification d'implémentation : l'architecture et la spécification sont consolidées et le blueprint d'implémentation est maintenant explicite, mais le moteur opérationnel n'est pas encore implémenté.

La documentation ne doit jamais être interprétée comme une preuve d'implémentation. Les futurs commits doivent apporter le code, les tests, les données de démonstration, les métriques et les preuves de validation correspondant à chaque étape.