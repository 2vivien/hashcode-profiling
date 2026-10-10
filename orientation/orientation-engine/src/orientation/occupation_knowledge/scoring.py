from __future__ import annotations

from dataclasses import dataclass
from math import sqrt

from orientation.contracts.profile import StudentProfile
from orientation.occupation_knowledge.models import (
    DirectionExploration,
    OccupationMatch,
    OccupationRecord,
    ScoreComponent,
)


@dataclass(frozen=True)
class ScoreWeights:
    interest: float = 0.20
    ability: float = 0.14
    skill: float = 0.16
    value: float = 0.10
    environment: float = 0.08
    work_style: float = 0.08
    self_efficacy: float = 0.08
    learning: float = 0.05
    adaptability: float = 0.04
    knowledge: float = 0.03
    evidence: float = 0.02

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


def _merge_dimensions(*maps: dict[str, float]) -> dict[str, float]:
    merged: dict[str, float] = {}
    for mapping in maps:
        for key, value in mapping.items():
            merged[key] = max(merged.get(key, 0.0), value)
    return merged


def _experiences(profile: StudentProfile, occupation: OccupationRecord) -> tuple[str, ...]:
    gaps = []
    if occupation.job_zone is not None:
        gaps.append(f"Explorer une formation compatible avec la Job Zone {occupation.job_zone}.")
    if occupation.essential_skill_ids:
        gaps.append("Tester au moins une compétence essentielle via un mini-projet pratique.")
    if profile.assessment_confidence < 0.65:
        gaps.append("Comparer cette piste avec une autre expérience avant de conclure.")
    return tuple(gaps[:3])


class OccupationScorer:
    """Scores compatibility, never a deterministic career prescription."""

    def __init__(self, weights: ScoreWeights | None = None) -> None:
        self.weights = (weights or ScoreWeights()).normalized()

    def score(self, profile: StudentProfile, occupation: OccupationRecord) -> OccupationMatch:
        profile_skills = {skill.skill_id: skill.level for skill in profile.skills}
        occupation_skills = occupation.skills or {
            skill: 1.0 for skill in occupation.essential_skill_ids + occupation.optional_skill_ids
        }
        subject_evidence = occupation.knowledge or occupation.work_activities
        components = (
            ScoreComponent("interest", _cosine(profile.interests, occupation.riasec), self.weights["interest"]),
            ScoreComponent("ability", _cosine(profile.abilities, occupation.abilities), self.weights["ability"]),
            ScoreComponent("skill", _overlap(profile_skills, occupation_skills), self.weights["skill"]),
            ScoreComponent("subject", _cosine(profile.subjects, subject_evidence), self.weights["knowledge"]),
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
            ScoreComponent("learning", _cosine(profile.learning, occupation.training), self.weights["learning"]),
            ScoreComponent("adaptability", _cosine(profile.adaptability, occupation.environment), self.weights["adaptability"]),
            ScoreComponent("knowledge", _cosine(profile.subjects, occupation.knowledge), self.weights["knowledge"]),
            ScoreComponent("evidence", occupation.data_completeness, self.weights["evidence"]),
        )
        raw = sum(component.score * component.weight for component in components) / (sum(component.weight for component in components) or 1.0)
        evidence = min(1.0, occupation.data_completeness * 0.75 + min(1.0, occupation.evidence_count / 20.0) * 0.25)
        confidence = max(0.0, min(1.0, 0.60 * profile.assessment_confidence + 0.40 * evidence))
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
        if components[10].score < 0.45:
            gaps.append("connaissances")

        reasons = tuple(
            f"{component.name}={component.score:.2f}"
            for component in components
            if component.score >= 0.65
        )
        classification = (
            "strong_fit" if score >= 80 and confidence >= 0.70
            else "good_fit" if score >= 68 and confidence >= 0.55
            else "adjacent" if score >= 52
            else "exploration"
        )
        uncertainty = 1.0 - confidence
        experiences = ["réaliser un mini-projet représentatif", "faire un quiz court sur les connaissances fondamentales"]
        if components[0].score < 0.60:
            experiences.append("tester une activité réelle représentative de la direction")
        if components[5].score < 0.60:
            experiences.append("observer le contexte de travail réel via une immersion ou un échange")
        return OccupationMatch(
            occupation_id=occupation.occupation_id,
            title=occupation.title,
            source=occupation.source,
            score=score,
            confidence=confidence,
            uncertainty=uncertainty,
            recommendation_class=classification,
            isco08_code=occupation.isco08_code,
            isco_major_group=occupation.isco_major_group,
            components=components,
            reasons=reasons,
            gaps=tuple(gaps),
            experiences=_experiences(profile, occupation) + tuple(item for item in experiences if item not in _experiences(profile, occupation)),
            related_occupation_ids=occupation.related_occupation_ids,
            evidence_count=occupation.evidence_count,
            provenance=occupation.provenance,
        )

    def rank(self, profile: StudentProfile, occupations: list[OccupationRecord], limit: int = 20) -> list[OccupationMatch]:
        if limit < 1:
            raise ValueError("limit must be >= 1")
        matches = [self.score(profile, occupation) for occupation in occupations]
        matches.sort(key=lambda item: (-item.score, -item.confidence, item.title))
        selected: list[OccupationMatch] = []
        selected_records: list[OccupationRecord] = []
        by_id = {item.occupation_id: item for item in occupations}
        for match in matches:
            if len(selected) >= limit:
                break
            record = by_id[match.occupation_id]
            if self._too_similar(record, selected_records) and len(selected) < min(limit, 6):
                continue
            selected.append(match)
            selected_records.append(record)
        return selected

    def discover_directions(
        self,
        profile: StudentProfile,
        occupations: list[OccupationRecord],
        limit: int = 8,
    ) -> list[DirectionExploration]:
        if limit < 1:
            raise ValueError("limit must be >= 1")
        matches = self.rank(profile, occupations, max(limit * 4, 20))
        records = {item.occupation_id: item for item in occupations}
        buckets: dict[str, list[OccupationMatch]] = {}
        for match in matches:
            record = records[match.occupation_id]
            key = record.isco_major_group or "unclassified"
            buckets.setdefault(key, []).append(match)
        directions: list[DirectionExploration] = []
        for key, items in buckets.items():
            representative = items[:3]
            compatibility = sum(item.score for item in representative) / len(representative)
            confidence = sum(item.confidence for item in representative) / len(representative)
            gaps = tuple(dict.fromkeys(gap for item in representative for gap in item.gaps))[:4]
            reasons = tuple(dict.fromkeys(reason for item in representative for reason in item.reasons))[:4]
            experiments = tuple(dict.fromkeys(exp for item in representative for exp in item.experiences))[:3]
            label = next((records[item.occupation_id].domains[0] for item in representative if records[item.occupation_id].domains), f"Direction {key}")
            directions.append(DirectionExploration(
                direction_id=f"isco-major:{key}",
                label=label,
                compatibility=compatibility,
                confidence=confidence,
                uncertainty=1.0 - confidence,
                reasons=reasons,
                gaps=gaps,
                experiments=experiments,
                candidate_occupation_ids=tuple(item.occupation_id for item in representative),
            ))
        return sorted(directions, key=lambda item: (-item.compatibility, -item.confidence, item.label))[:limit]

    @staticmethod
    def _too_similar(record: OccupationRecord, selected: list[OccupationRecord]) -> bool:
        if not selected:
            return False
        for previous in selected:
            same_family = (
                record.isco_major_group is not None
                and record.isco_major_group == previous.isco_major_group
            )
            shared = len(set(record.skill_ids) & set(previous.skill_ids))
            if same_family and (shared >= 3 or record.isco_major_group is not None):
                return True
        return False
