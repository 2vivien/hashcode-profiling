# 05 — État de l'art : papiers, dépôts GitHub & packages

> **Objet.** Benchmark des travaux académiques et des projets open-source qui servent de références d'implémentation. Rappel de principe : **la science fonde, GitHub illustre** — les dépôts montrent *comment* implémenter, la littérature dit *pourquoi* et *quoi*.

---

## 1. Papiers et sources scientifiques clés

### 1.1 Psychologie de l'orientation

| Référence | Apport | Exploitation Otheloo |
|---|---|---|
| Lent, Brown & Hackett (1994), monographie SCCT ([PDF](https://stelar.edc.org/sites/default/files/2022-12/Toward%20a%20Unifying%20Social%20Cognitive%20Theory%20of%20Career%20and%20Academic%20Interest%2C%20Choice%2C%20and%20Performance%20_1994%20monograph.pdf)) | Modèle causal auto-efficacité → intérêts → buts → actions ; r = 0,40/0,42/0,60 sur les buts de choix | Séparation désir / capacité perçue / capacité observée |
| Lent (2021), *Career Development and Counseling*, ch. 5 ([PDF](https://stelar.edc.org/sites/default/files/2022-12/c05_Lent%20%282021%29_1.pdf)) | Les 5 modèles SCCT (intérêt, choix, performance, satisfaction, self-management) ; rôle des soutiens/obstacles | Niveau 1 (contraintes) + métriques d'intervention |
| Savickas & Porfeli, CAAS ([Career Adaptability](https://www.marksavickas.com/files/1_Savickas_bio/Career%20Construction%20Theory/Publications/Books/Career%20Adaptability/Career_Adaptability.pdf)) | 4 C ; validité discriminante vs. intelligence (r = 0,08) ; hiérarchie second ordre validée | Vecteur adaptabilité $\mathbf{D}$, instruments |
| CAAS scoring & forme courte ([CAAS Chapter](https://www.marksavickas.com/files/1_Savickas_bio/Career%20Construction%20Theory/Publications/Book%20Chapters/CAAS_Chapter.pdf)) | Clés de scoring, CAAS-SF 12 items, invariance de mesure | Questionnaire adaptatif de la brique ② |
| Nye, Su, Rounds & Drasgow (2012 ; 2017) ([PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC8931396/), [Illinois](https://experts.illinois.edu/en/publications/interest-congruence-and-performance-revisiting-recent-meta-analyt/)) | Congruence d'intérêt → performance/persistance (ρ ≈ 0,30–0,36 ; congruence 0,32 vs intérêts seuls 0,16) | Justifie le matching P–E Fit **et** l'humilité du système |
| Mount, Barrick, Scullen & Rounds (2005) ([PDF](http://www.sitesbysarah.com/mbwp/Pubs/2005_Mount_Barrick_Scullen_Rounds_PP.pdf)) | Corrélations Big Five ↔ RIASEC faibles (4/30 > 0,20) | Personnalité = signal faible, jamais verdict |
| O*NET Interest Profiler Manual ([PDF](https://www.onetcenter.org/dl_files/IP_Manual.pdf)) | Instrument RIASEC officiel, 3 formes, profils métiers numériques | Couche intérêts + profils cibles de matching |

### 1.2 Algorithmes et systèmes

| Référence | Apport | Exploitation Otheloo |
|---|---|---|
| Skills2Job (2021) ([ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S156849462030987X)) | Embeddings d'offres + ESCO + RCA + base graphe pour recommander des professions | Preuve de concept du graphe compétences→métiers |
| Carbonell & Goldstein (1998), MMR ([PDF CMU](https://www.cs.cmu.edu/~jgc/publication/The_Use_MMR_Diversity_Based_LTMIR_1998.pdf)) | Diversification par pertinence marginale | Bouquet de directions non redondant |
| Survey of Knowledge Tracing ([arXiv 2105.15106](https://arxiv.org/html/2105.15106v4)) | BKT (HMM 4 paramètres), variantes DKT/SAKT | SkillEngine : maîtrise par compétence |
| Optimizing BKT with NN parameter generation (JEDM) ([PDF](https://jedm.educationaldatamining.org/index.php/JEDM/article/download/758/224)) | Artefact de convergence du BKT (P(L) > P(T)) ; BKTransformer | Garde-fous BKT ; piste V4 interprétable |
| Ban et al., EE-Net (JMLR 2026) ([JMLR](https://jmlr.org/beta/papers/v27/23-0582.html)) | État de l'art bandits contextuels neuronaux ; TS vs UCB | ExplorationEngine V4 |
| Elmachtoub et al. (UAI 2017) ([PDF](https://www.auai.org/uai2017/proceedings/papers/171.pdf)) | Bandits contextuels par arbres de décision, bootstrap « façon Thompson » | Alternative interprétable aux bandits linéaires |
| Explainable PJRS — revue systématique 2019–2025 ([PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC12546238/)) | 85 travaux ; explicabilité = transparence + équité + confiance ; défis : biais, opacité, standardisation des compétences | Positionnement scientifique global |
| Interpretable Ranking with Constrained LambdaMART ([arXiv](https://arxiv.org/html/2206.00473v1)) | LTR interprétable par contrainte de features, code public | Niveau 5 explicable |
| Fairness in RecSys ([arXiv 2409.03893](https://arxiv.org/html/2409.03893v2)) ; panorama des métriques ([PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC8913820/)) | DP, EO, parité prédictive ; tensions entre métriques | Suite d'audit d'équité (fichier 04) |
| Dropout prediction review ([MDPI 2026](https://www.mdpi.com/2073-431X/15/3/164)) | Les modèles transparents dominent ; fairness rarement traitée | Choix de modèles lisibles pour la trajectoire |

---

## 2. Dépôts GitHub et packages de référence

### 2.1 Exploitation des ontologies

| Projet | Description | Réutilisation |
|---|---|---|
| [`KonstantinosPetrakis/esco-skill-extractor`](https://github.com/KonstantinosPetrakis/esco-skill-extractor) | Extraction de compétences ESCO depuis du texte (GUI + API, package PyPI) | Mapper les réponses libres des élèves sur la taxonomie ESCO |
| [`par-tec/esco-playground`](https://github.com/par-tec/esco-playground) | `LocalDB` ESCO en pandas, index vectoriel des compétences, NER texte→skills, client SPARQL | Base de départ du chargement ESCO + index vectoriel |
| [ESCoE Skills Extractor Library](https://www.escoe.ac.uk/the-skills-extractor-library/) | Extraction de phrases de compétences d'offres d'emploi et mapping sur taxonomies (ESCO, Lightcast) | Méthodologie d'extraction/normalisation |
| [`veneres/ilmart`](https://github.com/veneres/ilmart) | Implémentation publique du LambdaMART contraint interprétable | Niveau 5 (LTR auditable) |

### 2.2 Packages recommandés

| Brique | Python | Notes |
|---|---|---|
| IRT / psychométrie | `mirt` (R), `py-irt`, `girth` | Calibration 2PL/GRM, scores EAP |
| CAT | `catsim` | Simulation et exécution de tests adaptatifs |
| Statistiques profil | `numpy`, `scipy`, `pandas` | Trajectoires, EWMA, covariance |
| Matching vectoriel | `sentence-transformers`, `faiss-cpu` | Embeddings multilingues + recherche ANN |
| Graphe | `networkx` (proto), `neo4j` (prod), `pytorch-geometric` | Traversée, puis GNN (R-GCN) |
| Knowledge graph embeddings | `pykeen` | TransE, RotatE, prédiction de liens |
| Learning-to-rank | `lightgbm` (`objective="lambdarank"`), `xgboost` | LambdaMART natif, NDCG |
| Bandits | `vowpalwabbit` (contextual bandits), `ax-platform` | LinUCB / Thompson en prod |
| Fairness | `fairlearn`, `aif360` | DP/EO, mitigation |
| Explicabilité | `shap` | Audit interne du LTR |
| BKT/KT | `pyBKT` | Knowledge tracing interprétable |
| API | `fastapi`, TypeScript `NestJS` côté front | Services des 7 briques |

---

## 3. Leçons du terrain (ce que l'état de l'art impose à Otheloo)

1. **L'hybride domine.** Les revues systématiques des PJRS montrent que ni le pure knowledge-based ni le pure data-driven ne suffisent ; l'hybride à dominante explicable est la position défendable ([Explainable PJRS](https://pmc.ncbi.nlm.nih.gov/articles/PMC12546238/)).
2. **La standardisation des compétences est le goulot.** ESCO/O*NET ne sont pas optionnels : sans taxonomie commune, ni matching, ni graphe, ni audit d'équité ne sont possibles ([ESCO](https://esco.ec.europa.eu/en/about-esco/what-esco)).
3. **Le démarrage à froid se traite par des priors, pas par du hasard.** Les déploiements de bandits en production recommandent l'initialisation supervisée + priors de cohorte avec incertitude gonflée ([MCP Analytics](https://mcpanalytics.ai/whitepapers/contextual-bandits-whitepaper.html)).
4. **Les modèles transparents restent compétitifs sur données structurées** — les revues de prédiction en éducation montrent la domination des arbres/boosting/régressions, avec l'explicabilité comme facteur d'adoption ([MDPI review](https://www.mdpi.com/2073-431X/15/3/164)).
5. **L'explicabilité post-hoc ne remplace pas un modèle explicable.** SHAP sert l'audit ; l'utilisateur reçoit la décomposition exacte (fichier 04).
6. **La fairness se mesure en continu**, avec des métriques multiples et des seuils d'alerte — une seule métrique ne suffit pas et les métriques sont mutuellement incompatibles ([Fairness in RecSys](https://arxiv.org/html/2409.03893v2)).

---

## 4. Datasets et ressources de données

| Ressource | Accès | Usage |
|---|---|---|
| O*NET Database (fichiers Excel/CSV par domaine : intérêts, compétences, connaissances…) | Téléchargement libre, onetcenter.org | Profils numériques des métiers, Job Zones |
| ESCO v1.2.1 (CSV, RDF/SPARQL, API) | Libre, esco.ec.europa.eu | Taxonomie multilingue compétences/professions |
| O*NET Interest Profiler (items + scoring) | Licence Career Exploration Tools gratuite | Banque d'items RIASEC de départ |
| CAAS / CAAS-SF | Publications Savickas | Structure du questionnaire d'adaptabilité |
| MSLR-WEB10K/30K | Publics | Benchmark LTR (entraînement méthodologique, pas données métier) |
| Datasets KT (ASSISTments, Cognitive Tutor) | Publics | Calibration/validation du SkillEngine |
