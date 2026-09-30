# Matrice scientifique V1 → V5 — Otheloo Orientation Engine

> Document canonique d'implémentation scientifique. Les documents historiques V1→V7 restent utiles pour la recherche, mais la chaîne d'implémentation industrielle actuelle est V1 déterministe → V2 sémantique/knowledge → V3 ranking appris → V4 exploration adaptative → V5 graph learning.

## 1. V1 — moteur déterministe

### Normalisation

Z-score :

`z = (x - μ) / σ`

Min-max :

`x' = (x - x_min) / (x_max - x_min)`

La transformation retenue doit être versionnée avec ses paramètres.

### Similarités

Cosinus :

`cos(x,y) = (x·y) / (||x|| ||y||)`

Cosinus pondéré avec confiance :

`S(x,y) = Σ(w_i c_i x_i y_i) / [sqrt(Σ(w_i c_i x_i²)) sqrt(Σ(w_i c_i y_i²))]`

Distance euclidienne pondérée :

`D(x,y) = sqrt(Σ w_i (x_i-y_i)²)`

Mahalanobis régularisée :

`D_M(x,y) = sqrt((x-y)^T (Σ + λI)^(-1) (x-y))`

### Score hybride

Pour une direction d :

`S(d|p) = wI*InterestFit + wA*AbilityFit + wS*SkillFit + wV*ValueFit + wE*EnvironmentFit + wT*TrajectoryFit + wSE*SelfEfficacy + wAd*Adaptability - wG*SkillGapPenalty`

Chaque signal est pondéré par sa confiance :

`w_eff,i = w_i * confidence_i`

Le score de compatibilité n'est pas automatiquement une probabilité.

### Skill gap

`G_k = max(0, Required_k - Observed_k)`

Un gap signifie « compétence à renforcer », jamais « incapacité ».

### Trajectoire

Moyenne :

`x̄ = (1/n) Σx_i`

Variance :

`Var(X) = (1/(n-1)) Σ(x_i-x̄)²`

Vélocité :

`v_t = x_t - x_(t-1)`

Accélération :

`a_t = v_t - v_(t-1)`

Tendance :

`y_t = β0 + β1 t + ε_t`

### Incertitude / ouverture

Entropie :

`H(p) = -Σ p_i log(p_i)`

Entropie normalisée :

`H_norm = H / log(K)`

### Diversification

MMR :

`MMR(d) = λ Rel(d) - (1-λ) max_{d' sélectionné} Sim(d,d')`

### Contraintes

Les hard constraints suppriment seulement les impossibilités objectives et explicitement connues. Les préférences souples contribuent au score mais ne doivent pas fermer silencieusement une voie.

---

## 2. Knowledge Base

### Sources externes

- ESCO : version courante enregistrée dans le dépôt : v1.2.1.
- O*NET : version courante enregistrée dans le dépôt : 31.0.
- Catalogues locaux : formations, établissements, diplômes, admissions, coûts, durées, langues, localisation, opportunités.
- Données Otheloo : observations, compétences, activités, explorations, feedbacks et résultats.

La Commission européenne fournit ESCO en CSV/ODS/RDF/TTL/XML/JSON-LD ainsi qu'une API locale. O*NET 31.0 fournit des exports tabulaires et plusieurs formats structurés. Les versions et hashes doivent être conservés avec chaque snapshot.

### Modèle canonique

`OthelooSkill(id, label, aliases, escoId?, onetId?, localId?, provenance, confidence, version)`

Une correspondance automatisée est une proposition. Une correspondance de production doit être revue.

### Snapshot

Chaque snapshot conserve :

`version + source + date + sha256 + transformation_rules + item_counts`

Le Knowledge Base n'est pas un training dataset.

---

## 3. V2 — semantic matching

### Embeddings

Pour chaque document/direction :

`e_d = Encoder(description_d)`

Pour une requête :

`e_q = Encoder(query)`

Similarité :

`sim(q,d) = cos(e_q,e_d)`

Le moteur encode séparément requêtes et documents lorsque le modèle fournit des modes de retrieval distincts.

### Recherche

Pipeline :

`profile → text representation → embedding → vector retrieval → candidate enrichment`

Pour petit corpus : recherche exacte par produit scalaire sur vecteurs normalisés.

Pour gros corpus : ANN/HNSW/FAISS/pgvector peut remplacer l'index sans changer le contrat.

### Données nécessaires

- descriptions des directions ;
- descriptions des métiers ;
- descriptions des formations ;
- compétences ;
- synonymes/aliases ;
- corpus multilingue ;
- mappings ESCO/O*NET/local ;
- jeu d'évaluation semantic avec pertinence humaine.

---

## 4. Psychométrie — 2PL / GRM / MIRT / CAT

### 2PL

`P(X_i=1|θ) = 1 / [1 + exp(-a_i(θ-b_i))]`

Information de Fisher :

`I_i(θ) = a_i² P_i(θ)(1-P_i(θ))`

Erreur standard :

`SE(θ) = 1 / sqrt(I_total(θ))`

### GRM

Pour la catégorie cumulative k :

`P(X_i ≥ k | θ) = sigmoid(a_i(θ-b_ik))`

La probabilité de catégorie est obtenue par différence de deux probabilités cumulatives adjacentes.

### MIRT

Profil latent :

`θ ∈ R^m`

Pour l'item i :

`P(X_i=1|θ) = sigmoid(a_i^T θ - b_i)`

Information :

`I_i(θ) = P_i(1-P_i) a_i a_i^T`

Information totale :

`I(θ) = Σ_i I_i(θ) + λI`

Estimation par Newton régularisé :

`θ_(t+1) = θ_t + I(θ_t)^(-1) score(θ_t)`

### CAT

Sélection de l'item :

`i* = argmax_i I_i(θ)`

En multidimensionnel, une politique simple maximise la trace de la matrice d'information ; une politique plus avancée peut optimiser le déterminant ou le gain d'information attendu.

Arrêt :

- SE ≤ seuil ;
- nombre minimum d'items ;
- nombre maximum d'items ;
- couverture de contenu ;
- exposition ;
- règles de sécurité.

### Données indispensables avant validation scientifique

- banque d'items ;
- réponses réelles ;
- paramètres calibrés ;
- population de calibration ;
- fiabilité ;
- validité ;
- test-retest ;
- DIF ;
- validation de traduction ;
- politique d'exposition ;
- version de l'instrument.

Le code mathématique ne constitue pas à lui seul une validation psychométrique.

---

## 5. V3 — Learning-to-Rank

### Formulation

Pour un étudiant q, on dispose de candidats d et de features :

`x(q,d) = [score_V1, semantic, graph, skill_gap, confidence, uncertainty, accessibility, ...]`

Le modèle produit :

`f(x(q,d)) = score_rank`

L'objectif est d'ordonner les candidats pertinents.

### LambdaMART

Le dépôt utilise LightGBM avec l'objectif LambdaRank/LambdaMART et NDCG comme métrique.

La fonction de gain et le cutoff doivent être alignés avec la métrique cible.

### Dataset

Chaque ligne doit conserver :

`student_pseudonym + direction + position + timestamp + feature_snapshot + model_version + knowledge_version + feedback + outcome + label`

Le label n'est pas automatiquement « métier choisi ».

Il peut représenter une pertinence/utility définie expérimentalement.

### Split

Préférer un split temporel et éviter qu'un même étudiant apparaisse simultanément dans train et validation/test lorsque cela crée une fuite.

### Baselines obligatoires

- popularité ;
- règles ;
- scoring V1 ;
- semantic ;
- graph ;
- LambdaMART.

Le modèle appris ne remplace V1 que s'il démontre un gain mesuré.

---

## 6. Calibration

Un score devient une probabilité seulement après calibration.

### Brier

`Brier = (1/n) Σ(p_i-y_i)²`

### Log loss

`LogLoss = -(1/n) Σ[y_i log(p_i) + (1-y_i)log(1-p_i)]`

La calibration doit être entraînée sur des données indépendantes du dataset qui a entraîné le modèle de ranking.

Méthodes prévues :

- sigmoid/Platt ;
- isotonic si le volume le justifie ;
- temperature scaling pour des sorties multiclasses adaptées.

---

## 7. Fairness

Les groupes doivent être définis selon le cadre légal/produit applicable et ne doivent pas être introduits sans justification.

### Demographic parity gap

`DP_gap = max_g P(ŷ=1|g) - min_g P(ŷ=1|g)`

### Equal opportunity gap

`EO_gap = max_g TPR_g - min_g TPR_g`

Ajouter selon le cas :

- calibration par groupe ;
- error rates ;
- coverage ;
- ranking quality par groupe ;
- subgroup stability.

Aucune métrique unique ne suffit à conclure à elle seule.

---

## 8. V4 — contextual bandits

Contexte :

`x_t = profile_t`

Action :

`a_t = exploration_t`

Reward :

`r_t = learning_value_t`

Le reward ne doit pas être un simple clic.

Exemple conceptuel :

`r = α InformationGain + β LearningGain + γ SelfKnowledgeGain + δ Agency`

Les coefficients doivent être validés.

### LinUCB

`UCB_a = θ̂_a^T x + α sqrt(x^T A_a^{-1}x)`

Politique de sécurité :

- epsilon exploration ;
- actions réversibles ;
- faible risque ;
- adaptées au contexte ;
- possibilité de rollback.

### Thompson Sampling

`θ_a ~ P(θ_a|D)`

Puis :

`a_t = argmax_a x_t^T θ_a`

### UCB

`UCB = μ̂_a + α sqrt(ln(t)/n_a)`

---

## 9. Replay / IPS / Doubly Robust

### IPS

Pour une politique cible π et une politique de logging μ :

`V_IPS = (1/n) Σ 1[a_i = π(x_i)] r_i / μ(a_i|x_i)`

La propension μ doit être réellement enregistrée.

### Doubly Robust

`V_DR = (1/n) Σ [q(x_i,π(x_i)) + 1[a_i=π(x_i)](r_i-q(x_i,a_i))/μ(a_i|x_i)]`

Le dépôt expose ces estimateurs avec contrôle de propension minimale.

Sans propensités historiques fiables, l'évaluation offline n'est pas crédible.

---

## 10. V5 — Knowledge Graph / R-GCN

### Graphe

Nœuds :

`Student, Interest, Ability, Skill, Value, Direction, Training, Qualification, Occupation, Sector, Opportunity, Institution`

Relations :

`HAS_SKILL, REQUIRES_SKILL, DEVELOPS_SKILL, LEADS_TO, AVAILABLE_AT, RELATED_TO, ...`

### R-GCN

Pour un nœud i :

`h_i^(l+1) = σ(W_0^(l) h_i^(l) + Σ_r Σ_{j∈N_i^r} (1/c_{i,r}) W_r^(l) h_j^(l))`

Une décomposition par bases peut réduire le nombre de paramètres :

`W_r^(l) = Σ_b a_rb^(l) V_b^(l)`

### Tâches possibles

- classification de nœuds ;
- link prediction ;
- ranking ;
- candidate generation ;
- représentation d'entités.

Le choix de la tâche doit être déterminé par le besoin Otheloo et benchmarké contre V3.

---

## 11. Évaluation globale

### Ranking

- Precision@K
- Recall@K
- MAP@K
- MRR
- NDCG@K
- coverage
- diversity
- novelty

### Probabilités

- Brier
- log loss
- reliability/calibration curves

### Exploration

- IPS
- DR
- replay
- reward distribution
- exploration coverage

### Système

- p50
- p95
- p99
- throughput
- mémoire
- coût
- cache hit rate

### Produit

- clarté du profil ;
- compréhension du pourquoi ;
- utilité ;
- agency ;
- qualité des skill gaps ;
- qualité des explorations ;
- stabilité longitudinale.

---

## 12. Gates V1 → V5

### Gate V1 → V2

V1 déterministe reproductible, versionnée, testée et auditée.

### Gate V2 → V3

ESCO/O*NET/local Knowledge Snapshot + semantic retrieval + benchmark semantic disponibles.

### Gate V3

Dataset Otheloo versionné + labels définis + temporal split + baseline V1 + LambdaMART + benchmark.

### Gate calibration/fairness

Dataset indépendant + calibration report + subgroup audit.

### Gate V4

Logs d'exploration + propensités + reward défini + replay/IPS/DR + safety constraints.

### Gate V5

Graphe suffisamment riche + tâche clairement définie + train/validation/test sans fuite + benchmark V3 + justification du gain.

---

## 13. Règle de vérité du dépôt

Une fonctionnalité possède quatre états distincts :

1. **Code** — le mécanisme existe et est testé.
2. **Data** — les données réelles nécessaires sont présentes.
3. **Training** — un artefact de modèle a été entraîné sur ces données.
4. **Validation** — un rapport indépendant démontre les performances.

Un état ne peut jamais être déduit d'un autre.

Documentation ≠ implémentation.

Implémentation ≠ données.

Données ≠ entraînement.

Entraînement ≠ validation.
