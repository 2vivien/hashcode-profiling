# 02 — Moteur mathématique & algorithmique

> **Objet.** Toutes les formules et tous les algorithmes du moteur : psychométrie adaptative (IRT/CAT), mathématiques du matching (similarité cosinus pondérée, distances, scoring), dynamique des trajectoires, diversification (MMR) et entropie du profil, apprentissage bayésien du profil (BKT) et bandits contextuels pour l'exploration.

---

## 1. Psychométrie adaptative : Item Response Theory (IRT) et tests adaptatifs (CAT)

### 1.1 Pourquoi l'IRT et pas des sommes de points

La théorie classique des tests (somme des bonnes réponses) rend les scores dépendants du questionnaire exact administré : deux élèves passant des questionnaires différents ne sont pas comparables. L'**Item Response Theory** modélise la probabilité de réponse **item par item**, avec des paramètres d'items approximativement indépendants de l'échantillon — ce qui permet la banque d'items, l'équivalence entre formes, et le **test adaptatif informatisé (CAT)** qui choisit chaque question en fonction des réponses précédentes pour maximiser l'information tout en minimisant le nombre de questions ([Cambridge Psychometrics — IRT & CAT](https://www.psychometrics.cam.ac.uk/system/files/documents/SSRMCGibbons2016.pdf), [CASRAI — IRT guide](https://casrai.org/guides/item-response-theory)).

### 1.2 Modèles retenus

**Modèle logistique à 2 paramètres (2PL)** pour les items binaires (tâches de capacité) :

$$
P(X_{ij} = 1 \mid \theta_i) = \frac{1}{1 + e^{-a_j(\theta_i - b_j)}}
$$

où $\theta_i$ est le trait latent de l'élève $i$ (ex. aptitude numérique), $b_j$ la **difficulté** de l'item $j$ (le niveau $\theta$ pour lequel $P = 0{,}5$) et $a_j$ sa **discrimination** (la pente au point d'inflexion — « à quel point l'item tranche ») ([MetricGate — 2PL tutorial](https://metricgate.com/blogs/item-response-theory-2pl-irt-r/)).

**Modèle de réponse graduée (GRM, Samejima)** pour les items Likert (intérêts, valeurs, auto-efficacité — échelles ordinales 1–5) :

$$
P(X_{ij} \geq k \mid \theta_i) = \frac{1}{1 + e^{-a_j(\theta_i - b_{jk})}}
$$

avec des seuils ordonnés $b_{j1} < b_{j2} < \dots < b_{j,K-1}$. Le GRM est le choix standard pour les échelles de type Likert ; le 2PL pour les réponses binaires ; le 3PL (avec paramètre de devinette) uniquement pour les QCM de capacité ([CASRAI — IRT](https://casrai.org/guides/item-response-theory)).

### 1.3 Information de Fisher et sélection adaptative d'items

L'**information d'un item** au point $\theta$ est :

$$
I_j(\theta) = a_j^2 \, P_j(\theta)\, Q_j(\theta), \qquad Q_j(\theta) = 1 - P_j(\theta)
$$

L'information du test est la somme des informations d'items, et l'erreur standard de mesure est $SE(\hat\theta) = 1/\sqrt{I(\theta)}$. Le CAT applique alors la boucle :

```
ALGORITHME — CAT (questionnaire adaptatif Otheloo)
Entrées : banque d'items calibrée {(a_j, b_j)}, seuil de précision ε
1. θ̂ ← 0 (prior standard) ; items administrés ← ∅
2. Répéter :
   a. Sélectionner l'item j* = argmax_j I_j(θ̂) parmi les items non posés
      (règle de Maximum Fisher Information)
   b. Administrer j*, recueillir la réponse x_j
   c. Ré-estimer θ̂ par EAP (expected a posteriori) ou MLE
3. Jusqu'à SE(θ̂) < ε  OU  nb_items = nb_max
Sortie : θ̂, SE(θ̂)   ← l'erreur standard ALIMENTE l'incertitude du profil
```

La sortie du CAT n'est pas un score mais un **couple (estimation, incertitude)** : c'est ce couple qui alimente les intervalles de confiance du profil (§5). Concrètement, Otheloo peut réduire un questionnaire d'intérêts de 60 items à ~15–25 items par dimension mesurée avec précision comparable — essentiel pour ne pas épuiser des élèves de 13–16 ans. Les formes courtes de l'O*NET Interest Profiler (10 items/échelle) fournissent un point de départ calibré, mais le CAT permet d'aller au-delà en adaptatif ([O*NET IP Manual](https://www.onetcenter.org/dl_files/IP_Manual.pdf)).

**Calibration initiale (démarrage à froid).** Avant d'avoir des données Otheloo, on peut initialiser les paramètres d'items à partir des échelles publiques (CAAS, O*NET IP) puis recalibrer sur les réponses réelles avec `mirt` (R) ou `py-irt` (Python). La littérature recommande des échantillons de l'ordre de quelques centaines de répondants pour un 2PL stable ([CASRAI — IRT](https://casrai.org/guides/item-response-theory)).

---

## 2. Mathématiques du matching Personne–Environnement

### 2.1 Similarité cosinus pondérée par la confiance

Le matching de base entre le vecteur profil de l'élève $\mathbf{p}$ et le vecteur profil d'une direction $d$ (filière ou métier, profilé sur le même espace via O*NET/ESCO) est la similarité cosinus :

$$
\mathrm{sim}(\mathbf{p}, \mathbf{d}) = \frac{\mathbf{p} \cdot \mathbf{d}}{\|\mathbf{p}\| \, \|\mathbf{d}\|}
$$

O*NET fournit pour chaque profession un profil numérique complet : profils RIASEC (0–100), compétences, connaissances, capacités, styles de travail, activités et contexte ([O*NET IP Manual](https://www.onetcenter.org/dl_files/IP_Manual.pdf)). Le vecteur $\mathbf{d}$ est donc réel et structuré, pas fabriqué.

Chaque dimension du profil élève porte une confiance $w_i \in [0,1]$ dérivée de l'erreur de mesure ($w_i = 1/(1+SE_i)$) ou de la variance posterior. La **similarité cosinus pondérée par la confiance** :

$$
\mathrm{sim}_{w}(\mathbf{p}, \mathbf{d}) =
\frac{\sum_i w_i \, p_i \, d_i}
{\sqrt{\sum_i w_i \, p_i^2}\;\sqrt{\sum_i w_i \, d_i^2}}
$$

Effet recherché : les dimensions encore mal mesurées (peu de données) **ne tirent pas** la similarité ; elles sont signalées comme zones d'incertitude à explorer — ce qui alimente directement la stratégie d'exploration (§6).

### 2.2 Distances : Euclidienne et Mahalanobis

La recherche empirique sur la congruence RIASEC opérationnalise le fit par la **distance euclidienne** entre profils d'intérêts : les étudiants à faible distance persistent davantage et réussissent mieux, surtout en STEM ([PMC — Interest Congruence](https://pmc.ncbi.nlm.nih.gov/articles/PMC8931396/)) :

$$
D_E(\mathbf{p}, \mathbf{d}) = \sqrt{\sum_i (p_i - d_i)^2}
$$

La distance euclidienne suppose les dimensions indépendantes et de même variance — faux pour le profil Otheloo (les dimensions RIASEC adjacentes sont corrélées par construction de l'hexagone ; les notes de matières scientifiques co-varient). On utilise donc la **distance de Mahalanobis**, qui tient compte de la matrice de covariance $\Sigma$ des dimensions :

$$
D_M(\mathbf{p}, \mathbf{d}) = \sqrt{(\mathbf{p} - \mathbf{d})^\top \Sigma^{-1} (\mathbf{p} - \mathbf{d})}
$$

$\Sigma$ est estimée sur la population d'élèves (puis régularisée : $\Sigma + \lambda I$). Mahalanobis évite qu'une redondance (deux dimensions corrélées qui « comptent double ») ne gonfle artificiellement la distance. En pratique : Euclidienne pour la lisibilité et les explications, Mahalanobis pour le calcul interne quand $\Sigma$ est estimable ; les deux sont présentées et comparées dans le protocole de validation (fichier 06).

### 2.3 Normalisation des trajectoires académiques

Pour chaque matière $m$, série de notes $x_1, \dots, x_T$ :

**Niveau** (moyenne à pondération exponentielle, les récentes pèsent plus) :

$$
\mathrm{niveau}_m = \frac{\sum_{t=1}^{T} \gamma^{T-t} x_t}{\sum_{t=1}^{T} \gamma^{T-t}}, \quad \gamma \in (0,1), \text{ ex. } 0{,}8
$$

**Vélocité** (pente de la régression linéaire robuste des notes sur le temps) :

$$
\mathrm{v\'elocit\'e}_m = \frac{\sum_t (t - \bar t)(x_t - \bar x)}{\sum_t (t-\bar t)^2}
$$

**Volatilité** (écart-type des résidus autour de la tendance) et **persistance** (régularité de l'assiduité). Chaque matière est ensuite convertie en z-score **au sein de la cohorte** (même classe/même système de notation) pour rendre les trajectoires comparables entre établissements :

$$
z_{m} = \frac{\mathrm{niveau}_m - \mu_{\text{cohorte},m}}{\sigma_{\text{cohorte},m}}
$$

C'est cette normalisation par covariance de cohorte qui rend le signal « 8 → 10 → 12 → 14 » exploitable équitablement : une vélocité positive forte vaut signal même si le niveau absolu reste moyen — principe déjà inscrit dans la conception Otheloo (la trajectoire compte, pas uniquement la note actuelle).

### 2.4 Score de compatibilité composite

Le score de compatibilité d'une direction est une somme pondérée des similarités par bloc :

$$
S(e, d) = \sum_{b \in \mathcal{B}} \omega_b \, s_b(\mathbf{p}_b, \mathbf{d}_b),
\qquad \sum_b \omega_b = 1
$$

avec $\mathcal{B} = \{$intérêts, aptitudes, compétences, trajectoire, valeurs, style de travail, auto-efficacité, adaptabilité, contraintes$\}$. Poids **initiaux** (paramètres de départ à valider expérimentalement — non scientifiques tels quels) :

| Bloc $b$ | Poids initial $\omega_b$ | Justification |
|---|---|---|
| Intérêts | 0,20 | Prédicteur principal du choix (r = 0,60 dans la monographie SCCT) |
| Aptitudes | 0,20 | Condition de faisabilité |
| Compétences | 0,15 | Pont direct vers le graphe ESCO/O*NET |
| Trajectoire scolaire | 0,10 | Signal dynamique spécifique Otheloo |
| Valeurs | 0,10 | Différencie les vies pro à intérêts égaux |
| Style de travail | 0,05 | Affinement environnement |
| Auto-efficacité | 0,05 | Modérateur, pas bloquant |
| Adaptabilité | 0,05 | Capacité à construire |
| Contraintes/contexte | 0,10 | Faisabilité réelle |

Ces poids sont des **hyperparamètres appris ensuite** sur données réelles (learning-to-rank, fichier 03 §5) : le score composite sert de *baseline explicable* que le LTR vient raffiner, pas de vérité figée.

---

## 3. Entropie du profil : mesurer et afficher l'incertitude

Soit $\pi = (\pi_1, \dots, \pi_K)$ la distribution de compatibilité normalisée du moteur sur les $K$ grandes directions (softmax des scores $S(e, d_k)$). L'**entropie de Shannon** du profil de recommandation est :

$$
H(\pi) = -\sum_{k=1}^{K} \pi_k \log \pi_k, \qquad H_{\max} = \log K
$$

L'entropie normalisée $H / H_{\max} \in [0,1]$ est le **cadran d'incertitude** affiché à l'élève :

| Entropie normalisée | État déclaré | Comportement du système |
|---|---|---|
| Faible (< 0,4) | Direction dominante identifiée | Présenter la direction + chemins alternatifs proches |
| Moyenne (0,4–0,7) | Plusieurs trajectoires compatibles | Présenter le bouquet, activer la diversification MMR |
| Élevée (> 0,7) | **Profil encore incertain** | Ne pas trancher ; déclencher des expériences d'exploration ciblées (§6) |

« Profil encore incertain » et « les données disponibles ne permettent pas encore de différencier ces parcours » sont des **réponses valides** du système — ne jamais inventer une certitude. L'entropie pilote aussi l'allocation exploration/exploitation des bandits (§6).

---

## 4. Diversification : Maximal Marginal Relevance (MMR)

Présenter 5 directions qui sont en fait 5 variantes du même domaine est un échec pédagogique : l'exploration exige de la **diversité**. On applique le MMR de Carbonell & Goldstein (1998) — « un document a une haute pertinence marginale s'il est à la fois pertinent pour la requête et peu similaire aux documents déjà sélectionnés » ([Carbonell & Goldstein, 1998 — CMU](https://www.cs.cmu.edu/~jgc/publication/The_Use_MMR_Diversity_Based_LTMIR_1998.pdf)) :

$$
\mathrm{MMR} \;=\; \operatorname*{Arg\,max}_{d_i \in R \setminus S}
\left[ \lambda \, \mathrm{Sim}_1(d_i, e) \;-\; (1-\lambda) \max_{d_j \in S} \mathrm{Sim}_2(d_i, d_j) \right]
$$

où $R$ est l'ensemble des candidats, $S$ les déjà sélectionnés, $\mathrm{Sim}_1$ la compatibilité élève-direction, $\mathrm{Sim}_2$ la similarité entre directions (via le graphe ESCO/O*NET), et $\lambda$ le curseur pertinence/diversité. L'algorithme est glouton et itératif : premier choix = plus haute pertinence, puis chaque choix pénalise la redondance avec le plus proche des éléments déjà choisis ([Elastic — MMR](https://www.elastic.co/search-labs/blog/maximum-marginal-relevance-diversify-results), [Agrawal — MMR](https://aayushmnit.com/posts/2025-12-25-DiversityMMRPart1/DiversityMMRPart1.html)).

**Réglage adaptatif de λ :** λ élevé (≈ 0,8) quand l'entropie est faible (le profil est clair, on approfondit) ; λ bas (≈ 0,5) quand l'entropie est élevée (on élargit). MMR garantit qu'un « bouquet de directions » couvre des familles réellement distinctes — exactement le comportement « Sciences & santé · Ingénierie · Data · Recherche · Enseignement scientifique » de la sortie cible.

```python
def mmr_select(relevance, sim_matrix, k, lam):
    selected, remaining = [], list(range(len(relevance)))
    first = int(np.argmax(relevance))          # 1er : pure pertinence
    selected.append(first); remaining.remove(first)
    while len(selected) < k and remaining:
        best_score, best_idx = -np.inf, None
        for i in remaining:
            penalty = max(sim_matrix[i, j] for j in selected)
            score = lam * relevance[i] - (1 - lam) * penalty
            if score > best_score:
                best_score, best_idx = score, i
        selected.append(best_idx); remaining.remove(best_idx)
    return selected
```

---

## 5. Apprentissage progressif du profil : mise à jour bayésienne et BKT

### 5.1 Le profil comme posterior

Chaque dimension latente du profil est une **distribution**, pas un point. Chaque nouvelle observation (réponse, note, activité, réaction à une exploration) met à jour la distribution par la règle de Bayes :

$$
p(\theta \mid \mathcal{D}_t) \;\propto\; p(x_t \mid \theta) \; p(\theta \mid \mathcal{D}_{t-1})
$$

Le posterior d'hier devient le prior d'aujourd'hui : c'est formellement ce que signifie « le profil s'enrichit à 13, 14, 15, 16 ans ». Avec des vraisemblances gaussiennes, la mise à jour est conjuguée et analytique ; avec IRT, la vraisemblance est la fonction logistique 2PL/GRM et le posterior EAP est calculé numériquement.

### 5.2 Bayesian Knowledge Tracing (BKT) pour les compétences

Pour suivre la maîtrise de chaque **compétence** (composante $\mathbf{S}$ du profil), le modèle canonique est le **BKT**, un modèle de Markov caché à deux états (maîtrisé / non maîtrisé) par compétence, paramétré par quatre probabilités ([Survey of Knowledge Tracing — arXiv](https://arxiv.org/html/2105.15106v4), [BKT — Emergent Mind](https://www.emergentmind.com/topics/bayesian-knowledge-tracing)) :

$$
P(L_0) \; \text{(maîtrise initiale)}, \quad
P(T) = P(L_{t+1}=1 \mid L_t=0) \; \text{(apprentissage)},
$$
$$
P(G) = P(obs_t=1 \mid L_t=0) \; \text{(chance)}, \quad
P(S) = P(obs_t=0 \mid L_t=1) \; \text{(erreur)}.
$$

Après observation $obs_t$, la mise à jour du posterior de maîtrise est :

$$
P(L_t \mid obs_t = 1) = \frac{P(L_{t-1})(1 - P(S))}{P(L_{t-1})(1-P(S)) + (1-P(L_{t-1}))\,P(G)}
$$

$$
P(L_t \mid obs_t = 0) = \frac{P(L_{t-1})\, P(S)}{P(L_{t-1})\,P(S) + (1-P(L_{t-1}))(1-P(G))}
$$

puis transition d'apprentissage : $P(L_{t}) \leftarrow P(L_t \mid obs_t) + (1 - P(L_t \mid obs_t))\,P(T)$.

**Garde-fou documenté :** avec des paramètres dégénérés, la probabilité de maîtrise peut converger vers $> P(T)$ même après une suite d'échecs — un artefact connu qui impose de contraindre les paramètres ou d'utiliser des variantes à paramètres variables dans le temps ([JEDM — Optimizing BKT](https://jedm.educationaldatamining.org/index.php/JEDM/article/download/758/224), [ERIC — Optimizing BKT](https://files.eric.ed.gov/fulltext/EJ1458433.pdf)). Pour Otheloo : BKT standard en V3 (interprétable), puis variantes neurales (DKT, SAKT, BKTransformer) évaluées en V4 uniquement si elles préservent l'explicabilité — le BKT a justement l'avantage de rester probabiliste et lisible ([arXiv — KT Survey](https://arxiv.org/html/2105.15106v4)).

---

## 6. Bandits contextuels : le moteur d'exploration

### 6.1 Le problème

L'`ExplorationEngine` doit choisir, à chaque session, quelle expérience proposer : approfondir un domaine où l'élève semble fort (**exploitation**) ou lui faire découvrir un domaine encore incertain (**exploration**). C'est exactement le dilemme exploration/exploitation, formalisé par les **bandits manchots contextuels** ([Ban et al. — EE-Net, JMLR](https://jmlr.org/beta/papers/v27/23-0582.html)).

Formellement : à chaque pas $t$, le système observe le contexte $x_t$ (le profil courant $\mathcal{P}(e,t)$, incluant entropie et confiances), choisit un **bras** $a_t$ parmi les expériences possibles (découvrir le métier X, faire un mini-projet Y, regarder une journée type Z), et observe une récompense $r_t$ construite à partir de la réaction de l'élève (intérêt déclaré après découverte, temps passé, complétion, écart avant/après).

### 6.2 Thompson Sampling

Chaque bras $a$ possède des paramètres inconnus $\theta_a$ avec une distribution a priori. À chaque tour : on **échantillonne** $\tilde\theta_a$ du posterior de chaque bras, on choisit le bras de plus grande récompense attendue sous les paramètres échantillonnés, puis on met à jour le posterior avec la récompense observée ([Elmachtoub et al., UAI 2017](https://www.auai.org/uai2017/proceedings/papers/171.pdf)) :

$$
a_t = \operatorname*{arg\,max}_a \; \mathbb{E}[r \mid \tilde\theta_a, x_t], \qquad \tilde\theta_a \sim p(\theta_a \mid \mathcal{D}_{t-1,a})
$$

Cas bernoullien simple : posterior $\mathrm{Beta}(\alpha_a, \beta_a)$, mise à jour $\alpha_a \mathrel{+}= r$, $\beta_a \mathrel{+}= (1-r)$. Version contextuelle : régression linéaire bayésienne par bras, $\mathbb{E}[r] = x_t^\top \theta_a$. L'échantillonnage stochastique fait naturellement explorer les bras incertains — et **continue à randomiser même quand le feedback est retardé**, ce qui le fait surpasser UCB en présence de récompenses différées (cas fréquent : la réaction à une expérience d'orientation arrive des jours plus tard) ([applyingml.com — Bandits for Recsys](https://applyingml.com/resources/bandits/)).

### 6.3 LinUCB

Alternative déterministe : pour chaque bras, régression ridge $r = x^\top \theta_a$, avec borne de confiance supérieure ([Li et al. 2010, via MCP Analytics](https://mcpanalytics.ai/whitepapers/contextual-bandits-whitepaper.html)) :

$$
a_t = \operatorname*{arg\,max}_a \left( x_t^\top \hat\theta_a + \alpha \sqrt{x_t^\top A_a^{-1} x_t} \right)
$$

Le second terme est le bonus d'exploration : il grandit pour les contextes où le bras est incertain. Les déploiements en production rapportent que les bandits contextuels améliorent nettement les stratégies ε-greedy, et que le Thompson Sampling converge plus vite en contexte de grande dimension, tandis que LinUCB offre des décisions déterministes plus simples à auditer ([MCP Analytics — whitepaper](https://mcpanalytics.ai/whitepapers/contextual-bandits-whitepaper.html)). Pour Otheloo, l'auditabilité de LinUCB est un argument en faveur de la V1 ; le Thompson Sampling est la cible V4.

### 6.4 Règles de conception propres à l'orientation

1. **Jamais de démarrage à exploration uniforme.** Initialiser les bandits avec les priors du score composite explicable (§2.4) et les priors de cohorte, en gonflant l'incertitude (×1,5–2) — stratégie de *warm start* qui réduit fortement le regret de démarrage ([MCP Analytics](https://mcpanalytics.ai/whitepapers/contextual-bandits-whitepaper.html)).
2. **La récompense n'est jamais « l'élève a choisi ce métier ».** Elle encode l'*engagement d'exploration* et la *mise à jour d'intérêt après découverte* : « après avoir découvert ce métier, ton intérêt a-t-il augmenté ou diminué ? ».
3. **Garde-fou éthique :** un bras ne peut pas être « éteint » définitivement par manque de récompense précoce — plancher d'exploration minimal par famille de domaines (contrainte de diversité structurelle, en plus du MMR).
4. **Boucle complète :** profil → hypothèse → expérience proposée (bandit) → réaction observée → posterior mis à jour (Bayes/BKT) → nouvelle distribution de directions (entropie recalculée).

---

## 7. Tableau de synthèse des algorithmes

| Brique | Algorithme | Rôle | Quand |
|---|---|---|---|
| Mesure | IRT 2PL/GRM + CAT | Mesurer finement avec peu de questions | Dès V1 |
| Matching | Cosinus pondéré confiance | Compatibilité intérêts/compétences | V1 |
| Distance | Euclidienne / Mahalanobis | P–E Fit RIASEC, trajectoires | V1–V2 |
| Trajectoire | EWMA + pente + volatilité | Niveau/vélocité/volatilité des notes | V1 |
| Incertitude | Entropie de Shannon | Afficher « profil encore incertain » | V1 |
| Diversité | MMR | Bouquet de directions non redondant | V2 |
| Compétences | BKT (puis DKT évalué) | Maîtrise progressive par compétence | V2–V3 |
| Profil | Mise à jour bayésienne | Profil longitudinal probabiliste | V2–V3 |
| Exploration | Bandits contextuels (TS / LinUCB) | Quelle expérience proposer ensuite | V3–V4 |
| Ranking final | Learning-to-rank (LambdaMART) | Ordonner les directions (fichier 03 §5) | V3 |
| Graphe | Embeddings / GNN | Relier profil ↔ formations ↔ métiers (fichier 03) | V3–V4 |
