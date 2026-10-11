# Comment le moteur calcule une recommandation

Ce document explique le calcul **sans jargon**, en suivant l'ordre réel des
étapes. Chaque étape peut être vérifiée dans la réponse de l'API.

## Exemple concret

Un élève déclare : j'aime chercher (`investigative` 0.8), je suis bon en logique
(`logical` 0.75).

Voici ce que le moteur fait, dans l'ordre.

---

## Étape 1 — Lire le profil

Le profil rassemble ce que l'élève a dit, avec un **niveau de confiance** pour
chaque information.

> Pourquoi la confiance compte : une réponse à la première question d'un
> questionnaire ne vaut pas une conviction. Le moteur ne les traite pas pareil.

## Étape 2 — Proposer des directions candidates

Le moteur ne garde pas les 12 directions : il élimine celles qui n'ont aucun
rapport avec le profil. Un élève orienté « arts » ne se voit pas proposer
« comptabilité » en fin de liste.

## Étape 3 — Écarter ce qui est impossible

Trois filtres, dans cet ordre :
- **accessibilité** — la formation est-elle accessible depuis le niveau actuel ?
- **exigences** — des prérequis obligatoires manquent-ils ?
- **qualité des données** — a-t-on assez d'information fiable pour se prononcer ?

## Étape 4 — Comparer profil et direction

C'est le cœur. Le moteur compare **9 dimensions** :

| Dimension | Ce qu'elle mesure |
|---|---|
| Intérêts | Le profil aime-t-il ce que la direction propose ? |
| Capacités | Les capacités déclarées correspondent-elles aux exigences ? |
| Compétences | Le niveau de compétence suffit-il ? |
| Valeurs | Les valeurs de l'élève concordent-elles ? |
| Matières | Les matières réussies sont-elles utiles ? |
| Auto-efficacité | L'élève se sent-il capable de le faire ? |
| Adaptabilité | Le projet tient-il compte des changements ? |
| Environnement | Le cadre de travail convient-il ? |
| Trajectoire | Le chemin est-il cohérent avec l'historique ? |

**Le poids effectif d'une dimension = son poids × la confiance de la donnée.**

Exemple : si les intérêts pèsent 15 % mais que l'élève n'a répondu qu'une fois
(софиance 0.3), le poids réel de cette dimension tombe à 4,5 %.

### La règle d'or

> **Une information absente ne devient jamais un zéro.**
> Elle devient une **incertitude**, affichée à part.

C'est ce qui distingue le moteur d'un calcul classique : un élève qui n'a pas
répondu à la question « matières » n'est pas pénalisé, il est signalé comme
moins documenté.

## Étape 5 — Mesurer les écarts de compétences

Pour chaque direction, le moteur liste les compétences où l'élève est en dessous
du niveau attendu. Elles ne bloquent pas la proposition — elles deviennent la
**feuille de route**.

## Étape 6 — Calculer la compatibilité

Les 9 dimensions sont pondérées, la pénalité d'écart est soustraite, et le
résultat est ramené entre 0 et 1.

À partir d'ici, **les couches apprises pourraient intervenir**. Elles ne le font
pas aujourd'hui : elles sont branchées mais inactives. Voir
[engine-stack.md](engine-stack.md).

## Étape 7 — Classer puis diversifier

Deux étapes distinctes, souvent confondues :
- **classer** — le meilleur score d'abord ;
- **diversifier** — éviter que les 3 premiers résultats soient 3 variantes du
  même métier (MMR).

## Étape 8 — Expliquer et tracer

Chaque recommandation contient :
- les **faits** qui l'ont produite (pas une justification générique) ;
- les **parcours de métiers** concrets ;
- les **formations** accessibles ;
- les **pistes d'exploration** alternatives.

Et l'ensemble est écrit en base : on peut, plus tard, dire qu'une recommandation
donnée a été produite **sans** modèle entraîné.

---

## Récapitulatif

```
profil
  ↓  (confiance associée à chaque donnée)
candidats            9 dimensions comparées
  ↓
filtres              accessibilité, exigences, qualité
  ↓
compatibilité        poids × confiance − écart de compétences
  ↓
couches apprises     calibration, classement, graphe, bandit
  ↓                  (toutes inactives aujourd'hui)
classement + diversification
  ↓
explication + métier + formations + exploration
  ↓
écriture en base     journal complet, y compris l'état des couches
```

## Vérifier par soi-même

```bash
curl -s -X POST https://profiler.otheloo.com/v1/orientation/recommendations \
  -H "Content-Type: application/json" \
  -d '{"student_id":"demo","interests":{"investigative":0.8},"abilities":{"logical":0.75}}'
```

Dans la réponse :
- `candidates[].score_breakdown` → le détail des 9 dimensions
- `candidates[].skill_gaps` → les compétences à renforcer
- `candidates[].occupation_paths` → les métiers concrets (issus du ROME)
- `layers` → l'état réel de chaque couche du moteur