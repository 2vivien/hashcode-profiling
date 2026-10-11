# Otheloo — moteur d'orientation

Le moteur prend le profil d'un élève (ce qu'il aime, ce qu'il sait faire, ses
valeurs) et lui propose **plusieurs directions à explorer** — jamais un métier
unique imposé. Chaque proposition vient avec son score, son niveau de confiance,
et **les compétences à renforcer**.

## État au 11 octobre 2026

Le moteur tourne en production sur <https://profiler.otheloo.com>.

| | |
|---|---|
| Métiers chargés | **1 911** (nomenclature ROME, France Travail) |
| Compétences | **19 479** (taxonomie ROME) |
| Recherche documentaire | **5 967 documents** indexés |
| Contrôles automatiques | 135 tests, tous verts |
| Moteur qui décide du score | un seul : le moteur déterministe |

### Ce qui est réellement en service

- Un profil multidimensionnel (intérêts, capacités, compétences, matières, valeurs).
- Un score de compatibilité calculé par une pondération fixe, **reproductible** :
  le même profil donne toujours le même résultat.
- Une recherche dans les vrais métiers français, avec la source de chaque
  information.
- Un journal de chaque recommandation en base (qui, quoi, quelle version du
  modèle, quelles couches ont joué).

### Ce qui est écrit mais pas en service

Quatre couches plus poussées existent dans le code — calibration, classement
apprentissage, graphe de métiers, exploration automatique. **Elles ne sont pas
actives**, faute d'avoir été entraînées sur des données réelles. Elles le disent
elles-mêmes dans la réponse du moteur : préférer l'ignorance à une fausse
promesse.

### Limite géographique

Les données actuelles sont **françaises**. Le moteur ne prétend pas couvrir
l'Afrique, l'Asie ou les États-Unis. Voir [docs/sources-donnees.md](docs/sources-donnees.md).

## Démarrer

```bash
# Démarrer la pile (base + service de données + moteur)
docker compose up -d

# Charger la connaissance en base
./scripts/db-init.sh v3

# Ouverture
open https://profiler.otheloo.com
```

## Comprendre le moteur

| Si tu veux… | Lis |
|---|---|
| Savoir comment le score est calculé | [docs/moteur.md](docs/moteur.md) |
| Comprendre pourquoi le moteur dit « non entrené » | [docs/engine-stack.md](docs/engine-stack.md) |
| Voir d'où viennent les données | [docs/sources-donnees.md](docs/sources-donnees.md) |
| Comprendre la recherche documentaire | [docs/rag.md](docs/rag.md) |
| Utiliser l'API | [docs/api.md](docs/api.md) |
| Comprendre l'architecture | [docs/architecture.md](docs/architecture.md) |
| Exploiter, déployer, surveiller | [docs/deploiement.md](docs/deploiement.md) |
| Déboguer un mot inconnu | [docs/glossaire.md](docs/glossaire.md) |

## Le glossaire, sans jargon

| Mot du dépôt | Ce que ça veut dire |
|---|---|
| **direction** | Une piste d'orientation (« Ingénierie réseaux »), pas un métier |
| **occupation** | Un métier concret (« Technicien réseaux ») |
| **competence** | Une capacité mobilisable (« Résoudre un incident réseau ») |
| **connaissance** | L'ensemble des données de référence, versionné (v1, v2, v3) |
| **couche** | Une étape du calcul : chacune peut être active ou inactive |
| **RAG** | La capacité à retrouver la bonne information dans les 5 967 documents |
| **déterministe** | Qui donne toujours le même résultat pour la même entrée |

## Règle du dépôt

**Code présent ≠ données présentes ≠ modèle entraîné ≠ modèle validé.**

Un composant qui n'est pas prêt doit le dire, pas laisser croire qu'il
fonctionne. C'est pourquoi la réponse du moteur indique l'état de chaque couche,
et pourquoi `/etat` est alimenté par l'API plutôt que par du texte figé.

## Documentation de conception

Les documents `orientation/00-25` sont la spécification d'origine : vision,
psychométrie, algorithmes, équité, architecture. Ils décrivent l'intention
originale ; **le code et ce README** décrivent ce qui existe.

## Autres documents

| Document | Sujet |
|---|---|
| [SECURITY.md](SECURITY.md) | Sécurité, secrets, quoi faire en cas d'incident |
| [ENVIRONMENTS.md](ENVIRONMENTS.md) | Variables d'environnement, déploiement |
| [RAPPORT-VEILLE.md](RAPPORT-VEILLE.md) | Mesures, risques, feuille de route |