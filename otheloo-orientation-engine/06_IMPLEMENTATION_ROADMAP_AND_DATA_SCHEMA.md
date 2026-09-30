# 06 — Schémas de données, roadmap d'implémentation & bibliographie

> **Objet.** Le schéma de données complet (JSON Schema, PostgreSQL, graphe) pour représenter le profil longitudinal, puis la feuille de route V1 → V4, le protocole de validation scientifique, et la bibliographie de travail.

---

## 1. Schéma de données

### 1.1 Principes

- **Longitudinal d'abord** : toute mesure porte un timestamp ; rien n'est écrasé, tout est historisé.
- **Incertitude native** : toute mesure porte une erreur/variance (SE IRT, variance posterior).
- **Pseudonymisation** : `student_id` est un identifiant opaque ; la table de correspondance identité ↔ profil vit dans un coffre séparé (fichier 04 §5).
- **Traçabilité des recommandations** : chaque direction présentée est journalisée avec sa décomposition de score (base de l'explicabilité et des audits d'équité).

### 1.2 JSON Schema — profil élève (vue consolidée)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "StudentProfile",
  "type": "object",
  "required": ["student_id", "as_of", "interests", "skills", "constraints"],
  "properties": {
    "student_id": { "type": "string", "format": "uuid" },
    "as_of": { "type": "string", "format": "date-time" },
    "interests": {
      "type": "object",
      "description": "Vecteur RIASEC + intérêts fins, chaque entrée avec valeur et confiance",
      "patternProperties": {
        "^(R|I|A|S|E|C)$": { "$ref": "#/$defs/measured" }
      }
    },
    "aptitudes": {
      "type": "object",
      "description": "Par matière : niveau EWMA, vélocité, volatilité (z-scores de cohorte)",
      "additionalProperties": {
        "type": "object",
        "properties": {
          "level":     { "$ref": "#/$defs/measured" },
          "velocity":  { "$ref": "#/$defs/measured" },
          "volatility":{ "type": "number", "minimum": 0 }
        }
      }
    },
    "skills": {
      "type": "object",
      "description": "Clé = URI ESCO ; maîtrise = posterior BKT",
      "additionalProperties": {
        "type": "object",
        "properties": {
          "mastery":    { "type": "number", "minimum": 0, "maximum": 1 },
          "bkt_params": {
            "type": "object",
            "properties": {
              "p_learn": {"type":"number"}, "p_guess": {"type":"number"},
              "p_slip":  {"type":"number"}
            }
          },
          "evidence_count": { "type": "integer", "minimum": 0 }
        }
      }
    },
    "values":       { "type": "object", "additionalProperties": { "$ref": "#/$defs/measured" } },
    "personality":  { "type": "object", "description": "Big Five — signal faible, jamais verdict",
                      "additionalProperties": { "$ref": "#/$defs/measured" } },
    "self_efficacy":{ "type": "object", "additionalProperties": { "$ref": "#/$defs/measured" } },
    "adaptability": {
      "type": "object",
      "properties": {
        "concern":    { "$ref": "#/$defs/measured" },
        "control":    { "$ref": "#/$defs/measured" },
        "curiosity":  { "$ref": "#/$defs/measured" },
        "confidence": { "$ref": "#/$defs/measured" }
      }
    },
    "constraints": {
      "type": "object",
      "properties": {
        "country": {"type":"string"}, "region": {"type":"string"},
        "max_tuition": {"type":"number"}, "max_duration_years": {"type":"integer"},
        "mobility": {"type":"boolean"}, "language": {"type":"array","items":{"type":"string"}}
      }
    },
    "profile_entropy": { "type": "number", "minimum": 0 },
    "uncertainty_flags": { "type": "array", "items": { "type": "string" } }
  },
  "$defs": {
    "measured": {
      "type": "object",
      "required": ["value", "confidence"],
      "properties": {
        "value":      { "type": "number" },
        "confidence": { "type": "number", "minimum": 0, "maximum": 1 },
        "measured_at":{ "type": "string", "format": "date-time" }
      }
    }
  }
}
```

### 1.3 PostgreSQL — tables principales

```sql
-- Profil longitudinal : aucune mise à jour destructive
CREATE TABLE measurements (
    id            BIGSERIAL PRIMARY KEY,
    student_id    UUID NOT NULL,
    dimension     TEXT NOT NULL,          -- ex. 'interest.I', 'skill.esco:1234', 'aptitude.maths.level'
    value         DOUBLE PRECISION NOT NULL,
    confidence    DOUBLE PRECISION NOT NULL CHECK (confidence BETWEEN 0 AND 1),
    instrument    TEXT NOT NULL,          -- 'CAT', 'grades', 'BKT', 'exploration_feedback'
    measured_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_measurements_student_dim ON measurements(student_id, dimension, measured_at DESC);

CREATE TABLE assessment_sessions (
    id            BIGSERIAL PRIMARY KEY,
    student_id    UUID NOT NULL,
    instrument    TEXT NOT NULL,          -- 'RIASEC_CAT', 'CAAS_SF', ...
    theta         DOUBLE PRECISION,
    se            DOUBLE PRECISION,       -- erreur standard -> confiance du profil
    items_administered JSONB NOT NULL,    -- [{item_id, a, b, response}]
    started_at    TIMESTAMPTZ, ended_at TIMESTAMPTZ
);

CREATE TABLE recommendations (
    id            BIGSERIAL PRIMARY KEY,
    student_id    UUID NOT NULL,
    direction_id  TEXT NOT NULL,          -- nœud Domain/Formation/Occupation du graphe
    score         DOUBLE PRECISION,
    score_decomp  JSONB NOT NULL,         -- {"interests": 0.148, "aptitudes": 0.102, ...}
    skill_gaps    JSONB,                  -- [{skill_uri, gap, category}]
    counterfactuals JSONB,                -- [{action, delta_score, cost}]
    mmr_lambda    DOUBLE PRECISION,
    profile_entropy DOUBLE PRECISION,
    engine_version TEXT NOT NULL,
    created_at    TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE exploration_events (          -- journal des bandits
    id            BIGSERIAL PRIMARY KEY,
    student_id    UUID NOT NULL,
    arm_id        TEXT NOT NULL,          -- expérience proposée
    context       JSONB NOT NULL,         -- snapshot du profil (features du bandit)
    reward        DOUBLE PRECISION,       -- engagement / delta d'intérêt post-découverte
    policy        TEXT NOT NULL,          -- 'thompson' | 'linucb' | 'rule'
    propensity    DOUBLE PRECISION,       -- proba de sélection (pour évaluation hors-ligne)
    created_at    TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE fairness_audit (
    id            BIGSERIAL PRIMARY KEY,
    period        DATERANGE NOT NULL,
    metric        TEXT NOT NULL,          -- 'demographic_parity', 'equal_opportunity'
    group_dim     TEXT NOT NULL,          -- 'gender', 'ses_proxy', 'school'
    value         DOUBLE PRECISION NOT NULL,
    threshold     DOUBLE PRECISION NOT NULL,
    alert         BOOLEAN GENERATED ALWAYS AS (abs(value) > threshold) STORED
);

-- Consentements (RGPD art. 8)
CREATE TABLE consents (
    id            BIGSERIAL PRIMARY KEY,
    student_id    UUID NOT NULL,
    scope         TEXT NOT NULL,
    granted_by    TEXT NOT NULL,          -- 'parent' | 'student' (selon âge légal)
    granted_at    TIMESTAMPTZ, revoked_at TIMESTAMPTZ
);
```

### 1.4 Schéma du graphe (Cypher-like)

```cypher
// Nœuds
(:Student {id, pseudonym})                 // anonymisé ; liaison identité en coffre séparé
(:Skill {esco_uri, label, pillar})         // ESCO 13 939 concepts
(:Occupation {esco_uri, onet_soc, label, riasec: {R,I,A,S,E,C}})
(:Formation {id, label, level, cost, duration_y, country, region, language})
(:Domain {code, label})                    -- familles RIASEC / thématiques
(:Sector {code, label})
(:Opportunity {id, type})                  -- stage, concours, bourse, MOOC

// Arêtes
(Student)-[:POSSESSES {mastery, confidence, since}]->(Skill)
(Student)-[:INTERESTED_IN {score, confidence}]->(Domain)
(Occupation)-[:REQUIRES {level, importance, essential}]->(Skill)
(Formation)-[:TEACHES {weight}]->(Skill)
(Formation)-[:PREPARES_FOR]->(Occupation)
(Formation)-[:ACCESSIBLE_IF {rule}]->(Formation)     -- passerelles / prérequis
(Occupation)-[:BELONGS_TO]->(Sector)
(Occupation)-[:ALIGNED_WITH {riasec_weight}]->(Domain)
(Opportunity)-[:RELATES_TO]->(Occupation|Formation|Domain)
```

**Requêtes types :**

```cypher
// Skill gaps d'une direction
MATCH (o:Occupation {esco_uri: $uri})-[r:REQUIRES]->(s:Skill)
OPTIONAL MATCH (st:Student {id: $sid})-[p:POSSESSES]->(s)
RETURN s.label, r.level AS required, p.mastery AS current,
       (r.level - coalesce(p.mastery, 0)) * r.importance AS gap
ORDER BY gap DESC;

// Chemins formation vers un métier, filtrés par contraintes
MATCH path = shortestPath(
  (f:Formation)-[:TEACHES|PREPARES_FOR|ACCESSIBLE_IF*1..4]->(o:Occupation {esco_uri:$uri}))
WHERE f.country = $country AND f.cost <= $max_tuition
RETURN path;
```

---

## 2. Roadmap d'implémentation V1 → V4

### V1 — Fondations explicables (M0–M6)

**Objectif :** un moteur déjà utile, 100 % explicable, sans ML appris.

- `StudentProfile` v1 (PostgreSQL + JSON Schema ci-dessus) ;
- `AssessmentEngine` : questionnaires calibrés (RIASEC inspiré O*NET IP, CAAS-SF, valeurs) en mode **fixe puis CAT** (`catsim`) ;
- Trajectoires scolaires : EWMA/vélocité/volatilité, z-scores de cohorte ;
- Matching : cosinus pondéré confiance sur profils RIASEC O*NET + distance Euclidienne ;
- Score composite à poids initiaux (fichier 02 §2.4) + **décomposition exacte** = `ExplanationEngine` v1 ;
- Entropie du profil affichée ; filtrage dur des contraintes (niveau 1) ;
- Chargement ESCO + O*NET (CSV → graphe Neo4j) ; base `esco-playground` comme starter ;
- Consentement parental, minimisation, tableau de bord parent (RGPD).

**Critère de sortie :** pour 100 % des directions affichées, le « Pourquoi ? » est générable et vérifié par un humain.

### V2 — Profil probabiliste et graphe (M6–M12)

- Mise à jour bayésienne des dimensions (posteriors) ; confiances propagées au matching ;
- `SkillEngine` : BKT par compétence (`pyBKT`), garde-fous de convergence documentés ;
- Skill gaps matriciels + premiers contrefactuels actionnables ;
- MMR pour la diversification des bouquets de directions ;
- Embeddings sémantiques (`sentence-transformers` multilingue + FAISS) pour le langage libre et l'extraction de compétences vers ESCO ;
- Pathfinding de trajectoires (chemins + chemins alternatifs) ;
- Audit d'équité v1 (DP, EO) automatisé.

**Critère de sortie :** l'entropie moyenne des profils décroît avec l'usage ; les skill gaps verbalisés sont jugés exacts par des conseillers.

### V3 — Apprentissage du classement (M12–M18)

- Learning-to-rank (LightGBM LambdaMART) entraîné sur les signaux longitudinaux (engagement, intérêt post-exploration, persévérance) ; features = tous les scores des niveaux 1–4 ;
- Variante contrainte/interprétable (`ilmart`) évaluée pour l'auditabilité ;
- Factorisation matricielle sur les engagements (signal collaboratif) ;
- SHAP en couche d'audit interne ;
- Évaluation hors-ligne des politiques de recommandation (propensity logging déjà en place).

**Critère de sortie :** le LTR bat la baseline à poids fixes en NDCG@5 sur validation temporelle, **sans** dégrader les métriques d'équité ni l'explicabilité.

### V4 — Orientation & Opportunités : la boucle complète

- `ExplorationEngine` : bandits contextuels (LinUCB puis Thompson Sampling), initialisés par priors supervisés + priors de cohorte, plancher d'exploration par famille de domaines ;
- Expériences de découverte (journées types, mini-projets, quiz « ton intérêt a-t-il augmenté ? ») bouclant sur le profil ;
- GNN (R-GCN via PyTorch Geometric) pour prédiction de liens et candidats non évidents — re-scorés par le pipeline explicable ;
- Intégration des opportunités réelles (stages, concours, bourses) dans le graphe ;
- Tableau de bord longitudinal élève/parent : évolution du profil, entropie, expériences faites et à faire.

**Critère de sortie :** démonstration mesurée que la boucle augmente l'efficacité décisionnelle (mesure type CDMSE avant/après) et l'adaptabilité (CAAS répété) — les métriques de succès que la littérature valide.

---

## 3. Protocole de validation scientifique

| # | Validation | Méthode | Seuil d'acceptation |
|---|---|---|---|
| 1 | Fiabilité des instruments | α de Cronbach, test-retest (4 semaines) | α ≥ 0,70 ; r_tt ≥ 0,70 |
| 2 | Précision CAT | Biais/RMSE de θ̂ vs. forme longue, simulé puis réel | RMSE ≤ 0,35 logits |
| 3 | Validité convergente | Corrélations RIASEC ↔ instruments de référence | pattern attendu, pics sur échelles homologues |
| 4 | Qualité du classement | NDCG@5, validation temporelle (train passé → test futur) | LTR > baseline, écart significatif (test de Fisher) |
| 5 | Exactitude des explications | Revue par conseillers d'orientation (échantillon) | ≥ 90 % jugées fidèles |
| 6 | Équité | DP, EO, parité prédictive par groupe, en continu | écarts ≤ 0,1 |
| 7 | BKT sain | Contrôle des paramètres dégénérés (learn rate excessif) | 0 compétence à maîtrise aberrante |
| 8 | Effet utilisateur | CDMSE + CAAS avant/après 6 mois d'usage | augmentation significative |
| 9 | Conformité | AIPD, registre, exercice des droits (test) | 100 % des droits exercables |
| 10 | Dérive | Monitoring entropie, fairness, graphe (releases ESCO/O*NET) | alertes traitées < 1 mois |

**Principes du protocole :** validation **temporelle** (jamais de fuite futur→passé), cohortes témoins quand éthiquement possible, aucune métrique de « prédiction du bon métier » — le succès se mesure en *construction de carrière*, pas en précision de classification.

---

## 4. Bibliographie et ressources

### Fondations psychologiques

1. Lent, R. W., Brown, S. D., & Hackett, G. (1994). *Toward a Unifying Social Cognitive Theory of Career and Academic Interest, Choice, and Performance.* [Monographie](https://stelar.edc.org/sites/default/files/2022-12/Toward%20a%20Unifying%20Social%20Cognitive%20Theory%20of%20Career%20and%20Academic%20Interest%2C%20Choice%2C%20and%20Performance%20_1994%20monograph.pdf)
2. Lent, R. W. (2021). *Career Development and Counseling*, chap. 5 — SCCT. [PDF](https://stelar.edc.org/sites/default/files/2022-12/c05_Lent%20%282021%29_1.pdf)
3. *The perspectives of social cognitive career theory approach in current times.* [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC9749854/)
4. Savickas, M. L., & Porfeli, E. J. — *Career Adaptability / CAAS*. [PDF](https://www.marksavickas.com/files/1_Savickas_bio/Career%20Construction%20Theory/Publications/Books/Career%20Adaptability/Career_Adaptability.pdf) ; [CAAS Chapter](https://www.marksavickas.com/files/1_Savickas_bio/Career%20Construction%20Theory/Publications/Book%20Chapters/CAAS_Chapter.pdf)
5. Nye, C. D., Su, R., Rounds, J., & Drasgow, F. (2012/2017). *Vocational interests and performance / Interest congruence and performance.* [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC8931396/) ; [Illinois Experts](https://experts.illinois.edu/en/publications/interest-congruence-and-performance-revisiting-recent-meta-analyt/)
6. Mount, M. K., Barrick, M. R., Scullen, S. E., & Rounds, J. (2005). *Higher-order dimensions of the Big Five and the Big Six.* [PDF](http://www.sitesbysarah.com/mbwp/Pubs/2005_Mount_Barrick_Scullen_Rounds_PP.pdf) ; Barrick, Mount & Gupta (2003). [PDF](http://www.sitesbysarah.com/mbwp/Pubs/2003_Barrick_Mount_Gupta.pdf)
7. *O*NET Interest Profiler Manual* (2021). [PDF](https://www.onetcenter.org/dl_files/IP_Manual.pdf) ; [O*NET IP](https://www.onetcenter.org/IP.html)
8. ESCO — European Commission. [What is ESCO](https://esco.ec.europa.eu/en/about-esco/what-esco) ; [Skills pillar](https://esco.ec.europa.eu/en/classification/skill_main)
9. Théorie des valeurs de Schwartz appliquée à la carrière. [Guide](https://jobcannon.io/blog/schwartz-values-theory-career-guide)

### Psychométrie et algorithmes

10. Cambridge Psychometrics — *Introduction to IRT and CAT*. [PDF](https://www.psychometrics.cam.ac.uk/system/files/documents/SSRMCGibbons2016.pdf)
11. *Item Response Theory for Research Scales.* [CASRAI](https://casrai.org/guides/item-response-theory) ; [2PL tutorial](https://metricgate.com/blogs/item-response-theory-2pl-irt-r/)
12. Carbonell, J., & Goldstein, J. (1998). *The Use of MMR.* [PDF CMU](https://www.cs.cmu.edu/~jgc/publication/The_Use_MMR_Diversity_Based_LTMIR_1998.pdf)
13. *A Survey of Knowledge Tracing.* [arXiv:2105.15106](https://arxiv.org/html/2105.15106v4) ; *Optimizing BKT with NN Parameter Generation* (JEDM). [PDF](https://jedm.educationaldatamining.org/index.php/JEDM/article/download/758/224) ; [BKT — Emergent Mind](https://www.emergentmind.com/topics/bayesian-knowledge-tracing)
14. Ban, Y. et al. (2026). *Neural Exploitation and Exploration of Contextual Bandits.* [JMLR](https://jmlr.org/beta/papers/v27/23-0582.html) ; Elmachtoub et al. (2017). *Practical Contextual Bandits with Decision Trees.* [UAI](https://www.auai.org/uai2017/proceedings/papers/171.pdf) ; [Bandits for RecSys](https://applyingml.com/resources/bandits/) ; [Contextual Bandits in Prod](https://mcpanalytics.ai/whitepapers/contextual-bandits-whitepaper.html)
15. *Skills2Job* (2021). [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S156849462030987X)
16. *Interpretable Ranking with Constrained LambdaMART.* [arXiv](https://arxiv.org/html/2206.00473v1) ; *Boosting LTR with user dynamics* (IR Journal). [PDF](https://iris.cnr.it/retrieve/8273f62b-1b1c-4903-ba93-e11fea3e5d77/prod_416220-doc_146665.pdf)
17. *Explainable person–job recommendations: challenges.* [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC12546238/)

### Équité, explicabilité, droit

18. *Understanding Fairness in Recommender Systems.* [arXiv:2409.03893](https://arxiv.org/html/2409.03893v2) ; *A clarification of the nuances in the fairness metrics landscape.* [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC8913820/) ; [Fairness Metrics — GeeksforGeeks](https://www.geeksforgeeks.org/artificial-intelligence/fairness-metrics-demographic-parity-equalized-odds/) ; [Fairlearn — Microsoft](https://medium.com/data-science-at-microsoft/measuring-fairness-in-machine-learning-3211b62340b)
19. *Counterfactual Shapley Additive Explanations* (FAccT 2022). [PDF](https://facctconference.org/static/pdfs_2022/facct22-3533168.pdf)
20. RGPD art. 8 (consentement des enfants). [gdpr-info.eu](https://gdpr-info.eu/art-8-gdpr/) ; âges par pays. [GDPRWise](https://gdprwise.eu/en/kennisbank/verplichtingen/gdpr-children-data/) ; mineurs et recherche. [UGent](https://onderzoektips.ugent.be/en/tips/00001882/)
21. *ML and DL for Dropout Prediction in HE: A Review.* [MDPI](https://www.mdpi.com/2073-431X/15/3/164)

### Implémentation open-source

22. [esco-skill-extractor](https://github.com/KonstantinosPetrakis/esco-skill-extractor) · [esco-playground](https://github.com/par-tec/esco-playground) · [ESCoE Skills Extractor Library](https://www.escoe.ac.uk/the-skills-extractor-library/) · [ilmart](https://github.com/veneres/ilmart)
