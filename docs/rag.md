# RAG et assemblage de contexte

Le moteur ne-score pas sur du texte libre : il score sur des dimensions
normalisées. Un RAG sert donc à deux choses, pas une :

1. **répondre à une question en langage naturel** sur la connaissance réelle
   (1 935 métiers ROME, 19 479 compétences) ;
2. **fournir un contexte sourcé** à un modèle ou à un humain, pour expliquer
   d'où vient une recommandation.

## État de départ honnête

Le module `semantic/` existait déjà (embeddings, index vectoriel, matcher) mais
**n'était appelé nulle part**, et son encodeur dépend de `sentence_transformers`,
absent des dépendances : il ne pouvait pas fonctionner. Ce n'est pas une
amélioration de ce module, c'est une réécriture utilisable.

## Architecture

```
Connaissance (v3)
   └─ build_documents ─▶ Documents (direction / occupation / competence / formation)
                            └─ HybridRetriever
                                 ├─ BM25          (lexical, déterministe, sans réseau)
                                 └─ embeddings    (cosinus)
                                 └─ fusion RRF ─▶ RetrievedDocument
                                     └─ ContextBuilder ─▶ ContextPack (budget + provenance)
```

| Module | Rôle |
|---|---|
| `rag/documents.py` | transforme les objets métier en documents, garde la provenance |
| `rag/lexical.py` | BM25 (écrit à la main : ~150 lignes valent mieux qu'une dépendance) |
| `rag/embedding.py` | `HashingEmbedder` (local, gratuit) et `GeminiEmbedder` (optionnel) |
| `rag/retriever.py` | fusion des rangs réciproques (RRF) |
| `rag/context.py` | budget de tokens, plafond par type, rendu sourcé |
| `rag/service.py` | façade, mémoïsation par process, cache disque |

## Pourquoi la fusion RRF et pas une somme de scores

Les deux voies ne sont pas comparables : un score BM25 vit sur une autre échelle
qu'un cosinus. Additionner les scores bruts donnerait le poids au fournisseur le
plus bavard. La fusion RRF combine les **rangs** (`1/(k+rang)`), ce qui est
robuste aux échelles.

## Quel embedder, et pourquoi pas Gemini par défaut

Mesuré le 2026-10-10 : l'offre gratuite Gemini se fait **throttler (429)** dès
quelques centaines de documents. Indexer 6 000 textes y est donc inexploitable,
alors qu'une requête unique par utilisateur passerait sans problème.

- **par défaut** : `HashingEmbedder` — hash de n-grammes projeté en 512
  dimensions. Ce n'est **pas** un modèle appris : c'est un filet, déterministe,
  gratuit, sans réseau. Il suffit à la Fusion BM25 pour faire le gros du travail.
- **optionnel** : `OTHELOO_RAG_EMBEDDER=gemini` pour un vrai modèle
  (`gemini-embedding-001`, 3072 dimensions). À n'utiliser qu'avec du quota.

Si l'indexation échoue sur quota, le service bascule automatiquement en local
plutôt que de rendre la page indisponible.

> Note : `text-embedding-004` est **retiré** de l'API Gemini. Les modèles
> d'embedding publiés sont désormais `gemini-embedding-001` et `-2`.

## Règles de construction du contexte

1. **Budget explicite.** On ne déborde jamais en silence : si le budget est
   atteint, `dropped` dit combien de documents ont été écartés.
2. **Jamais de troncature.** Un document entre en entier ou pas du tout — un
   contexte coupé en milieu de phrase est pire qu'absent.
3. **Provenance obligatoire.** Chaque bloc porte `kind`, `doc_id`, `source` et
   `source_version` : un contexte non vérifiable ne sert à rien.
4. **Déterminisme.** Le tri départage par score puis par identifiant, jamais par
   l'ordre d'un dictionnaire. Même entrée → même sortie.

## Mesures

Corpus réel : **5 967 documents** (12 directions, 1 935 métiers, 4 000 compétences
échantillonnées, 20 formations).

| Requête (langage naturel) | 1er résultat |
|---|---|
| « je veux travailler avec les réseaux » | Technicien / Technicienne réseaux mobiles |
| « comment devenir infirmier » | Infirmier / Infirmière de prévention |
| « devenir développeur web » | Développeur / Développeuse web |
| « travail dans la restauration » | Directeur / Directrice de la restauration |
| « j'aime les animaux » | Éleveur / Éleveuse d'animaux sauvages |
| « piloter une équipe » | Chef / Cheffe d'équipe et d'atelier |

**Rappel@10 = 9/10** sur ce jeu d'évaluation. Le lexical seul obtient aussi 9/10,
mais sur deux questions différentes : l'hybride gagne sur « j'aime les animaux »
(par Distance morphologique), le lexical seul gagne sur « construire des ponts ».

**Ce que je n'améliore pas :** sur une question très reformulée (« construire
des ponts »), le premier résultat hybride reste faible (« responsable des
attractions »). C'est la limite assumée d'un embedder par hachage face aux
paraphrases : sans clé Gemini ou de quota, on n'a pas de sémantique apprise.

| Coût mesuré | Valeur |
|---|---|
| Indexation à froid | 1,5 s |
| Index mémoïsé (2e appel) | 0,001 s |
| 1re requête API après redémarrage | 2,5 s |
| Requête suivante | 67 ms |
| Cache disque (float16 + base64) | 8,2 Mo |

## API

```bash
curl "https://profiler.otheloo.com/v1/orientation/rag/stats"
curl "https://profiler.otheloo.com/v1/orientation/context?query=devenir+infirmier&k=5&budget=800"
```

La réponse contient le contexte **rendu** (injectable tel quel dans un prompt),
le contexte **structuré**, et les statistiques d'index.

## Ce qui n'est pas fait

- Le RAG **n'entre pas dans le score** des recommandations. Le calibrage du
  baseline est sur 24 occupations curées ; y brancher du lexique retrieval
  changerait les scores sans revalidation. Il est câblé pour l'**explication**
  et l'**answered query**, pas pour le scoring.
- Pas de réécriture de requête ni de reformulation multi-tours.
- Pas de citation fine : un bloc = un document entier, pas un passage.