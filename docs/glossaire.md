# Glossaire

Les mots du dépôt, expliqués. Le jargon du domaine et celui du code ne sont pas
la même chose : les deux sont listés.

## Le métier

| Mot | Signifie | Ne signifie pas |
|---|---|---|
| **élève / usager** | la personne dont on construit le profil | n'est pas identifié nominativement : tout passe par `student_ref` |
| **profil** | ce qu'on sait : intérêts, capacités, compétences, matières, valeurs, chacun avec une confiance | ce n'est pas un dossier, ni un judgment |
| **direction** | une piste d'orientation (« Ingénierie réseaux ») | ce n'est pas un métier, et surtout pas un verdict |
| **occupation** | un métier concret et nommé (« Technicien / Technicienne réseaux ») | n'est pas une entreprise, ni une offre d'emploi |
| **compétence** | une capacité mobilisable, tirée de la taxonomie ROME | ce n'est pas un diplôme |
| **formation** | un parcours vers une direction, avec niveau et durée | ce n'est pas une inscription |
| **compatibilité** | score entre 0 et 1 entre un profil et une direction | ce n'est pas une probabilité de réussite |
| **incertitude** | ce qu'on ne sait pas sur un élève | ce n'est pas un défaut de l'élève |
| **écart de compétence** | où l'élève est sous le niveau attendu | ce n'est pas un blocage : c'est une feuille de route |
| **exploration** | une piste voisine, à considérer et non à retenir | n'est pas une recommandation secondaire |

## Les données

| Mot | Signifie |
|---|---|
| **connaissance** | l'ensemble des données de référence, versionné : v1, v2, v3 |
| **version de connaissance** | un instantané complet et daté ; on bascule de l'un à l'autre |
| **manifeste** | le fichier qui décrit une version : origine, date, empreintes, volumes |
| **RÉFÉRENTIEL** | une nomenclature officielle : ROME (France), O\*NET (États-Unis), ESCO (UE), ISCO (OIT) |
| **nomenclature** | la liste officielle des métiers d'un pays, avec ses codes |
| **taxonomie** | une classification par nature (par exemple, les compétences par domaine) |
| **périmètre / couverture** | **quels pays, quelles langues** une version couvre — à toujours vérifier |
| **provenance** | d'où vient une information : source, version, licence |
| **empreinte SHA-256** | l'empreinte d'un fichier téléchargé, pour prouver qu'il n'a pas changé |
| **curation** | une donnée écrite à la main plutôt que téléchargée |
| **pseudonymisation** | remplacer l'identité par une référence (`student_ref`) — pas l'anonymat |

## Le moteur

| Mot | Signifie |
|---|---|
| **moteur** | le service qui transforme un profil en recommandations |
| **couche** | une étape du calcul ; chacune est active ou inactive, et **le dit** |
| **couche apprise** | une étape qui utilise un modèle entraîné sur des données |
| **artifact** | le fichier produit par un entraînement : sans lui, la couche est inactive |
| **registre de modèles** | l'inventaire des artifacts, avec version, date et métriques |
| **entraînement** | produire un modèle à partir de données étiquetées |
| **calibration** | convertir un score en probabilité, après validation sur des données réelles |
| **déterministe** | qui donne **toujours** le même résultat pour la même entrée |
| **reproductible** | que l'on peut refaire et obtenir le même résultat |
| **audit** | la trace : qui, quoi, avec quelles versions |
| **MMR** | rééquilibrage qui évite que les 3 premiers résultats soient 3 variantes du même métier |
| **skill gap** | écart entre le niveau actuel et le niveau attendu |

## La récupération documentaire

| Mot | Signifie |
|---|---|
| **RAG** | retrouver la bonne information dans un corpus pour répondre ou expliquer |
| **document** | un fragment indexable, toujours rattaché à sa source |
| **chunk** | un fragment de document |
| **index vectoriel** | les vecteurs de tous les documents, pour comparer par sens |
| **embedding** | une liste de nombres qui représente le sens d'un texte |
| **cosinus** | la mesure de proximité entre deux vecteurs (de 0, pas proche, à 1, identique) |
| **BM25** | une recherche par mots exacts, classée par pertinence — sans réseau, sans clé |
| **fusion RRF** | combiner deux classements **par rang**, pas par score |
| **rappel@k** | en combien de résultats pertinents on tombe dans les k premiers |
| **contexte** | le bloc de texte transmis au modèle, avec sa provenance et son budget |
| **budget de tokens** | la taille maximale du contexte ; ce qui dépasse est **dit**, pas coupé en silence |

## Les mots à manier avec précaution

| Mot | Pourquoi |
|---|---|
| **universel** | aucune source n'est universelle ; ISCO-08 est le référentiel le plus large, pas international dans le sens de « vraie partout » |
| **prêt** | demander : prêt à être challengé, prêt à décider, ou prêt pour la production ? |
| **entraîné** | un modèle sans artefact n'est pas entraîné, même si le code existe |
| **temps réel** | l'index RAG met 1,5 s à se construire à froid ; ce n'est pas du temps réel |
| **IA** | dire *quelle* IA : un modèle appelé par API, ou un calcul déterministe ? |

## Abréviations

| Sigle | Signifie |
|---|---|
| **API** | interface programmatique — ici du JSON sur HTTP |
| **CLI** | commande en ligne |
| **CI** | intégration continue — les contrôles automatiques |
| **RGPD** | règlement européen sur les données personnelles |
| **DPIA** | analyse d'impact, obligatoire pour un profilage à grande échelle |
| **CEFR / CECRL** | cadre européen commun de référence pour les langues (A1 → C2) |
| **ISCO** | classification internationale des métiers, de l'OIT |
| **CC BY** | licence Creative Commons : réutilisation avec attribution |
| **SHA-256** | empreinte de fichier |
| **SVG** | image vectorielle — nette à toute taille |
| **BM25 / RRF / MIRT / 2PL** | algorithmes, détaillés dans les documents techniques |