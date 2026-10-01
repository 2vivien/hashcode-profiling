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
        raw = (
            sum(
                weight * matches[key].score * matches[key].confidence
                for weight, key in zip(w.positive, keys, strict=True)
            )
            - w.skill_gap * skill_gap_penalty
        )
        denominator = max(sum(w.positive), 1e-9)
        compatibility = max(0.0, min(1.0, raw / denominator))
        confidence = sum(matches[key].confidence for key in keys) / len(keys)
        return ScoreBreakdown(
            interest_fit=matches["interest"].score,
            ability_fit=matches["ability"].score,
            skill_fit=matches["skill"].score,
            value_fit=matches["value"].score,
            subject_fit=matches["subject"].score,
            self_efficacy_fit=matches["self_efficacy"].score,
            adaptability_fit=matches["adaptability"].score,
            environment_fit=matches["environment"].score,
            trajectory_fit=matches["trajectory"].score,
            semantic_fit=max(0.0, min(1.0, semantic_fit)),
            graph_fit=max(0.0, min(1.0, graph_fit)),
            skill_gap_penalty=max(0.0, min(1.0, skill_gap_penalty)),
            confidence=confidence,
            compatibility=compatibility,
        )
