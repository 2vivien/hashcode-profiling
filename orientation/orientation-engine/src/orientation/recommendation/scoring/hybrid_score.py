from orientation.config.recommendation import RecommendationConfig
from orientation.contracts.scoring import MatchResult, ScoreBreakdown


class HybridScorer:
    def __init__(self, config: RecommendationConfig) -> None:
        self.config = config

    def score(
        self,
        matches: dict[str, MatchResult],
        skill_gap_penalty: float,
        semantic_fit: float = 0.0,
        graph_fit: float = 0.0,
    ) -> ScoreBreakdown:
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
        available = [
            (key, weight)
            for key, weight in zip(keys, w.positive, strict=True)
            if key in matches
        ]
        if not available:
            raise ValueError("at least one matching dimension is required")
        raw = (
            sum(
                weight * matches[key].score * matches[key].confidence
                for key, weight in available
            )
            - w.skill_gap * skill_gap_penalty
        )
        denominator = max(sum(weight for _, weight in available), 1e-9)
        compatibility = max(0.0, min(1.0, raw / denominator))
        confidence = sum(matches[key].confidence for key, _ in available) / len(available)
        return ScoreBreakdown(
            interest_fit=matches["interest"].score,
            ability_fit=matches["ability"].score,
            skill_fit=matches["skill"].score,
            value_fit=matches["value"].score,
            subject_fit=matches["subject"].score,
            self_efficacy_fit=matches.get(
                "self_efficacy", MatchResult(score=0.0, confidence=0.0)
            ).score,
            adaptability_fit=matches.get(
                "adaptability", MatchResult(score=0.0, confidence=0.0)
            ).score,
            environment_fit=matches.get(
                "environment", MatchResult(score=0.0, confidence=0.0)
            ).score,
            trajectory_fit=matches.get(
                "trajectory", MatchResult(score=0.0, confidence=0.0)
            ).score,
            semantic_fit=max(0.0, min(1.0, semantic_fit)),
            graph_fit=max(0.0, min(1.0, graph_fit)),
            skill_gap_penalty=max(0.0, min(1.0, skill_gap_penalty)),
            confidence=confidence,
            compatibility=compatibility,
        )
