# Discovery Engine

Le moteur d'orientation Otheloo est un système de **découverte progressive**, pas un système de prescription.

## Règles

1. Aucune réponse ne dit à l'élève qu'il « doit » exercer un métier.
2. Les 40 questions produisent un profil latent multidimensionnel ; les signaux non-RIASEC ne sont pas jetés.
3. Les observations longitudinales peuvent enrichir le profil uniquement avec une provenance et une confiance explicites.
4. Le score retourné est une **compatibilité explicable**, pas une probabilité calibrée.
5. Chaque piste expose les écarts, l'incertitude et des expériences permettant de tester l'hypothèse.
6. Le moteur diversifie les résultats pour explorer plusieurs familles professionnelles.
7. Les données Otheloo comportementales restent séparées des données de référence ESCO/O*NET.

## Catalogue officiel

Le builder consomme les archives officielles ESCO v1.2.1 et O*NET 31.0 sans les versionner dans Git.

Commande :

    cd orientation/orientation-engine
    python scripts/build_occupation_catalog.py --esco-zip /data/esco-v1.2.1-en.zip --onet-zip /data/onet-31.0.zip --language fr --output data/generated/occupations.jsonl

Le résultat contient les identifiants, relations skills, preuves, Job Zones, signaux O*NET, tâches et métiers liés. Les formations concrètes ne sont pas inventées : elles devront être reliées à un catalogue de formations Otheloo ou à une source de learning opportunities.

## Couche de sortie

`POST /occupation-v2/discover` agrège les métiers compatibles en directions professionnelles par famille ISCO-08. Chaque direction contient :
- compatibilité ;
- confiance ;
- incertitude ;
- raisons ;
- écarts ;
- expériences à tester ;
- quelques métiers représentatifs.

Les futures versions ML peuvent apprendre sur les choix réels Otheloo, mais aucune donnée comportementale fictive ne doit être introduite pour entraîner V3/V4/V5.
