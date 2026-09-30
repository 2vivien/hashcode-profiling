# 04 — Explicabilité, équité, skill gaps & confidentialité

> **Objet.** Le « Pourquoi cette direction ? », les explications contrefactuelles, le calcul des écarts de compétences, les garde-fous d'équité (biais de genre, socio-économiques, stéréotypes de diplômes) et les obligations de confidentialité propres à un public mineur.

---

## 1. L'explicabilité comme exigence structurelle

La revue systématique 2019–2025 sur les systèmes de recommandation personne–emploi (PJRS) identifie l'explicabilité comme le levier central de transparence, d'équité et de confiance, en opposant les modèles boîte noire aux techniques explicables : importance des features, mécanismes d'attention, raisonnement sur graphe de connaissances et **explications contrefactuelles** ([Explainable PJRS — PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC12546238/)). Pour Otheloo, l'explicabilité n'est pas une couche cosmétique : elle est le contrat pédagogique. Chaque direction affichée doit répondre à quatre questions :

1. **Pourquoi ?** — les facteurs qui soutiennent la direction ;
2. **Qu'est-ce qui manque ?** — les skill gaps et prérequis ;
3. **Qu'est-ce qui est incertain ?** — les dimensions mal mesurées ;
4. **Que faire ensuite ?** — les expériences pour tester l'hypothèse.

### 1.1 Génération du « Pourquoi »

Le moteur hybride étant composé de scores décomposables (fichier 02 §2.4), l'explication principale est une **décomposition additive exacte** du score :

$$
S(e, d) = \underbrace{\omega_{int} s_{int}}_{\text{✓ intérêt scientifique élevé}} + \underbrace{\omega_{apt} s_{apt}}_{\text{✓ progression en maths}} + \cdots
$$

L'`ExplanationEngine` sélectionne les 3–5 termes les plus contributifs (signe +) et les 2–3 plus pénalisants (signe −) et les verbalise. C'est une explication **fidèle par construction** — pas une rationalisation post-hoc d'un modèle opaque.

### 1.2 SHAP en couche d'audit

Quand le learning-to-rank (LambdaMART) raffine le classement, la décomposition exacte ne suffit plus. On ajoute **SHAP** (valeurs de Shapley additives) pour attribuer la contribution de chaque feature au score d'un candidat. SHAP offre une interprétabilité locale et globale avec des garanties de cohérence, au prix d'un coût de calcul supérieur ([SHAP/LIME/Counterfactuals — overview](https://medium.com/@siddharthapramanik771/mastering-explainable-ai-shap-lime-counterfactuals-and-interpretable-neural-networks-for-1db6892461f6)). La variante **Counterfactual SHAP** (CF-SHAP) choisit les points de comparaison de manière à ce que les explications répondent aussi à la question « que faudrait-il changer ? » ([CF-SHAP — FAccT 2022](https://facctconference.org/static/pdfs_2022/facct22-3533168.pdf), [Generating Counterfactual Explanations with SHAP](https://www.alphaxiv.org/abs/1906.09293)).

**Règle d'architecture :** SHAP sert à l'**audit interne et aux développeurs** ; l'élève reçoit toujours la verbalisation de la décomposition interprétable. Jamais une explication technique brute.

---

## 2. Skill gaps : calcul matriciel des écarts

### 2.1 Définition

Soit $p_{e,s} \in [0,1]$ le niveau de maîtrise de la compétence $s$ par l'élève $e$ (posterior BKT, fichier 02 §5.2) et $r_{d,s} \in [0,1]$ le niveau requis par la direction $d$, pondéré par l'importance $\iota_{d,s}$ de la compétence pour $d$ (ESC0 distingue compétences essentielles et optionnelles ; O*NET fournit importance et niveau). Le **vecteur d'écart** :

$$
g_{s}(e, d) = \max\big(0,\; r_{d,s} - p_{e,s}\big) \cdot \iota_{d,s}
$$

et le gap agrégé $G(e,d) = \sum_s g_s(e,d) \big/ \sum_s r_{d,s}\,\iota_{d,s} \in [0,1]$.

Trois catégories affichées :

- **⚠ à renforcer** : compétences essentielles avec gap élevé et atteignables à court terme ;
- **⏳ prérequis de long terme** : gaps structurants (ex. mathématiques avancées) ;
- **🔍 exposition** : pas un gap de compétence mais de *connaissance du domaine* — résolu par l'exploration, pas par des cours.

### 2.2 Exemple verbalisé

```
Direction : Ingénierie & technologies — compatibilité 0,74 (confiance moyenne)
Pourquoi : ✓ intérêt investigateur élevé  ✓ vélocité positive en maths
           ✓ raisonnement logique maîtrisé
À renforcer : ⚠ mathématiques avancées (gap 0,35)  ⚠ autonomie de travail
À explorer : 🔍 aucune exposition aux métiers de l'ingénierie à ce jour
```

---

## 3. Explications contrefactuelles

Le contrefactuel répond à : *« quel changement minimal du profil changerait la conclusion ? »*. Otheloo l'utilise dans le sens **empowering** uniquement — montrer les leviers d'action, jamais les verrous :

$$
\delta^* = \operatorname*{arg\,min}_{\delta \in \mathcal{F}} \; \mathrm{c\hat{u}t}(\delta)
\quad \text{t.q.} \quad S(e + \delta, d) \geq \tau
$$

où $\mathcal{F}$ est l'ensemble des changements **faisables et actionnables** (renforcer une compétence, suivre une formation pont) — les attributs non actionnables (genre, origine, âge) sont **exclus par construction** de $\mathcal{F}$. $\mathrm{c\hat{u}t}(\delta)$ estime l'effort (durée de formation × difficulté).

**Exemple cible :** « Si tu renforces tes mathématiques de +2 niveaux, la compatibilité avec Ingénierie passerait d'environ 60 % à environ 85 %, et 3 formations supplémentaires deviendraient accessibles. »

Contrefactuels négatifs autorisés uniquement en mode *chemin alternatif* : « La voie A exige X que tu n'as pas ; la voie B arrive au même métier sans X » — jamais « tu ne peux pas ».

---

## 4. Équité (fairness) : biais, métriques et débiaisage

### 4.1 Sources de biais spécifiques à l'orientation

| Biais | Mécanisme | Contre-mesure Otheloo |
|---|---|---|
| Genre | Stéréotypes métier (infirmière/ingénieur) dans les données historiques | Normalisation des profils de cohorte par sous-groupe ; audit DP/EO ; jamais le genre comme feature prédictive |
| Socio-économique | L'auto-efficacité reflète l'exposition, pas le potentiel | Distinguer capacité observée / perçue (SCCT) ; bandits avec plancher d'exploration |
| Diplôme/prestige | Le graphe surreprésente les voies académiques | Chemins alternatifs obligatoires (apprentissage, passerelles) |
| Géographique | Les opportunités locales limitées écrasent le score | Contraintes dures déclarées explicitement + affichage des options à distance |
| Boucle de rétroaction | Le système ne montre que ce qu'il croit pertinent → auto-confirmation | Plancher d'exploration + MMR (diversité structurelle) |

### 4.2 Métriques d'équité calculées en continu

**Demographic Parity** : taux de proposition d'une direction dite « attractive » égal entre groupes $A$ ([Fairness metrics — PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC8913820/), [GeeksforGeeks — Fairness Metrics](https://www.geeksforgeeks.org/artificial-intelligence/fairness-metrics-demographic-parity-equalized-odds/)) :

$$
P(\hat Y = 1 \mid A = a) = P(\hat Y = 1 \mid A = b) \quad \forall\, a, b
$$

**Equalized Odds** : égalité des taux de vrais positifs et de faux positifs entre groupes — à profil réellement comparable, la probabilité de se voir proposer une direction ne dépend pas du groupe :

$$
P(\hat Y = 1 \mid Y = y, A = a) = P(\hat Y = 1 \mid Y = y, A = b), \quad y \in \{0,1\}
$$

On suit aussi l'**Equal Opportunity** (TPR seul) et la **parité prédictive** (précision égale). Les métriques sont en tension — on ne peut pas toutes les satisfaire simultanément, et le choix est **contextuel** : en orientation (enjeu élevé mais non binaire), Otheloo privilégie l'Equal Opportunity sur les directions à forte valeur (filières sélectives proposées à mérite réel égal) et surveille la Demographic Parity sur l'exposition globale ([Understanding Fairness in RecSys — arXiv](https://arxiv.org/html/2409.03893v2)). Les seuils d'alerte : |DPD| > 0,1 ou écart TPR > 0,1 → revue humaine obligatoire.

**Outil :** Fairlearn pour le suivi et la mitigation ([Microsoft — Measuring fairness](https://medium.com/data-science-at-microsoft/measuring-fairness-in-machine-learning-3211b62340b)).

### 4.3 Débiaisage opérationnel

1. **Pré-traitement** : exclusion des attributs sensibles des features prédictives (fairness through unawareness) — insuffisant seul (proxys) mais nécessaire.
2. **In-processing** : contraintes d'équité dans l'objectif du LTR (régularisation de parité).
3. **Post-traitement** : ré-équilibrage borné de l'exposition (pas de quotas de verdict, uniquement de la diversité d'exposition — compatible avec MMR).
4. **Audit trimestriel** : rapport d'équité par genre, quartier/SES proxy, établissement ; publication interne.

---

## 5. Confidentialité et données de mineurs (RGPD)

Otheloo traite les données d'élèves mineurs : le cadre est le plus strict qui existe. L'**article 8 du RGPD** fixe à 16 ans l'âge du consentement autonome pour les services en ligne, avec possibilité pour les États membres de descendre jusqu'à 13 ans — la France a choisi **15 ans** ([Art. 8 GDPR](https://gdpr-info.eu/art-8-gdpr/), [GDPRWise — âges par pays](https://gdprwise.eu/en/kennisbank/verplichtingen/gdpr-children-data/)). En dessous, le consentement du titulaire de l'autorité parentale est requis, avec des « efforts raisonnables » de vérification.

Obligations d'architecture qui en découlent :

- **Consentement parental vérifié** en dessous de l'âge national + **assentiment** de l'élève expliqué en langage adapté (support visuel/vidéo) ([UGent — données de mineurs](https://onderzoektips.ugent.be/en/tips/00001882/)).
- **Minimisation** : aucune donnée non nécessaire au profil ; les attributs sensibles (origine, santé, opinions) ne sont **jamais collectés**.
- **Droits exercables** : accès, rectification, effacement, portabilité, retrait du consentement à tout moment ([GDPR.eu](https://gdpr.eu/what-is-gdpr/)) — avec tableau de bord parental.
- **Droit à ne pas être profilé sans explication** : l'`ExplanationEngine` est aussi un dispositif de conformité (le RGPD exige une « information significative sur la logique » des traitements automatisés).
- **Aucune décision automatisée produisant des effets juridiques ou significatifs** : le système propose des directions, il ne décide rien — le principe « le système accompagne, les humains décident » est aussi une exigence légale.
- **Conservation bornée** + pseudonymisation des identifiants élèves dans le graphe (le nœud `Student` est anonymisé, la liaison identité↔profil est dans un coffre séparé).
- **Hébergement UE** recommandé ; registre des traitements ; AIPD (analyse d'impact) obligatoire avant tout déploiement réel.

---

## 6. Boucle de validation continue

| Contrôle | Fréquence | Seuil d'alerte |
|---|---|---|
| Fiabilité des échelles (α de Cronbach par dimension) | À chaque recalibration | α < 0,70 |
| Entropie moyenne des profils | Mensuelle | Dérive inexpliquée |
| Demographic Parity / Equal Opportunity | Mensuelle | écart > 0,1 |
| Taux de recommandations suivies d'exploration | Mensuel | < 20 % (le système n'inspire pas) |
| Exactitude des contrefactuels (revue experte) | Trimestrielle | tout contrefactuel irréaliste |
| Dérive du graphe (liens obsolètes ESCO/O*NET) | À chaque release des ontologies | — |
