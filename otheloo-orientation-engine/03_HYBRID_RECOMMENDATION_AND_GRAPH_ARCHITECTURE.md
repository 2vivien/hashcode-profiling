# 03 — Architecture hybride de recommandation & graphe de connaissances

> **Objet.** Le graphe élève → compétences → formations → filières → professions → opportunités ; l'intégration structurée des ontologies ESCO et O*NET ; les embeddings et réseaux de neurones sur graphes ; le moteur hybride à 5 niveaux (règles → skill-gap → embeddings → graphe → learning-to-rank).

---

## 1. Les deux référentiels fondateurs : ESCO et O*NET

### 1.1 ESCO

ESCO (*European Skills, Competences, Qualifications and Occupations*) est la classification multilingue européenne des compétences et des professions : **3 039 professions et 13 939 compétences** liées entre elles, traduites en 28 langues ([ESCO — What is ESCO](https://esco.ec.europa.eu/en/about-esco/what-esco)). Le pilier compétences est structuré en quatre sous-classifications — connaissances, langues, compétences proprement dites et compétences transversales — et chaque concept porte un terme préféré, des synonymes, une description, un niveau de réutilisabilité et des **relations** avec d'autres compétences et avec les professions ([ESCO — Skills pillar](https://esco.ec.europa.eu/en/classification/skill_main)).

ESCO est conçu explicitement pour être « compris par des systèmes électroniques » afin d'alimenter des services de matching (appariement chercheurs d'emploi–emplois, suggestions de formation pour monter en compétence) ([ESCO — What is ESCO](https://esco.ec.europa.eu/en/about-esco/what-esco)). C'est le squelette du `CareerKnowledgeGraph` côté Europe/francophonie.

### 1.2 O*NET

O*NET est la base de référence américaine, dont le modèle de contenu décrit chaque profession selon : capacités, compétences, connaissances, intérêts (profils RIASEC numériques 0–100), styles de travail, activités professionnelles, contexte de travail, formation et expérience requises ([O*NET IP Manual](https://www.onetcenter.org/dl_files/IP_Manual.pdf)). Les *Occupational Interest Profiles* fournissent des profils RIASEC complets par profession — première classification à donner des profils numériques sur les six environnements — ce qui rend le cosinus de matching intérêts élève ↔ métier directement calculable ([O*NET IP Manual](https://www.onetcenter.org/dl_files/IP_Manual.pdf)).

### 1.3 Stratégie d'intégration

| Propriété | ESCO | O*NET |
|---|---|---|
| Professions | 3 039 | ~900+ (O*NET-SOC) |
| Compétences | 13 939, hiérarchisées, 28 langues | capacités / compétences / connaissances / styles |
| Intérêts RIASEC | non (structure différente) | oui, profils numériques 0–100 |
| Usage Otheloo | colonne vertébrale multilingue du graphe compétences | profils numériques de matching + Job Zones (niveau de préparation) |

Le graphe unifié mappe les deux ontologies sur un schéma interne commun (nœuds `Occupation`, `Skill`, `Knowledge`, `Interest`, `Formation`, `Sector`, `Opportunity`), les mappings ESCO ↔ O*NET existants servant de ponts initiaux.

---

## 2. Le graphe de connaissances d'orientation

### 2.1 Schéma

```
(Élève) ──possède──▶ (Compétence) ◀──requiert── (Métier)
   │                      │                       │
   ├──intérêt RIASEC──▶ (Domaine) ◀──profil── (Métier)
   │                      │                       │
   ├──scolarité──▶ (Matière) ──développe──▶ (Compétence)
   │                                              │
(Formation) ──prépare──▶ (Métier) ──appartient──▶ (Secteur)
   │                                              │
(Formation) ──enseigne──▶ (Compétence)   (Opportunité) : stage, concours, bourse
```

Types de nœuds : `Student` (anonymisé), `Skill`, `Knowledge`, `Occupation`, `Formation` (filière/diplôme), `Sector`, `Opportunity` (stage, concours, MOOC, bourse), `Domain` (famille RIASEC/thématique). Types d'arêtes : `possède(niveau, confiance)`, `requiert(niveau, importance)`, `prépare`, `enseigne`, `appartient`, `accessible_si` (prérequis), `débouche_sur`.

### 2.2 Ce que le graphe rend calculable

- **Chemins** : « de mon niveau actuel au métier M » = plus court chemin contraint passant par les formations et compétences requises — c'est la visualisation *Aujourd'hui → niveau actuel → compétences manquantes → formations possibles → spécialisations → métiers*.
- **Skill gaps** : différence ensembliste pondérée entre `possède` et `requiert` (fichier 04).
- **Métiers proches** : voisinage dans le graphe (même famille ISCO/ESCO, compétences partagées) — alimente la diversification et les « chemins alternatifs ».
- **Propagation** : un intérêt pour « architecture » propage aux compétences associées, puis aux formations qui les enseignent.

### 2.3 Travaux de référence : Skills2Job

Le système **Skills2Job** (issu d'un projet Cedefop) est la preuve de concept académique la plus proche : il combine **embeddings sémantiques** extraits des offres d'emploi du marché européen, la représentation structurée **ESCO**, une mesure de pertinence de compétences (*revealed comparative advantage*, RCA), le tout organisé en **base graphe** interrogée par traversée pour recommander les professions les plus adaptées aux compétences d'un utilisateur ([Skills2Job — ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S156849462030987X)). Otheloo transpose ce schéma du matching « compétences → emploi » au matching « profil évolutif → directions d'avenir », en y ajoutant les couches psychométriques (fichier 01) et temporelles (fichier 02) que Skills2Job n'a pas.

---

## 3. Embeddings et GNN

### 3.1 Embeddings sémantiques

Chaque nœud textuel (profession, compétence, formation) est encodé par un modèle de phrases (type Sentence-BERT multilingue) en un vecteur dense. Usages :

1. **Matching sémantique** : rapprocher les intérêts déclarés en langage libre de l'élève (« j'aime comprendre comment marchent les corps humains ») des descriptions officielles ESCO/O*NET — recherche vectorielle avec FAISS.
2. **Extraction de compétences** : les bibliothèques open-source d'extraction mappent des phrases de texte libre sur la taxonomie ESCO exactement par ce mécanisme (extraction de phrases de compétences puis alignement sur la taxonomie) ([ESCoE — Skills Extractor Library](https://www.escoe.ac.uk/the-skills-extractor-library/)).
3. **Alignement d'ontologies** : rapprocher les concepts ESCO et O*NET partiellement par similarité vectorielle + validation experte.

### 3.2 Embeddings de graphe

Pour capter la **structure** (et pas seulement le texte) :

- **Node2Vec** : marches aléatoires biaisées + Skip-gram → vecteurs de nœuds ; deux nœuds structurellement proches (mêmes voisins) ont des vecteurs proches. Utile pour « métiers similaires » et la matrice de similarité $\mathrm{Sim}_2$ du MMR.
- **TransE / complétion de graphe** : les relations sont des translations dans l'espace, $\mathbf{h} + \mathbf{r} \approx \mathbf{t}$ ; permet la **prédiction de liens manquants** — ex. inférer qu'une formation enseigne probablement une compétence non encore reliée, ou qu'un métier requiert une compétence émergente.

### 3.3 Graph Neural Networks (GNN)

Un GNN propage l'information le long des arêtes : à chaque couche, le vecteur d'un nœud agrège ceux de ses voisins :

$$
\mathbf{h}_v^{(k+1)} = \sigma\!\left( W^{(k)} \cdot \mathrm{AGG}\big( \{ \mathbf{h}_u^{(k)} : u \in \mathcal{N}(v) \} \cup \{\mathbf{h}_v^{(k)}\} \big) \right)
$$

Usages pour Otheloo (V4) :

- **Recommandation par propagation** : partir du nœud élève, propager ses signaux (intérêts, compétences) à travers compétences → formations → métiers, et lire les scores aux nœuds métiers/domaines.
- **Prédiction de liens** personnalisée : « quelle arête `accessible_si` ou `prépare` est la plus probable pour cet élève ».
- **Variantes** : LightGCN (propagation simplifiée, efficace sur graphes user–item), R-GCN (relations typées — le graphe d'orientation est multi-relations).

**Garde-fou d'explicabilité :** le GNN ne remplace jamais le score explicable ; il sert de *feature generator* et de détecteur de candidats non évidents, ses sorties sont ensuite **re-scorées** par le pipeline explicable (§4) et auditées (fichier 04). La littérature sur les systèmes de recommandation personne–emploi souligne justement que l'opacité et la faible interprétabilité sont des problèmes majeurs du domaine ([Explainable PJRS — PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC12546238/)).

---

## 4. Le moteur hybride à 5 niveaux

Architecture en cascade : chaque niveau filtre/score et transmet au suivant. Les niveaux 1–2 sont déterministes et auditables ; les niveaux 3–4 sont sémantiques/structurels ; le niveau 5 apprend.

```
Niveau 1 — Règles dures (hard constraints)
Niveau 2 — Skill-gap analysis & factorisation matricielle
Niveau 3 — Matching sémantique (embeddings, vector search)
Niveau 4 — Traversée de graphe & pathfinding
Niveau 5 — Learning-to-rank (classement final)
```

### 4.1 Niveau 1 — Règles et contraintes dures

Filtre éliminatoire **avant** tout scoring : pays/région de la formation, accessibilité financière (coût ≤ budget déclaré), prérequis réglementaires (diplôme requis, âge, sélection), langue d'enseignement, durée maximale acceptable. Une direction qui échoue au niveau 1 n'est pas « mal scorée » : elle est **retirée** ou signalée comme « inaccessible aujourd'hui — conditions : … ». C'est l'implémentation directe des influences contextuelles de la SCCT (soutiens/obstacles, proximaux et distaux) ([marcr.net — SCCT](https://marcr.net/for-career-professionals-and-learners/career_theories_a_to_z/scct/)).

```
ALGORITHME — Filtrage dur
pour chaque candidat c dans Catalogue:
    si ¬satisfait(c, contraintes_élève): retirer c (raison r attachée)
    si prérequis_manquants(c) ≠ ∅: marquer c "accessible_sous_conditions"
```

### 4.2 Niveau 2 — Skill-gap analysis & factorisation matricielle

Pour chaque direction survivante, calcul de l'écart de compétences (formalisme complet au fichier 04 §2) : $gap(e, d) = \sum_s \max(0, r_{d,s} - p_{e,s}) \cdot importance_{d,s}$ où $r_{d,s}$ est le niveau requis et $p_{e,s}$ le niveau possédé (BKT posterior).

En parallèle, la **factorisation matricielle** exploite les données collectives : soit la matrice élèves × directions d'engagement $R$ (qui a exploré/réagi positivement à quoi), on factorise $R \approx U V^\top$ avec $U \in \mathbb{R}^{n \times k}$, $V \in \mathbb{R}^{m \times k}$ :

$$
\min_{U,V} \sum_{(i,j) \in \Omega} \left( R_{ij} - \mathbf{u}_i^\top \mathbf{v}_j \right)^2 + \lambda \left( \|U\|_F^2 + \|V\|_F^2 \right)
$$

Rôle : **complétion collaborative** — suggérer des directions qu'ont appréciées des élèves au profil latent proche. Jamais utilisée seule (cold start + opacité) : elle alimente des *features* pour le niveau 5 et des candidats pour le niveau 4.

### 4.3 Niveau 3 — Matching sémantique (embeddings)

Recherche vectorielle (FAISS, cosinus sur vecteurs L2-normalisés) entre : (a) l'embedding du profil textuel agrégé de l'élève (intérêts libres, réponses ouvertes, activités) et (b) les embeddings des descriptions de domaines/formations/métiers ESCO/O*NET. Sortie : score sémantique $s_{sem} \in [0,1]$ par candidat + candidats « hors graphe » rattrapés par le texte.

### 4.4 Niveau 4 — Traversée de graphe & pathfinding

À partir des nœuds « ancres » de l'élève (compétences maîtrisées, matières fortes, domaines RIASEC dominants) :

1. **Expansion** : voisins à 1–2 sauts (compétences voisines, formations qui enseignent, métiers qui requièrent).
2. **Pathfinding** : pour chaque métier cible retenu, calcul des chemins de formations réalisables (plus courts chemins contraints par niveau 1) → génère la visualisation *Aujourd'hui → compétences manquantes → formations → spécialisations → métiers*.
3. **Chemins alternatifs** : pour chaque chemin, variantes (apprentissage vs. cursus académique, passerelles) — « si tu renforces X et Y, plusieurs trajectoires deviennent accessibles ».

### 4.5 Niveau 5 — Learning-to-rank

Le classement final des directions est appris par **LambdaMART** (gradient boosting optimisant directement NDCG), l'algorithme LTR le plus déployé en production et implémenté nativement dans LightGBM/XGBoost ([Humblebee — ranking algorithms](https://blog.humblebee.ai/posts/the-algorithm-behind-perfect-results-an-introduction-to-ranking-algorithms)). Principe : pour deux candidats $d_i, d_j$ de labels de pertinence $l_i > l_j$, le gradient « lambda » pondère l'erreur de paire par le gain de métrique obtenu en les échangeant :

$$
\lambda_{ij} = \frac{\partial Q_{ij}}{\partial (s_i - s_j)} = \mathrm{sgn}(l_i - l_j)\,|\Delta Q_{ij}| \cdot \frac{1}{1 + e^{s_i - s_j}}
$$

où $Q$ = NDCG ([IR Journal — LambdaMART & user dynamics](https://iris.cnr.it/retrieve/8273f62b-1b1c-4903-ba93-e11fea3e5d77/prod_416220-doc_146665.pdf)). Le NDCG@k mesure la qualité du classement :

$$
DCG@k = \sum_{i=1}^{k} \frac{2^{l_i} - 1}{\log_2(i+1)}, \qquad NDCG@k = \frac{DCG@k}{IDCG@k}
$$

**Labels d'apprentissage** (le point délicat) : pas de « vérité métier ». Labels dérivés des signaux longitudinaux : engagement soutenu avec une direction, intérêt post-exploration augmenté, filière effectivement choisie ET persévérée. **Features** : tous les scores des niveaux 1–4, les confiances, l'entropie, les skill gaps. Le LTR **apprend les poids** que le score composite (fichier 02 §2.4) fixait arbitrairement.

Variante à étudier : **LambdaMART contraint/interprétable** (ILMART — contraindre le nombre de features par arbre pour conserver l'interprétabilité, code public disponible) ([Interpretable Ranking with Constrained LambdaMART — arXiv](https://arxiv.org/html/2206.00473v1)) — très aligné avec l'exigence d'explicabilité d'Otheloo.

---

## 5. Familles d'algorithmes : synthèse et positionnement

| Famille | Exemple | Rôle dans Otheloo | Limite |
|---|---|---|---|
| Règles | Filtres durs | Faisabilité réelle (niveau 1) | Aucune nuance |
| Scoring | Somme pondérée explicable | Baseline de compatibilité (fichier 02) | Poids arbitraires au départ |
| Similarité | Cosinus, Mahalanobis | Matching P–E Fit | Suppose les espaces comparables |
| KNN | Élèves similaires | Priors de cohorte, cold start | Scalabilité, bulles |
| Factorisation matricielle | SVD/ALS sur engagements | Signal collaboratif | Cold start, opacité |
| Learning-to-rank | LambdaMART | Classement final (niveau 5) | Besoin de labels longitudinaux |
| Knowledge graph | Traversée, pathfinding | Trajectoires et chemins alternatifs | Complétude du graphe |
| Embeddings | Sentence-BERT, Node2Vec, TransE | Sémantique + structure | Dérive, validation requise |
| GNN | R-GCN, LightGCN | Propagation, prédiction de liens | Explicabilité → audit |
| Bayésien | Posteriors, BKT | Incertitude native, progressivité | Hypothèses de modèle |
| Bandits contextuels | Thompson, LinUCB | Quelle expérience proposer | Définition de la récompense |
| **Hybride** | **Tout ce qui précède** | **L'architecture retenue** | Complexité d'intégration |

L'état de l'art des recommandeurs d'emploi confirme ce choix : les revues systématiques récentes montrent que les architectures **knowledge-based, data-driven et hybrides** coexistent, que l'hybride domine, et que les défis ouverts sont précisément le biais, l'opacité, l'interprétabilité et la standardisation des compétences ([Explainable PJRS — PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC12546238/)). Otheloo se positionne comme un hybride **à dominante explicable** : chaque niveau complexe est doublé d'une contrepartie interprétable.
