from orientation.config.recommendation import RecommendationConfig
from orientation.contracts.scoring import ScoreBreakdown

class HybridScorer:
    def __init__(self, config: RecommendationConfig) -> None:
        self.config = config

    def score(self, matches: dict[str,object], skill_gap_penalty: float) -> ScoreBreakdown:
        w = self.config.weights
        values = {key: float(getattr(matches[key],"score")) for key in ("interest","ability","skill","value","subject","trajectory")}
        raw = sum((w.interest,w.ability,w.skill,w.value,w.subject,w.trajectory)[i] * values[key] for i,key in enumerate(values)) - w.skill_gap * skill_gap_penalty
        compatibility = max(0.0,min(1.0,raw/max(sum(w.positive),1e-9)))
        confidence = sum(float(getattr(matches[key],"confidence")) for key in values) / len(values)
        return ScoreBreakdown(interest_fit=values["interest"],ability_fit=values["ability"],skill_fit=values["skill"],value_fit=values["value"],subject_fit=values["subject"],trajectory_fit=values["trajectory"],semantic_fit=0.0,graph_fit=0.0,skill_gap_penalty=skill_gap_penalty,confidence=confidence,compatibility=compatibility)
