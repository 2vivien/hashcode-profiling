# Schéma de données conceptuel

## Profil

    StudentOrientationProfile
      profileVersion
      studentId
      interests[]
      abilities[]
      skills[]
      knowledge[]
      values[]
      environmentPreferences[]
      selfEfficacy[]
      adaptability[]
      schoolTrajectory[]
      experiences[]
      constraints[]
      explorations[]
      feedback[]
      uncertainty{}

## Observation

    OrientationObservation
      id
      dimension
      key
      value
      confidence
      source
      instrument
      instrumentVersion
      observedAt

## Direction

    OrientationDirection
      id
      label
      version
      domains[]
      requiredSkills[]
      optionalSkills[]
      relatedTrainings[]
      relatedOccupations[]
      constraints[]

## Recommandation

    OrientationRecommendation
      id
      directionId
      score
      confidence
      evidence[]
      skillGaps[]
      uncertainties[]
      explorations[]
      modelVersion
      createdAt

## Exploration

    OrientationExploration
      id
      activityId
      directionIds[]
      startedAt
      completedAt
      feedback
      observations[]

## Audit

    RecommendationAudit
      recommendationId
      profileVersion
      modelVersion
      knowledgeVersion
      candidateIds[]
      selectedIds[]
      evidence[]
      createdAt

## PostgreSQL conceptuel

    orientation_profiles
    orientation_observations
    orientation_interests
    orientation_skills
    orientation_values
    orientation_assessments
    orientation_assessment_items
    orientation_trajectories
    orientation_experiences
    orientation_explorations
    orientation_feedback
    orientation_directions
    orientation_direction_skills
    orientation_trainings
    orientation_occupations
    orientation_recommendations
    orientation_recommendation_evidence
    orientation_model_versions
    orientation_knowledge_versions

## Graphe

    (:Student)-[:HAS_INTEREST]->(:Interest)
    (:Student)-[:HAS_SKILL]->(:Skill)
    (:Direction)-[:REQUIRES]->(:Skill)
    (:Training)-[:DEVELOPS]->(:Skill)
    (:Training)-[:LEADS_TO]->(:Direction)
    (:Occupation)-[:REQUIRES]->(:Skill)

## Identifiants

Séparer :

    internalId
    escoId
    onetId
    localId

## Versioning

Une mise à jour de référentiel ne doit pas modifier silencieusement le sens historique d'une recommandation.
