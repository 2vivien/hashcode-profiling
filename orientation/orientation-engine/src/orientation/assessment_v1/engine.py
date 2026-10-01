from __future__ import annotations

import math
from collections import defaultdict
from statistics import fmean, pstdev

from orientation.assessment_v1.models import (
    AdaptivePair,
    AdaptiveQuestionRequest,
    AssessmentSubmission,
    DimensionEstimate,
    LatentProfile,
)
from orientation.assessment_v1.question_bank import QUESTION_BY_ID

RIASEC = ("realistic", "investigative", "artistic", "social", "enterprising", "conventional")


def _sigmoid(value: float) -> float:
    value = max(-12.0, min(12.0, value))
    return 1.0 / (1.0 + math.exp(-value))


def _normalized_entropy(values: list[float]) -> float:
    positive = [max(value, 1e-9) for value in values]
    total = sum(positive)
    probabilities = [value / total for value in positive]
    entropy = -sum(p * math.log(p) for p in probabilities)
    return entropy / math.log(len(probabilities))


def _estimate(raw_values: list[float], confidence_values: list[float]) -> DimensionEstimate:
    if not raw_values:
        return DimensionEstimate(value=0.5, confidence=0.0, raw_mean=0.0, z_score=0.0, evidence_count=0)
    mean = fmean(raw_values)
    scale = pstdev(raw_values) if len(raw_values) > 1 else 0.5
    z = mean / max(scale, 0.5)
    return DimensionEstimate(
        value=_sigmoid(z),
        confidence=max(0.0, min(1.0, fmean(confidence_values))),
        raw_mean=mean,
        z_score=z,
        evidence_count=len(raw_values),
    )


class AssessmentV1Engine:
    questionnaire_version = "othello-v1.0.0"
    profile_version = "latent-v1.0.0"

    def validate_submission(self, submission: AssessmentSubmission) -> None:
        seen: set[str] = set()
        for answer in submission.answers:
            question = QUESTION_BY_ID.get(answer.question_id)
            if question is None:
                raise ValueError(f"unknown_question:{answer.question_id}")
            if answer.question_id in seen:
                raise ValueError(f"duplicate_answer:{answer.question_id}")
            seen.add(answer.question_id)
            if not question.min_selections <= len(answer.option_ids) <= question.max_selections:
                raise ValueError(f"invalid_selection_count:{answer.question_id}")
            valid = {option.option_id for option in question.options}
            if not set(answer.option_ids).issubset(valid):
                raise ValueError(f"invalid_option:{answer.question_id}")

    def build_profile(self, submission: AssessmentSubmission) -> LatentProfile:
        self.validate_submission(submission)
        raw: dict[str, list[float]] = defaultdict(list)
        conf: dict[str, list[float]] = defaultdict(list)
        for answer in submission.answers:
            question = QUESTION_BY_ID[answer.question_id]
            for option_id in answer.option_ids:
                option = next(option for option in question.options if option.option_id == option_id)
                if option.value is not None:
                    for dimension in question.dimensions:
                        raw[dimension].append(option.value)
                        conf[dimension].append(answer.confidence)
                for dimension, weight in option.latent_weights.items():
                    raw[dimension].append(weight)
                    conf[dimension].append(answer.confidence)

        def group(names: tuple[str, ...]) -> dict[str, DimensionEstimate]:
            return {name: _estimate(raw[name], conf[name]) for name in names}

        riasec = group(RIASEC)
        # Intra-person RIASEC z-scores are computed across the six interests, not across respondents.
        riasec_means = [estimate.raw_mean for estimate in riasec.values()]
        riasec_scale = max(pstdev(riasec_means), 0.5)
        riasec = {
            name: estimate.model_copy(
                update={
                    "z_score": estimate.raw_mean / riasec_scale,
                    "value": _sigmoid(estimate.raw_mean / riasec_scale),
                }
            )
            for name, estimate in riasec.items()
        }
        abilities = group(("numerical", "verbal", "logical", "technical_learning", "problem_solving", "communication"))
        values = group(("income", "stability", "autonomy", "impact", "creativity", "recognition", "learning", "balance", "mobility", "entrepreneurship"))
        work_style = group(("structure_preference", "teamwork", "autonomy"))
        environment = group(("human_interaction", "physical_activity", "uncertainty_tolerance"))
        learning = group(("persistence", "self_directed_learning", "project_learning", "education_duration_tolerance"))
        adaptability = group(("adaptability", "agency", "decision_under_uncertainty", "metacognition"))

        interest = {name: estimate.value for name, estimate in riasec.items()}
        efficacy = {
            "analytical": abilities["logical"].value,
            "numerical": abilities["numerical"].value,
            "verbal": abilities["verbal"].value,
            "technical": abilities["technical_learning"].value,
            "problem_solving": abilities["problem_solving"].value,
            "communication": abilities["communication"].value,
        }
        gap = {
            "analytical": interest["investigative"] - efficacy["analytical"],
            "technical": (interest["realistic"] + interest["investigative"]) / 2 - efficacy["technical"],
            "social": interest["social"] - efficacy["communication"],
        }
        entropy = _normalized_entropy(list(interest.values()))
        contradictions: list[str] = []
        if work_style["teamwork"].value > 0.75 and environment["human_interaction"].value < 0.25:
            contradictions.append("teamwork_vs_human_interaction")
        if values["autonomy"].value > 0.75 and work_style["structure_preference"].value > 0.75:
            contradictions.append("autonomy_vs_structure")
        if values["stability"].value > 0.75 and environment["uncertainty_tolerance"].value > 0.75:
            contradictions.append("stability_vs_uncertainty_tolerance")

        answered = len(submission.answers)
        coverage = answered / 40.0
        mean_confidence = fmean(answer.confidence for answer in submission.answers)
        contradiction_penalty = min(0.30, 0.10 * len(contradictions))
        profile_confidence = max(0.0, min(1.0, coverage * mean_confidence * (1.0 - contradiction_penalty)))

        return LatentProfile(
            profile_version=self.profile_version,
            questionnaire_version=self.questionnaire_version,
            riasec=riasec,
            abilities=abilities,
            values=values,
            work_style=work_style,
            environment=environment,
            learning=learning,
            adaptability=adaptability,
            constraints={},
            interest_efficacy_gap=gap,
            riasec_entropy=entropy,
            profile_confidence=profile_confidence,
            contradictions=tuple(contradictions),
            answered_count=answered,
            total_questions=40,
        )

    def adaptive_questions(self, profile: LatentProfile, request: AdaptiveQuestionRequest) -> tuple[AdaptivePair, ...]:
        if profile.profile_confidence >= 0.65 or request.maximum_questions == 0:
            return ()
        answered = set(request.answered_question_ids)
        pairs = (
            ("adaptive_ri", "investigative", "artistic", 0.95),
            ("adaptive_rs", "realistic", "social", 0.90),
            ("adaptive_ec", "enterprising", "conventional", 0.85),
            ("adaptive_ia", "investigative", "artistic", 0.80),
            ("adaptive_se", "social", "enterprising", 0.75),
        )
        candidates = [
            AdaptivePair(question_id=qid, dimension=f"{a}:{b}", option_a=a, option_b=b, information_gain=gain)
            for qid, a, b, gain in pairs if qid not in answered
        ]
        return tuple(sorted(candidates, key=lambda item: (-item.information_gain, item.question_id))[:request.maximum_questions])
