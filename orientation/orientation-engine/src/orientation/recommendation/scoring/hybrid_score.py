from orientation.config.recommendation import RecommendationConfig
from orientation.contracts.scoring import MatchResult, ScoreBreakdown


class HybridScorer:
    def __init__(self, config: RecommendationConfig) -> None:
        self.config = config

    @staticmethod
    def _weighted_score(
        match: MatchResult,
        weight: float,
    ) -> tuple[float, float]:
        effective_weight = weight * match.confidence
        return effective_weight * match.score, effective_weight

    def score(
        self,
        matches: dict[str, MatchResult],
        skill_gap_penalty: float,
        semantic_fit: float = 0.0,
        graph_fit: float = 0.0,
    ) -> ScoreBreakdown:
        if not 0.0 <= skill_gap_penalty <= 1.0:
            raise ValueError("skill_gap_penalty must be in [0,1]")
        if not 0.0 <= semantic_fit <= 1.0 or not 0.0 <= graph_fit <= 1.0:
            raise ValueError("semantic_fit and graph_fit must be in [0,1]")

        w = self.config.weights
        keys = (
            "interest",
            "ability",
            "skill",
            "value",
            "subject",
            "self_efficacy",
            "adaptability",
            "environment",
            "trajectory",
        )
        weights = dict(zip(keys, w.positive, strict=True))
        observed = [key for key in keys if key in matches]
        if not observed:
            raise ValueError("at least one matching dimension is required")

        weighted_sum = 0.0
        effective_total = 0.0
        for key in observed:
            contribution, effective_weight = self._weighted_score(matches[key], weights[key])
            weighted_sum += contribution
            effective_total += effective_weight

        # Missing evidence is uncertainty, not a zero-quality signal.
        base_compatibility = (
            weighted_sum / effective_total if effective_total > 0.0 else 0.5
        )

        total_positive_weight = max(sum(weights[key] for key in keys), 1e-9)
        normalized_gap_penalty = w.skill_gap * skill_gap_penalty / total_positive_weight
        compatibility = max(0.0, min(1.0, base_compatibility - normalized_gap_penalty))

        confidence = (
            sum(matches[key].confidence for key in observed) / len(observed)
        )
        empty = MatchResult(score=0.0, confidence=0.0)
        return ScoreBreakdown(
            interest_fit=matches.get("interest", empty).score,
            ability_fit=matches.get("ability", empty).score,
            skill_fit=matches.get("skill", empty).score,
            value_fit=matches.get("value", empty).score,
            subject_fit=matches.get("subject", empty).score,
            self_efficacy_fit=matches.get("self_efficacy", empty).score,
            adaptability_fit=matches.get("adaptability", empty).score,
            environment_fit=matches.get("environment", empty).score,
            trajectory_fit=matches.get("trajectory", empty).score,
            semantic_fit=semantic_fit,
            graph_fit=graph_fit,
            skill_gap_penalty=skill_gap_penalty,
            confidence=confidence,
            compatibility=compatibility,
        )
