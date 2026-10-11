# Documentation

Guides du moteur d'orientation. **Commencez par le [README](../README.md)** si
vous découvrez le projet.

## Par où commencer

| Vous êtes… | Lisez d'abord |
|---|---|
| Quelqu'un de curieux | [Guide utilisateur](user-guide.md) — ce que le moteur propose et pourquoi |
| Un développeur | [Comment le moteur calcule](moteur.md) — le parcours complet d'une recommandation |
| Une personne qui déploie | [Guide administrateur](admin-guide.md) |
| Curieux des données | [Sources de données](sources-donnees.md) et [Données Afrique](donnees-afrique.md) |

## Tous les documents

| Document | Sujet | Langue |
|---|---|---|
| [Guide utilisateur](user-guide.md) | Ce que le moteur propose, comment lire une recommandation | clair |
| [Comment le moteur calcule](moteur.md) | Les 8 étapes, de la lecture du profil à l'écriture en base | clair |
| [Données Afrique](donnees-afrique.md) | Sources publiques disponibles, ce qui répond et ce qui non | clair |
| [Pile de recommandation](engine-stack.md) | Les 5 couches, ce qui est actif et pourquoi | technique |
| [Recherche documentaire (RAG)](rag.md) | Comment le moteur retrouve l'information | technique |
| [Traduction](translation.md) | Traduire les catalogues en anglais vers le français | technique |
| [Sources de données](sources-donnees.md) | D'où viennent les 1 911 métiers, et ce qu'on a écarté | technique |
| [Guide administrateur](admin-guide.md) | Déployer, exploiter, surveiller | technique |
| [Base de données](data-drizzle.md) | Schéma, migrations, requêtes | technique |
| [SECURITY.md](../SECURITY.md) | Sécurité et secrets | technique |
| [ENVIRONMENTS.md](../ENVIRONMENTS.md) | Variables d'environnement | technique |

## Deux lectures, deux usages

Les documents marqués **clair** s'écrivent pour être lus par quelqu'un qui ne
connaît pas le projet. Les autres restent techniques : ils décrivent le code et
servent à le maintenir.

## Règle de rédaction

Un composant qui n'est pas prêt doit le dire explicitement. Aucun document ne
décrit une intention comme une réalité, et aucun chiffre n'est écrit en dur
quand il peut être lu depuis l'API.