from __future__ import annotations

from dataclasses import dataclass
from math import sqrt

from orientation.contracts.profile import StudentProfile
from orientation.occupation_knowledge.models import OccupationMatch, OccupationRecord, ScoreComponent


@dataclass(frozen=True)
class ScoreWeights:
    interest: float = 0.24
    ability: float = 0.16
    skill: float = 0.16
    value: float = 0.12
    environment: float = 0.10
    work_style: float = 0.07
    self_efficacy: float = 0.07
    adaptability: float = 0.04
    evidence: float = 0.04

    def normalized(self) -> dict[str, float]:
        values = self.__dict__
        total = sum(values.values())
        return {key: value / total for key, value in values.items()}


def _cosine(left: dict[str, float], right: dict[str, float]) -> float:
    keys = set(left) | set(right)
    if not keys:
        return 0.5
    dot = sum(left.get(k, 0.0) * right.get(k, 0.0) for k in keys)
    nl = sqrt(sum(value * value for value in left.values()))
    nr = sqrt(sum(value * value for value in right.values()))
    if nl == 0 or nr == 0:
        return 0.5
    return max(0.0, min(1.0, dot / (nl * nr)))


def _overlap(left: dict[str, float], right: dict[str, float]) -> float:
    keys = set(left) & set(right)
    if not keys:
        return 0.5
    return max(0.0, min(1.0, sum(min(left[k], right[k]) for k in keys) / len(keys)))


class OccupationScorer:
    """Explainable scorer; missing occupational evidence never becomes a perfect match."""

    def __init__(self, weights: ScoreWeights | None = None) -> None:
        self.weights = (weights or ScoreWeights()).normalized()

    def score(self, profile: StudentProfile, occupation: OccupationRecord) -> OccupationMatch:
        profile_skills = {skill.skill_id: skill.level for skill in profile.skills}
        occupation_skills = occupation.skills or {skill: 1.0 for skill in occupation.skill_ids}
        components = (
            ScoreComponent("interest", _cosine(profile.interests, occupation.riasec), self.weights["interest"]),
            ScoreComponent("ability", _cosine(profile.abilities, occupation.abilities), self.weights["ability"]),
            ScoreComponent("skill", _overlap(profile_skills, occupation_skills), self.weights["skill"]),
            ScoreComponent("value", _cosine(profile.values, occupation.values), self.weights["value"]),
            ScoreComponent("environment", _cosine(profile.environment, occupation.environment), self.weights["environment"]),
            ScoreComponent(
                "work_style",
                _cosine(
                    {
                        "structure_preference": profile.environment.get("structure_preference", 0.5),
                        "teamwork": profile.environment.get("teamwork", 0.5),
                        "autonomy": profile.values.get("autonomy", 0.5),
                    },
                    occupation.work_style,
                ),
                self.weights["work_style"],
            ),
            ScoreComponent("self_efficacy", _cosine(profile.self_efficacy, occupation.abilities), self.weights["self_efficacy"]),
            ScoreComponent("adaptability", _cosine(profile.adaptability, occupation.environment), self.weights["adaptability"]),
            ScoreComponent("evidence", occupation.data_completeness, self.weights["evidence"]),
        )
        raw = sum(component.score * component.weight for component in components)
        evidence = min(
            1.0,
            occupation.data_completeness * 0.75
            + min(1.0, occupation.evidence_count / 12.0) * 0.25,
        )
        confidence = max(0.0, min(1.0, 0.55 * profile.assessment_confidence + 0.45 * evidence))
        score = max(0.0, min(100.0, raw * 100.0))

        gaps = []
        if components[0].score < 0.45:
            gaps.append("centres_d_interet")
        if components[1].score < 0.45:
            gaps.append("aptitudes")
        if components[2].score < 0.45 and profile.skills:
            gaps.append("competences")
        if components[4].score < 0.45:
            gaps.append("environnement_de_travail")

        reasons = tuple(
            f"{component.name}={component.score:.2f}"
            for component in components
            if component.score >= 0.65
        )
        classification = (
            "strong_fit"
            if score >= 80 and confidence >= 0.70
            else "good_fit"
            if score >= 68 and confidence >= 0.55
            else "adjacent"
            if score >= 52
            else "exploration"
        )
        return OccupationMatch(
            occupation_id=occupation.occupation_id,
            title=occupation.title,
            source=occupation.source,
            score=score,
            confidence=confidence,
            recommendation_class=classification,
            isco08_code=occupation.isco08_code,
            isco_major_group=occupation.isco_major_group,
            components=components,
            reasons=reasons,
            gaps=tuple(gaps),
            evidence_count=occupation.evidence_count,
        )

    def rank(
        self,
        profile: StudentProfile,
        occupations: list[OccupationRecord],
        limit: int = 20,
    ) -> list[OccupationMatch]:
        if limit < 1:
            raise ValueError("limit must be >= 1")
        matches = [self.score(profile, occupation) for occupation in occupations]
        return sorted(matches, key=lambda item: (-item.score, -item.confidence, item.title))[:limit]
