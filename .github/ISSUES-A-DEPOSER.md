# Issues à déposer sur GitHub

> **Ces 13 issues ont été créées sur GitHub** : #33, #38, #39, #40, #41, #42, #43,
> #44, #45, #46, #47, #48, #49. Ce fichier reste la référence détaillée.
>
> Note d'exploitation (#48) : le PAT exposé est révoqué et renvoie 401 sur l'API,
> mais `git` utilise **un autre credential stocké sur disque** (`~/.git-credentials`),
> ce qui explique que le push ait continué à fonctionner.

État au **11 octobre 2026**. 10 issues déjà ouvertes sur le dépôt, cette liste
les complète et les priorise.

---

## P0 — Bloquants

### 1. `SECU` RGPD et mineurs : finalité, base légale, consentement, DPIA, effacement

**Suivi de #22. Bloquant avant toute mise en production réelle.**

Le moteur traite des profils d'élèves, donc potentiellement de mineurs. Aucun de
ces points n'est traité.

À traiter :
- finalité et base légale de chaque traitement (profilage d'un mineur) ;
- consentement et droit de retrait, y compris pour un mineur ;
- durée de conservation de `profile`, `observation`, `recommendation`, `audit_event` ;
- droit d'effacement : la suppression réelle doitRemove toutes les lignes liées
  à un `student_ref` (aujourd'hui il n'existe aucun script de suppression) ;
- DPIA (analyse d'impact) obligatoire dès qu'un profilage systématisé ;
- information des familles et des équipes éducatives ;
- documentation de ce qui est pseudonymisé et ce qui ne l'est pas.

Point technique : `audit_event` conserve `recommendation_id` et `student_ref`.
Un journal d'audit qui ne s'efface jamais est un registre de suivi, pas un
journal d'audit — à trancher explicitement.

---

### 2. `OPS` Sauvegardes automatiques et restauration **testée**

**Aucun mécanisme en place, et aucune restauration jamais réalisée.**

Le risque est asymétrique : une perte de données sur `profile`,
`recommendation` et `audit_event` est irrécupérable, la fréquence de perte est
faible. C'est le meilleur rapport risque/effort de toute la liste.

À faire :
- sauvegarde quotidienne de Postgres (dump compressé, hors du volume applicatif) ;
- rétention définie et testée ;
- **restauration réellement vérifiée** sur un environnement jetable, pas seulement
  la sauvegarde ;
- alerte si la sauvegarde échoue.

---

### 3. `SECU` Rotation des secrets exposés

Les clés以下 ont été partagées en clair dans une conversation :
- un PAT GitHub (révoqué depuis),
- une clé API Gemini,
- une clé API Groq.

Elles sont dans `.env` (600, gitignoré), jamais commitées — vérifié. Mais elles
doivent être **régénérées** une dernière fois et l'ancienne version considérée
comme compromise. Vérifier aussi les journaux d'accès des deux fournisseurs.

---

## P1 — Qualité et sécurité

### 4. `TEST` Couvrir par des tests de contrat les endpoints récents

`layers`, `/atlas`, `/context`, `/rag/stats` et `/assessment-v1/ability` ont été
ajoutés sans un seul test de contrat. Une régression silencieuse passerait.

À faire :
- figer la forme des réponses dans `tests/contract/` ;
- vérifier qu'un `layers` vide ne casse pas le front ;
- tester le comportement quand le RAG est indisponible ou la base injoignable ;
- vérifier que `atlas` dégrade proprement sans `coverage.json`.

---

### 5. `OBS` Observabilité : métriques Prometheus, logs structurés, alertes

**Suivi de #18.** Le moteur est en production sans `/metrics`, sans logs
structurés et sans aucune alerte.

Priorité minimale :
- latence p50/p95 par endpoint ;
- durée d'indexation RAG et état de l'index ;
- nombre de couches actives (doit être surveillé : un passage à 0 indicates une
  régression silencieuse) ;
- taux d'échec de la chaîne de traduction (Gemini puis Groq) ;
- alerte si le moteur ne démarre pas avec la connaissance attendue.

---

### 6. `SECU` Durcissement restant : CORS, quotas par consommateur, scans

**Suivi de #19.** CORS est non configuré (et le site est sur le même domaine —
à trancher), il n'y a pas de quotas par appelant, et aucun scan de sécurité
périodique.

À faire : politique CORS explicite, rate limiting par clé d'API, Dependabot,
scan de dépendances, en-têtes CSP stricts.

---

### 7. `QA` Tests de charge et tenue en service

Le RAG construit un index de 5 967 documents à froid (1,5 s). Rien n'a été
mesuré sous charge réelle ni en cas de pic.

À faire : test de charge sur `/recommendations` et `/context`, définir ce qu'on
accepte comme latence p95, et vérifier le comportement en cas d'épuisement de
mémoire.

---

## P2 — Données et périmètre

### 8. `DATA` Ingestion ESCO et O\*NET (suite de #21)

Les archives sont téléchargées et traçables dans `data/raw/` (manifests avec
SHA-256 versionnés), mais l'ingestion n'est pas faite.

Reste à faire :
- ingérer l'archive O\*NET 31.0 (91,8 Mo déjà téléchargée) ;
- exploiter le **crosswalk officiel ESCO ↔ O\*NET** de la Commission européenne,
  qui évite tout mapping manuel ;
- écrire un lecteur ROME `.xlsx` dans `occupation_knowledge/` (aujourd'hui
  contourné par `scripts/build_knowledge_v3.py`) ;
- router ensuite la connaissance par pays plutôt que par version unique.

---

### 9. `DATA` ISCO-08 comme socle international neutre

La connaissance actuelle est française. ISCO-08 (OIT) est le référentiel
international, y compris pour l'Afrique, mais **le fichier n'a pas été obtenu**
(`isco.ilo.org` répond 200, mais les URL de téléchargement historiques sont en
404 ; ILOSTAT est inaccessible depuis ce serveur).

À faire : obtenir la structure ISCO-08, l'ingérer comme taxonomie neutre, et
faire de ROME une surcouche « France » plutôt que le socle.

**À ne pas oublier** : ISCO-08 décrit des métiers *en général*. Il ne remplace
pas des données locales de marché de l'emploi, et il est en anglais.

---

### 10. `DATA` Collecter les données publiques africaines

Sources mesurées le 11/10/2026, toutes accessibles sans clé :

| Source | Contenu |
|---|---|
| World Bank API | chômage, participation féminine, par pays |
| HDX (`data.humdata.org`) | 2 101 jeux « emploi », 4 696 « éducation » |
| GeoNames | villes et localités |
| Overpass (OSM) | écoles, hôpitaux, universités par localisation |
| Wikidata | 2 486 universités africaines |

Inaccessible d'ici : ILOSTAT, open.africa, data.gov.za, Banque africaine.

Contrainte technique : **l'API Overpass répond 406 sans `User-Agent`**. Toute
collecte doit s'identifier, comme déjà fait dans `scripts/fetch_external.py`.

Préférer API et téléchargements en masse au scraping ; si scraping malgré tout :
respecter `robots.txt`, limiter le débit, ne jamais aspirer de données
personnelles.

---

### 11. `DATA` Remplir la table `employer`

La table existe (migration `0003`) et est **vide par construction** : il n'y a
pas encore de source de marché de l'emploi branchée.

La table est volontairement séparée d'`occupation` : un métier est stable et
théorique, un emploi bouge chaque semaine. Les mélanger produirait des
recommandations fausses au bout de trois mois.

Attention à la péremence : toute ligne d'employeur doit porter `observed_at`, et
il faudra une politique d'expiration.

---

## P3 — Architecture et dette

### 12. `CLEAN` 78 modules hors chemin de production : brancher, documenter ou supprimer

**Mesuré au chargement de `main` : 116 modules chargés, 78 non chargés.**

| Groupe | Non chargés |
|---|---|
| `recommendation/` | 20 |
| `domain/` | 19 |
| `occupation_knowledge/` | 8 |
| `learning/` | 7 |
| `psychometrics/` | 3 |
| `semantic/` | 3 |
| `explanation/`, `evaluation/`, `infrastructure/`, `core/`, `workers/` | 2 à 3 chacun |

Trois options à trancher explicitement, module par module :
- **brancher** dans le chemin de requête ;
- **documenter** comme « expérimental, non activé » avec la raison ;
- **supprimer**.

Chaque module inutilisé est de la dette : il donne l'impression que le moteur
fait plus qu'il ne fait. C'est exactement le problème que la pile de scoring a
été construite pour régler — il reste 78 cas.

---

### 13. `OPS` Entraînement des quatre couches apprises

Les couches existent, sont branchées et **déclarent leur inactivité**. Pour les
activer il manque de la donnée, pas du code.

| Couche | Ce qui manque |
|---|---|
| calibration | ≥ 20 observations étiquetées (2 en base) |
| LambdaMART | jeu de requêtes + clics (aucune interaction enregistrée) |
| R-GCN | labels d'arêtes (le graphe existe) |
| bandit | trafic + feedback (exploration risquée sans volume) |

Première brique indispensable : un **collecteur d'interactions** qui enregistre
quels métiers et quelles formations ont réellement été consultés après une
recommandation, pseudonymisé.

---

### 14. `API` Pagination, limites et politique de version d'API

**Suivi de #24.** `/knowledge/occupations` renvoie 1 935 lignes en une réponse.
Aucune pagination, aucune limite de débit, et la stratégie de versionnement
n'est pas écrite.

À faire : pagination par curseur sur les grandes collections, en-têtes de
limitation, et documenter ce qui casse en cas de version majeure.

---

### 15. `ARCH` Séparer inference stateless et workers batch

**Suivi de #15 et #29.** `workers/inference.py` existe et n'est jamais appelé.
L'inférence et le traitement par lots sont dans le même service : le second
peut saturer le premier.

---

### 16. `OPS` CI/CD de déploiement et environnement staging

**Suivi de #23.** Le déploiement est manuel. Aucune chaîne ne construit, ne
teste et ne déploie. Il n'y a pas d'environnement de staging.

À noter : la CI existante ne couvre pas `data-service` (TypeScript) et n'a pas
été mise à jour après l'ajout des nouveaux endpoints.

---

## P4 — Produit et conformité

### 17. `LEGAL` Pages légales et bandeau cookies

**Suivi de #27.** Aucune page mentions légales, politique de confidentialité,
gestion des cookies. Obligatoire dès qu'un site public collecte des données.

---

### 18. `A11Y` Accessibilité WCAG et internationalisation

**Suivi de #26.** Le site respecte `prefers-reduced-motion` (un bug d'affichage
des données en reduced-motion a d'ailleurs été corrigé à ce sujet), mais aucune
audit WCAG n'a été fait.

À faire : audit clavier et lecteurs d'écran, contrastes, navigation sans
souris, puis versionnement des textes (le site n'existe qu'en français alors que
les données externes sont multilingues).

---

### 19. `DOC` Compléter les guides et l'OpenAPI

**Suivi de #30.** Les guides administrateur et utilisateur existent mais ne
couvrent ni les migrations Drizzle, ni les modèles_registry, ni la pile de
scoring. L'OpenAPI est généré automatiquement mais jamais relu.

À compléter également : `docs/atlas` et la procédure de bascule d'une version de
connaissance à une autre.

---

### 20. `WEB` Démonstration du RAG dans l'interface

**Faible priorité, fort effet de démonstration.**

L'API `/v1/orientation/context` fonctionne (rappel@10 = 9/10 sur le corpus
réel) mais n'est visible par personne. Une page où l'on pose une question en
langage naturel et où l'on voit les documents retenus **avec leur provenance**
serait la démonstration la plus parlante du travail réalisé sur la récupération
documentaire.

---

## Ordre suggéré

1. **#22 RGPD** et **#2 sauvegardes** — avant toute mise en production réelle
2. **#4 tests de contrat** — ce qu'on construit n'est pas protégé
3. **#5 observabilité** — sans ça, on ne voit pas les régressions
4. **#9 ISCO-08** puis **#10 données Afrique** — le chantier de fond
5. **#12/modules orphelins** — trancher brancher ou supprimer
6. Le reste