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


def test_missing_evidence_is_neutral_but_uncertain() -> None:
    scorer = HybridScorer(RecommendationConfig())
    matches = {
        "interest": type("Match", (), {"score": 0.0, "confidence": 0.0})(),
        "ability": type("Match", (), {"score": 1.0, "confidence": 1.0})(),
    }
    result = scorer.score(matches, 0.0)
    assert 0.0 < result.compatibility <= 1.0
    assert result.confidence == 0.5
