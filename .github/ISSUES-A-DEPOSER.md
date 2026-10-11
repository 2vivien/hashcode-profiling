# Issues à déposer sur GitHub

> Le token GitHub utilisé jusqu'ici a été révoqué (HTTP 401). Ces issues sont
> rédigées ici, prêtes à copier dans GitHub ou à créer via `gh issue create`.

---

## 1. `DATA` La couverture géographique est française — documenter la limite et viser l'Afrique

**Priorité : haute.** Le moteur est présenté sans préciser que ses données ne
couvrent que la France. C'est le risque de déception le plus élevé du projet.

**État mesuré (11/10/2026)**

| Source | Couverture | Statut |
|---|---|---|
| ROME | France | ✅ 1 911 métiers chargés |
| O*NET 31.0 | États-Unis | ⬇️ téléchargé, non ingéré |
| ESCO 1.2.1 | Union européenne | ⬇️ page identifiée, non ingérée |
| ISCO-08 (OIT) | **international, y c. Afrique** | ❌ pas de fichier obtenu |

Vérifié ce jour : aucun des trois datasets chargés ne contient de métiers
africains. Wikidata n'en compte que ~26 avec libellé français — inexploitable.

**À faire**
1. Afficher la couverture géographique dans `/system/info` et sur le site.
2. Ajouter un `scope` (pays + langue) au manifeste de connaissance.
3. Trouver et charger ISCO-08 comme **taxonomie neutre**, ROME devenant une
   surcouche « France » plutôt que le socle.
4. Documenter ce que ISCO-08 **ne** couvre pas : les poids de scoring sont
   calibrés sur des compétences françaises, la taxonomie internationale ne
   suffira pas.

---

## 2. `DATA` Collecter les données publiques africaines (sans scraper quand c'est possible)

**Priorité : haute.** Testé le 11/10/2026, ces sources répondent aujourd'hui :

| Source | Test | Contenu | Accès |
|---|---|---|---|
| **World Bank API** | ✅ 200 | chômage, participation féminine, par pays | gratuit, sans clé |
| **HDX** (`data.humdata.org`) | ✅ 200 | 2 101 jeux « emploi », 4 696 « éducation » | API CKAN |
| **GeoNames** | ✅ 200 | villes et localités (dump gratuit) | téléchargement |
| **Overpass / OSM** | ✅ 200 **avec User-Agent** | écoles, hôpitaux, universités par lieu | gratuit, sans clé |
| **Wikidata** | ✅ 200 | 2 486 universités africaines | SPARQL |
| ILOSTAT | ❌ 403 / DNS | statistiques de l'emploi | inaccessible d'ici |
| open.africa | ❌ 403 | portail | inaccessible d'ici |

**Découverte technique** : l'API Overpass répond **406 sans User-Agent**, comme
Groq qui répond 403 sans User-Agent. Toute collecte doit en définir un.

**À faire**
- Ajouter World Bank, HDX, GeoNames et Overpass à `external_sources.json`.
- Privilégier les API et les dumps : le scraping est le dernier recours, il pose
  des problèmes juridiques et de charge sur les serveurs.
- Si scraping malgré tout : respecter `robots.txt`, limiter le débit, identifier
  le client, et ne jamais aspirer de données personnelles.
- Modèle de données : deux tables séparées, `occupation` (métier) et
  `employer` (qui recrute, où, combien) — ce sont deux collecteurs de nature
  différente.

---

## 3. `SECU` RGPD et mineurs : finalité, base légale, consentement, DPIA

**Priorité : critique.** Issue #22. On traite des profils d'élèves, donc
potentiellement des mineurs. Aucun de ces points n'est traité dans le dépôt.

À traiter : finalité et base légale, consentement et retrait, durée de
conservation, droit d'effacement, DPIA, information des familles.

Note technique : les observations et les audits sont pseudonymisés par
`student_ref`, mais rien ne documente la politique de rétention ni le chemin de
suppression d'un élève.

---

## 4. `TEST` Couvrir par des tests de contrat les endpoints récents

**Priorité : haute.** `layers`, `/context`, `/rag/stats`,
`/assessment-v1/ability` ont été ajoutés sans un seul test de contrat. Une
régression silencieuse passerait.

À faire : figer la forme des réponses, vérifier qu'un `layers` vide ne casse
pas le front, et tester le comportement quand le RAG est indisponible.

---

## 5. `OBS` Observabilité : métriques Prometheus et logs structurés

**Priorité : haute.** Issue #18. Le moteur est en production sans `/metrics`,
sans logs structurés et sans alerte.

Priorité auminimum : latence des endpoints, durée d'indexation RAG, taux
d'échec par couche du moteur, et alerte si le RAG tombe.

---

## 6. `OPS` Sauvegardes automatiques et procédure de restauration

**Priorité : haute.** Issue #19. La base contient les profils, les
recommandations et les audits. Aucune sauvegarde automatique n'est en place, et
aucune restauration n'a jamais été testée.

À faire : sauvegarde quotidienne, conservation définie, **et surtout** une
restauration réellement vérifiée sur un environnement jetable.

---

## 7. `DATA` Terminer l'ingestion ESCO et O*NET (suite de #21)

**Priorité : moyenne.** Les archives sont téléchargées et traçables, mais
l'ingestion O*NET n'est pas faite et le crosswalk officiel ESCO↔O*NET n'est pas
exploité. Il manque aussi un lecteur pour les fichiers ROME en `.xlsx`
aujourd'hui contournés par le script de construction.

---

## 8. `CLEAN` 78 modules hors chemin de production : brancher ou supprimer

**Priorité : moyenne.** Mesuré au chargement de `main` : 116 modules chargés,
**78 non chargés**. Parmi eux, `domain/` (19), `recommendation/` (20),
`occupation_knowledge/` (8), `learning/` (7).

Chaque module inutilisé est de la dette : il donne l'impression que le moteur
fait plus qu'il ne fait. Trois options, à trancher explicitement :
brancher, documenter comme « expérimental non activé », ou supprimer.

---

## 9. `UX` Page de démonstration du RAG (option B)

**Priorité : basse.** L'API `/context` fonctionne (rappel@10 = 9/10) mais
n'est visible par personne. Une page où l'on pose une question et où l'on voit
les documents retenus avec leur provenance est la démonstration la plus parlante
du travail réalisé.

---

## 10. `OPS` Corriger les 2 erreurs ruff restantes dans `scripts/`

**Priorité : basse.** `uv run ruff check .` signale encore 2 erreurs dans
`scripts/` (non corrigées après les derniers ajouts).