# Traduction des catalogues externes

O*NET et ESCO sont publiés en anglais ; le produit vise le francophone. Les
libellés sont donc traduits par lots, avec deux fournisseurs en chaîne.

```
Gemini (primaire)  ──échec──▶  Groq (repli)  ──échec──▶  libellé d'origine
```

## Pourquoi deux fournisseurs

L'offre gratuite est plafonnée en requêtes/minute. Une ingestion de plusieurs
milliers de libellés sature Gemini et se fait *throttler* (429). Sans repli, la
traduction s'arrête en plein milieu et l'ingestion se termine avec des libellés
mi-anglais. Groq sert de filet.

| | Primaire | Repli |
|---|---|---|
| Fournisseur | Gemini (`generativelanguage.googleapis.com`) | Groq (`api.groq.com`, API compatible OpenAI) |
| Modèle | `gemini-2.5-flash` | `qwen/qwen3.8-27b` |
| Offre gratuite | oui, quotas par minute | oui, quotas par minute |
| Auth | en-tête `x-goog-api-key` | en-tête `Authorization: Bearer` |

## Pourquoi `qwen/qwen3.8-27b` et pas `openai/gpt-oss-*` sur Groq

Les modèles `openai/gpt-oss-20b` / `120b` sont des **modèles à raisonnement** :
sur une traduction, ils consomment tout le budget de tokens à réfléchir et
répondent `content: ""` avec `finish_reason: "length"`. La réponse est
inexploitable. `qwen/qwen3.8-27b` renvoie directement le JSON attendu.

## Garde-fous

- **Clés jamais journalisées ni écrites sur disque** : elles viennent de
  l'environnement et voyagent uniquement dans un en-tête, jamais dans une URL
  (une URL finit dans les logs du proxy).
- **User-Agent explicite** : Groq répond `403` au `Python-urllib/3.12` par
  défaut (Cloudflare 1010). Le fournisseur s'identifie donc comme
  `hashcode-profiling/1.0`.
- **Validation stricte de la réponse** : un lot doit rendre exactement une clé
  par entrée. Une réponse incomplète est **refusée**, pas fusionnée — sinon on
  obtiendrait deux traductions dans une même valeur. Le refus déclenche le repli.
- **Cache disque** (`data/runtime/translation-cache.json`, gitignoré) indexé par
  SHA-256(modèle + cible + texte) : une chaîne déjà payée n'est jamais
  redemandée, quel que soit le fournisseur.
- **Jamais d'exception** : si tous les fournisseurs échouent, le libellé d'origine
  est conservé et le statut reste `none`. Une traduction manquante est un défaut
  visible, pas une panne.

## Tracer la provenance

Chaque enregistrement en base porte le statut de sa traduction :

| `translation_status` | Sens |
|---|---|
| `source` | la donnée source est déjà en français (ROME) |
| `done` | traduite et vérifiée |
| `pending` | file d'attente |
| `failed` | le fournisseur a échoué, le libellé d'origine est conservé |
| `none` | non concernée |

`language` porte la langue du contenu (ISO 639-1) et `original_title` le libellé
d'origine avant traduction — la donnée d'origine n'est jamais perdue.

## Usage

```python
from orientation.config.settings import Settings
from orientation.infrastructure.translation import build_service

service = build_service(Settings())
print(service.active)              # modèle retenu, None si aucune clé
traductions = service.translate(["Registered Nurse", "Data Scientist"])
```

Le service ne lève jamais : en cas d'échec total, `translate()` renvoie le
dictionnaire source inchangé.