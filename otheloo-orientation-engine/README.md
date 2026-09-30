# Otheloo Orientation Engine — Dossier Technique & Scientifique

> **Spécification de recherche et de conception** pour le moteur d'orientation intelligent prévu dans la **V4 d'Otheloo (Orientation & Opportunités)**.
> Ce dossier est une documentation de conception : il décrit l'architecture cible, les fondements scientifiques et les algorithmes retenus. Il ne prétend pas que le moteur existe déjà.

---

## Direction centrale (non négociable)

Le moteur Otheloo **ne prédit pas un métier**. Il construit **progressivement** une compréhension du profil de l'élève et lui présente des **directions possibles**, accompagnées de :

1. **Le « Pourquoi »** — raisons, correspondances d'intérêts, forces observées ;
2. **Les écarts de compétences** (*skill gaps*) et prérequis à renforcer ;
3. **Les zones d'incertitude** — ce que le système doit encore explorer ;
4. **Les expériences recommandées** — projets, lectures, découvertes, quiz pour tester l'hypothèse.

Le système observe ensuite ce que l'élève fait et comment il réagit, met à jour son profil, et recommence. L'orientation est un **processus continu**, pas un test passé une fois en classe de troisième.

**Exemple de sortie cible :**

```
Profil : Investigateur–Social
  Fort intérêt pour la résolution de problèmes et l'aide aux autres.
  Progression régulière en sciences. Forte curiosité.
  Auto-efficacité moyenne en mathématiques mais en progression.

Directions à explorer :
  Sciences & santé · Ingénierie & technologies · Informatique & données
  Recherche · Enseignement scientifique

Pourquoi ?
  ✓ intérêt scientifique élevé
  ✓ progression en mathématiques
  ✓ intérêt pour la résolution de problèmes
  ✓ préférence pour comprendre comment les choses fonctionnent

À renforcer / explorer :
  ⚠ mathématiques avancées
  ⚠ autonomie
  ⚠ exposition au domaine
```

---

## Structure du dossier

| Fichier | Contenu |
|---|---|
| `01_SCIENTIFIC_FOUNDATIONS.md` | Fondements psychologiques et psychométriques : RIASEC, SCCT, Savickas/CCT, Bandura, Schwartz, Big Five, Person–Environment Fit ; modèle formel du profil élève ; dynamique temporelle des trajectoires scolaires. |
| `02_MATHEMATICAL_AND_ALGORITHMIC_ENGINE.md` | Toutes les mathématiques du moteur : IRT/CAT, similarité cosinus pondérée, distances (Euclidienne, Mahalanobis), scoring pondéré, tendances de notes, entropie, MMR, mise à jour bayésienne, BKT, bandits contextuels (Thompson Sampling, UCB). |
| `03_HYBRID_RECOMMENDATION_AND_GRAPH_ARCHITECTURE.md` | Architecture du graphe de connaissances élève → compétences → formations → filières → professions → opportunités ; intégration ESCO/O*NET ; embeddings et GNN ; moteur hybride à 5 niveaux (règles → scoring → embeddings → graphe → learning-to-rank). |
| `04_EXPLAINABILITY_FAIRNESS_AND_SKILL_GAP.md` | Explicabilité (« pourquoi cette direction ? »), explications contrefactuelles, calcul des skill gaps, métriques d'équité (Demographic Parity, Equalized Odds), débiaisage, confidentialité et RGPD pour mineurs. |
| `05_GITHUB_REPOS_AND_RESEARCH_STATE_OF_THE_ART.md` | État de l'art : papiers clés, dépôts GitHub de référence, packages Python/TypeScript recommandés, benchmarks et leçons à retenir. |
| `06_IMPLEMENTATION_ROADMAP_AND_DATA_SCHEMA.md` | Schémas de données (JSON Schema, PostgreSQL, graphe), roadmap V1 → V4, protocole de validation scientifique, bibliographie et ressources. |

---

## Principes directeurs transverses

1. **Jamais de verdict.** Le système dit « plusieurs trajectoires sont compatibles », jamais « tu dois faire X ».
2. **Le profil est longitudinal.** La trajectoire (`8 → 10 → 12 → 14`) compte plus que la photographie (`13/20`).
3. **L'incertitude est affichée.** « Profil encore incertain » est une réponse valide.
4. **L'explication accompagne chaque recommandation.** Chaque direction affichée répond à « Pourquoi ? ».
5. **Les parents accompagnent, ne choisissent pas.** Le système informe ; les humains décident.
6. **L'exploration est une boucle.** profil → hypothèse → découverte → réaction de l'élève → nouveau profil → nouvelle recommandation.
7. **La science fonde, GitHub illustre.** Les fondations viennent de la littérature scientifique et des bases professionnelles structurées (O*NET, ESCO) ; les projets open-source servent de références d'implémentation, pas de preuves scientifiques.

---

## Les 7 briques logicielles cibles (V4)

| # | Brique | Rôle |
|---|---|---|
| ① | `StudentProfile` | Profil longitudinal multidimensionnel de l'élève. |
| ② | `AssessmentEngine` | Questionnaires psychométriques adaptatifs (IRT/CAT). |
| ③ | `SkillEngine` | Compétences actuelles, émergentes, à développer (BKT). |
| ④ | `CareerKnowledgeGraph` | matière ↔ compétence ↔ formation ↔ métier ↔ secteur ↔ opportunité (ESCO/O*NET). |
| ⑤ | `RecommendationEngine` | Matching hybride : règles + similarité vectorielle + graphe + ranking. |
| ⑥ | `ExplanationEngine` | Chaque recommandation répond « Pourquoi ? » + contrefactuels. |
| ⑦ | `ExplorationEngine` | Propose des découvertes, observe les réactions, met à jour le profil (bandits contextuels). |

---

*Dossier rédigé en français technique et scientifique. Octobre 2026.*
