# Documentation

Guides du moteur d'orientation. **Commencez par le [README](../README.md)** si
vous découvrez le projet.

## Par où commencer

| Vous êtes… | Lisez d'abord |
|---|---|
| Quelqu'un de curieux | [Guide utilisateur](user-guide.md) — ce que le moteur propose et pourquoi |
| Un élève ou une famille | [Guide utilisateur](user-guide.md), puis [comment le moteur calcule](moteur.md) |
| Un développeur | [Architecture](architecture.md), puis [API](api.md) |
| Vous déployez | [Déploiement et exploitation](deploiement.md) |
| Curieux des données | [Sources de données](sources-donnees.md) et [Données Afrique](donnees-afrique.md) |
| Vous contribuez | Ce fichier, section « Contribue » |

## Premier niveau — en langage clair

| Document | Sujet |
|---|---|
| [Guide utilisateur](user-guide.md) | Comprendre une recommandation, l'incertitude, les explorations |
| [Comment le moteur calcule](moteur.md) | Les 8 étapes, de la lecture du profil à l'écriture en base |
| [Glossaire](glossaire.md) | Chaque mot du dépôt, expliqué — et les mots à manier avec précaution |
| [Données Afrique](donnees-afrique.md) | Sources publiques disponibles, ce qui répond et ce qui non |

## Deuxième niveau — technique

| Document | Sujet |
|---|---|
| [Architecture](architecture.md) | Les services, la direction des données, les décisions structurantes |
| [API](api.md) | Les 22 endpoints, avec ce que renvoie vraiment chaque réponse |
| [Base de données](data-drizzle.md) | Schéma, migrations, requêtes |
| [Pile de recommandation](engine-stack.md) | Les 5 couches, ce qui est actif et pourquoi |
| [Recherche documentaire (RAG)](rag.md) | Comment le moteur retrouve l'information |
| [Traduction](translation.md) | Traduire les catalogues en anglais vers le français |
| [Sources de données](sources-donnees.md) | D'où viennent les 1 935 métiers, et ce qu'on a écarté |
| [Déploiement et exploitation](deploiement.md) | Démarrer, mettre à jour, surveiller, dépanner |
| [Guide administrateur](admin-guide.md) | Exploiter au quotidien |

## Référentiel

| Document | Sujet |
|---|---|
| [SECURITY.md](../SECURITY.md) | Sécurité, secrets, incident |
| [ENVIRONMENTS.md](../ENVIRONMENTS.md) | Variables d'environnement |
| [RAPPORT-VEILLE.md](../RAPPORT-VEILLE.md) | Mesures, risques, feuille de route |
| [`orientation/`](../orientation/README.md) | Spécification scientifique d'origine (00 → 31) |
| [`orientation-engine/docs/`](../orientation/orientation-engine/docs) | Documents internes du moteur |

> La spécification `orientation/` décrit l'**intention** d'origine. **Le code et
> le README** décrivent ce qui **existe**. Quand ils divergent, croire le code.

## Règle de rédaction

Un composant qui n'est pas prêt doit le dire explicitement. Aucun document ne
décrit une intention comme une réalité, et aucun chiffre n'est écrit en dur
quand il peut être lu depuis l'API — c'est ce qui a permis d'écrire « V1
baseline » sur le site et de découvrir ensuite que la pile existait déjà.

## Contribue

1. Branche, Working tree propre.
2. Écris le code **et** son test.
3. Fais passer les contrôles :
   ```bash
   docker run --rm --user root -e RUFF_CACHE_DIR=/tmp/ruff \
     -v "$PWD/orientation/orientation-engine:/app" -w /app \
     hashcodeprofiling-orientation-engine:latest \
     sh -c "uv run ruff check . && uv run mypy src && uv run pytest -q"

   cd data-service && npx tsc --noEmit
   ```
4. Si le comportement visible change, **mets à jour la documentation** dans le
   même commit.
5. Si tu déplaces le score, dis-le : le baseline est calibré, un changement
   silencieux invalide les comparaisons.

### Convention de messages

```
type(portée) : résumé à l'imparfait, en une ligne

Pourquoi, pas quoi — le diff montre déjà le quoi.
Ce qui est assumé, et ce qui reste ouvert.
```