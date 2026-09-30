# Fairness, sécurité et garde-fous

## Risque

L'orientation peut influencer :

- études ;
- ambitions ;
- confiance ;
- décisions familiales ;
- trajectoire scolaire.

Le moteur doit donc être un outil d'exploration.

## Interdictions fonctionnelles

Ne jamais :

- déclarer un enfant incapable ;
- prédire son échec ;
- imposer un métier ;
- fermer automatiquement une voie ;
- utiliser une corrélation comme causalité ;
- transformer un score en identité ;
- présenter un modèle expérimental comme une vérité.

## Données protégées

Définir pour chaque variable :

- utilisée dans le modèle ;
- utilisée uniquement pour audit ;
- interdite ;
- nécessaire pour une contrainte légale explicite.

Une donnée peut être utile à l'audit de biais sans entrer dans le score.

## Fairness

Selon le cas d'usage, tester :

### Demographic parity

    P(Yhat=1 | A=a)

### Equalized odds

    P(Yhat=1 | Y=y, A=a)

### Calibration

Les probabilités doivent conserver une signification comparable.

Ces critères peuvent entrer en tension ; il faut documenter le choix.

## Biais possibles

- historique ;
- culturel ;
- socio-économique ;
- familial ;
- de familiarité ;
- de popularité ;
- de disponibilité des données.

## Compatibilité ≠ accessibilité

Ne pas apprendre :

    « cet élève ne vise pas cette formation »

simplement parce qu'il n'y a pas accès.

Séparer :

    compatibilité
    accessibilité
    connaissance
    opportunité

## Boucle auto-réalisatrice

Danger :

    modèle → sciences
          ↓
    élève ne voit plus arts
          ↓
    données deviennent scientifiques
          ↓
    modèle renforce sciences

Contre-mesures :

- diversification ;
- exploration ;
- découverte ;
- contre-factuels ;
- possibilité de contester ;
- mesure de couverture.

## Confidentialité

Conserver seulement les données nécessaires.

Protéger :

- données scolaires ;
- psychométrie ;
- feedback ;
- historique d'exploration.

## Audit

Pour chaque recommandation :

    profileVersion
    modelVersion
    knowledgeVersion
    inputSnapshot
    candidateSet
    ranking
    evidence
    timestamp

## Human-in-the-loop

Le moteur fournit :

- hypothèses ;
- informations ;
- expériences ;
- explications.

Il ne prend pas seul les décisions importantes.
