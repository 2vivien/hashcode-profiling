from __future__ import annotations

from orientation.contracts.profile import StudentProfile


def incorporate_observations(profile: StudentProfile) -> StudentProfile:
    """Blend longitudinal observations deterministically; never invent evidence."""
    if not profile.observations:
        return profile

    buckets: dict[str, list[tuple[float, float]]] = {}
    for observation in profile.observations:
        if not isinstance(observation.value, (int, float)):
            continue
        buckets.setdefault(observation.dimension, []).append(
            (float(observation.value), observation.confidence)
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
        total_confidence = sum(confidence for _, confidence in values)
        if total_confidence <= 0:
            continue
        weighted = sum(value * confidence for value, confidence in values)
        updates.setdefault(target, {})[dimension] = weighted / total_confidence

    data = profile.model_dump()
    for target, values in updates.items():
        current = dict(data[target])
        current.update(values)
        data[target] = current
    return StudentProfile.model_validate(data)
