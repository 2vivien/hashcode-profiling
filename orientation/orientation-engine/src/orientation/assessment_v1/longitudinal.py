from __future__ import annotations

from orientation.contracts.common import Observation\nfrom orientation.contracts.profile import StudentProfile


def incorporate_observations(profile: StudentProfile) -> StudentProfile:
    """Blend longitudinal observations into the current profile without inventing evidence.

    Each observation must already carry its source and confidence. The update is a
    deterministic weighted mean and is intentionally not an ML training step.
    """
    if not profile.observations:
        return profile

    buckets: dict[str, list[tuple[float, float]]] = {}
    for observation in profile.observations:
        buckets.setdefault(observation.dimension, []).append(
            (observation.value, observation.confidence)
        )

    updates: dict[str, dict[str, float]] = {}
    map_by_dimension = {
        "interest": "interests",
        "ability": "abilities",
        "value": "values",
        "subject": "subjects",
        "environment": "environment",
        "learning": "learning",
        "adaptability": "adaptability",
        "trajectory": "trajectory",
    }
    for dimension, values in buckets.items():
        target = map_by_dimension.get(dimension)
        if target is None:
            continue
        weighted = sum(value * confidence for value, confidence in values)
        confidence = sum(conf for _, conf in values)
        if confidence <= 0:
            continue
        updates.setdefault(target, {})[dimension] = weighted / confidence

    data = profile.model_dump()
    for target, values in updates.items():
        current = dict(data[target])
        current.update(values)
        data[target] = current
    return StudentProfile.model_validate(data)
