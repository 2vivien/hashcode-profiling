from orientation.config.recommendation import RecommendationConfig
from orientation.recommendation.scoring.hybrid_score import HybridScorer


def test_hybrid_score_is_bounded() -> None:
    scorer = HybridScorer(RecommendationConfig())
    matches = {
        key: type("Match", (), {"score": 1.0, "confidence": 1.0})()
        for key in ("interest", "ability", "skill", "value", "subject", "trajectory")
    }
    result = scorer.score(matches, 0.0)
    assert 0 <= result.compatibility <= 1
    assert result.confidence == 1
