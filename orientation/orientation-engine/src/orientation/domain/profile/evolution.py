"""Évolution longitudinale du profil.

Deux mécanismes, tous deux vérifiables et testables :

1. **Observations** : fusion pondérée par la précision (poids = confiance x fiabilité
   de la source). Une observation ``unknown`` ou ``contradictory`` est ignorée :
   l'absence de donnée reste de l'incertitude, jamais un zéro.

2. **Feedback** : signal faible et réversible. On rapproche les intérêts de la
   direction concernée d'un petit pas (``rate``), sans jamais réécrire le profil.
"""

from __future__ import annotations

from collections.abc import Sequence

from orientation.contracts.common import DataState, Observation, SourceType
from orientation.contracts.direction import Direction
from orientation.contracts.profile import StudentProfile, StudentSkill

DIMENSIONS = (
    "interests",
    "abilities",
    "values",
    "subjects",
    "self_efficacy",
    "adaptability",
    "environment",
    "trajectory",
)

# Fiabilité de la source : une mesure évaluée pèse plus qu'une déclaration.
RELIABILITY: dict[SourceType, float] = {
    SourceType.ASSESSED: 1.0,
    SourceType.OBSERVED: 0.85,
    SourceType.DECLARED: 0.6,
    SourceType.INFERRED: 0.5,
}

POSITIVE_FEEDBACK = frozenset({"pertinent", "interessant", "deja_explore", "je_veux_en_savoir_plus", "relevant"})
NEGATIVE_FEEDBACK = frozenset({"pas_pertinent", "rejete", "pas_interesse", "incompris"})

FEEDBACK_RATE = 0.12


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def _next_version(version: str) -> str:
    tail = version.rsplit("v", 1)[-1]
    return f"v{int(tail) + 1}" if tail.isdigit() else f"{version}.1"


def merge_value(
    old_value: float | None,
    old_confidence: float,
    new_value: float,
    new_confidence: float,
    reliability: float,
) -> tuple[float, float]:
    """Fusion pondérée par la précision + confiance par bruit-OR."""
    precision = _clamp(new_confidence) * reliability
    if old_value is None or old_confidence <= 0:
        return _clamp(new_value), _clamp(precision)
    total = old_confidence + precision
    if total <= 0:
        return _clamp(new_value), _clamp(precision)
    merged = (old_value * old_confidence + new_value * precision) / total
    confidence = 1 - (1 - _clamp(old_confidence)) * (1 - precision)
    return _clamp(merged), _clamp(confidence)


class ProfileEvolutionService:
    """Fait évoluer un profil versionné à partir d'observations et de feedbacks."""

    def apply_observations(self, profile: StudentProfile, observations: Sequence[Observation]) -> StudentProfile:
        prior = profile.assessment_confidence
        dimensions: dict[str, dict[str, float]] = {name: dict(getattr(profile, name)) for name in DIMENSIONS}
        skills: dict[str, StudentSkill] = {skill.skill_id: skill for skill in profile.skills}
        applied = 0
        boost = 1.0

        for observation in observations:
            if observation.state is not DataState.KNOWN:
                continue
            reliability = RELIABILITY.get(observation.source, 0.5)
            value = observation.value

            if observation.dimension == "skills" and isinstance(value, dict):
                for skill_id, raw in value.items():
                    if not isinstance(raw, (int, float)):
                        continue
                    existing = skills.get(str(skill_id))
                    level, confidence = merge_value(
                        existing.level if existing else None,
                        existing.confidence if existing else prior,
                        float(raw),
                        observation.confidence,
                        reliability,
                    )
                    skills[str(skill_id)] = StudentSkill(
                        skill_id=str(skill_id),
                        level=level,
                        confidence=confidence,
                        source=observation.source.value,
                        status=observation.source,
                        observed_at=observation.observed_at,
                    )
                    applied += 1
                    boost *= 1 - confidence
                continue

            target = dimensions.get(observation.dimension)
            if target is None or not isinstance(value, dict):
                continue
            for key, raw in value.items():
                if not isinstance(raw, (int, float)):
                    continue
                merged, confidence = merge_value(target.get(str(key)), prior, float(raw), observation.confidence, reliability)
                target[str(key)] = merged
                applied += 1
                boost *= 1 - confidence

        if not applied:
            return profile

        assessment = _clamp(1 - (1 - prior) * boost)
        return profile.model_copy(
            update={
                **dimensions,
                "skills": list(skills.values()),
                "assessment_confidence": assessment,
                "profile_version": _next_version(profile.profile_version),
            }
        )

    def apply_feedback(self, profile: StudentProfile, feedback_type: str, direction: Direction) -> StudentProfile:
        """Feedback = signal faible : petit pas vers (ou loin de) la direction."""
        kind = feedback_type.strip().lower()
        if kind in POSITIVE_FEEDBACK:
            step = FEEDBACK_RATE
        elif kind in NEGATIVE_FEEDBACK:
            step = -FEEDBACK_RATE
        else:
            return profile

        weight = max(0.1, profile.assessment_confidence)
        interests = dict(profile.interests)
        changed = False
        for key, target in direction.interests.items():
            current = interests.get(key)
            if current is None:
                continue  # donnée absente : on n'invente pas
            interests[key] = _clamp(current + step * weight * (target - current))
            changed = True

        if not changed:
            return profile

        return profile.model_copy(
            update={
                "interests": interests,
                "profile_version": _next_version(profile.profile_version),
            }
        )
