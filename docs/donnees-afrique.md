# Données publiques : ce qui est accessible, pays par pays

Mesuré le **11 octobre 2026** depuis le serveur de production. Chaque ligne
correspond à un test HTTP réel, pas à une supposition.

## Le principe d'abord

La plupart de ce qu'on cherche **n'a pas besoin de scraper**. L'open data et les
API sont plus rapides, plus fiables et sans risque juridique. Le scraping n'est
utile que pour ce qui n'est publié nulle part.

Ordre de préférence :
1. **API officielle** (World Bank, HDX)
2. **téléchargement en masse** (GeoNames)
3. **requête géographique** (Overpass / OpenStreetMap)
4. **scraping** — en dernier recours, et seulement si `robots.txt` l'autorise

## Ce qui répond aujourd'hui

| Source | Test | Ce qu'on en tire | Accès |
|---|---|---|---|
| **World Bank API** | ✅ 200 | chômage (SL.UEM.TOTL.ZS), participation féminine (SL.TLF.CACT.ZS), par pays | gratuit, sans clé |
| **HDX** | ✅ 200 | 2 101 jeux « emploi », 4 696 « éducation », 640 « skills », 165 « formation professionnelle » | API CKAN |
| **GeoNames** | ✅ 200 | villes et localités de tous les pays | dump gratuit |
| **Overpass (OSM)** | ✅ 200 | écoles, universités, hôpitaux **par localisation** | gratuit, sans clé |
| **Wikidata SPARQL** | ✅ 200 | 2 486 universités africaines classées | gratuit |
| ROME (France Travail) | ✅ 200 | 1 911 métiers français | xlsx |
| data.gouv.fr | ✅ 200 | datasets français | API |

## Ce qui ne répond pas d'ici

| Source | Test | Contournement |
|---|---|---|
| ILOSTAT | ❌ 403 / DNS | passer par un miroir ou demander un accès |
| open.africa | ❌ 403 | idem |
| data.gov.za (Afrique du Sud) | ❌ DNS | idem |
| Banque africaine de développement | ❌ 403 | idem |
| ILO ISCO-08 (PDF) | ❌ 404 sur les URL historiques | `isco.ilo.org` répond, il faut trouver le bon chemin |

## Une découverte qui vaut d'être notée

L'API **Overpass répond 406 sans `User-Agent`** et fonctionne avec. C'est
exactement le même piège que Groq (403 avec le `User-Agent` par défaut de
Python).

**Toute collecte doit définir un User-Agent identifié.** C'est écrit dans
`scripts/fetch_external.py` (`USER_AGENT`), et il faudra le faire pareil pour
tout nouveau collecteur.

## Ce que chaque source peut alimenter

| Besoin | Source la plus adaptée |
|---|---|
| Liste de métiers | ISCO-08 (à obtenir) + classifications nationales |
| Écoles, formations, hôpital | Overpass / OSM + Wikidata |
| Où travailler (géographie) | GeoNames + Overpass |
| État du marché du travail | World Bank + HDX |
| Compétences par métier | O*NET (anglais) à traduire |

## Deux pièges à éviter

**1. Confondre « taxonomie » et « marché ».** ISCO-08 est universel, mais il
décrit des métiers *en général*. Un électricien d'Abidjan et un électricien de
Lyon n'ont ni les mêmes contraintes réglementaires, ni les mêmes débouchés. Une
taxonomie internationale ne remplace pas des données locales.

**2. La qualité du français.** O*NET et ISCO-08 sont en anglais. La traduction
automatique existe (voir `docs/translation.md`) mais une fiche métier mal
traduite est pire qu'une fiche absente : elle donne une fausse assurance.
D'où le statut `translation_status` dans la base.

## Modèle de données recommandé

Deux tables à ne pas confondre :

```
occupation   ← le métier        (nom, compétences, code ISCO)
employer     ← qui recrute      (organisation, lieu, volume, date)
```

Ce sont deux collecteurs de nature différente : le premier est statique et
théorique, le second bouge chaque semaine et se périme vite. Les mélanger
produirait des recommandations fausses au bout de trois mois.