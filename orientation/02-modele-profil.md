# Modèle du profil longitudinal

## Structure

    StudentOrientationProfile
    ├── interests
    ├── abilities
    ├── skills
    ├── knowledge
    ├── values
    ├── environmentPreferences
    ├── selfEfficacy
    ├── adaptability
    ├── schoolTrajectory
    ├── experiences
    ├── constraints
    ├── explorations
    ├── feedback
    └── uncertainty

## Observation atomique

Une observation doit idéalement contenir :

    value
    confidence
    source
    timestamp
    instrument
    instrumentVersion

Exemple conceptuel :

    dimension = self_efficacy
    key = mathematics
    value = 0.62
    confidence = 0.74
    source = student_questionnaire

## Preuves de compétence

Une compétence doit être distinguée selon son origine :

- declared : l'élève la déclare ;
- assessed : elle est évaluée ;
- observed : elle est observée dans une activité ;
- inferred : elle est inférée.

Une compétence inférée ne doit pas être traitée comme une compétence évaluée.

## Trajectoire

Conserver chaque observation scolaire :

- matière ;
- période ;
- valeur ;
- échelle ;
- source ;
- contexte disponible.

Calculer ensuite :

- moyenne ;
- tendance ;
- variance ;
- volatilité ;
- momentum ;
- régularité.

## Expériences

Chaque exploration devient une observation longitudinale :

    hypothèse
       ↓
    activité
       ↓
    comportement
       ↓
    feedback
       ↓
    mise à jour

Exemple :

    avant : intérêt data = 0.61
    après : intérêt data = 0.79
    avant : confiance = 0.48
    après : confiance = 0.66

## Versionnement

Chaque profil calculé référence :

- profileVersion ;
- questionnaireVersion ;
- knowledgeVersion ;
- modelVersion ;
- timestamp.

Une recommandation historique doit rester reproductible.

## Incertitude

Un profil peut dire :

    mathématiques = 0.61
    confiance = 0.72

mais aussi :

    programmation = inconnu
    confiance = faible

« Inconnu » est une information utile.

## Profil exemple

### Investigateur–Social

- Investigative : forte ;
- Social : forte ;
- curiosité : forte ;
- résolution de problèmes : forte ;
- sciences : progression positive ;
- mathématiques : intermédiaire et en progression ;
- aide aux autres : forte ;
- autonomie : moyenne.

### Sortie

Le moteur produit des directions et non un verdict.

Il peut afficher :

    Sciences et santé
    Ingénierie et technologies
    Informatique et données
    Recherche
    Enseignement scientifique

puis expliquer pourquoi chacune apparaît.
