from orientation.application.use_cases.generate_recommendation import GenerateRecommendation
from orientation.config.recommendation import RecommendationConfig


def test_golden_technical_profile(knowledge_root, technical_profile) -> None:
    config = RecommendationConfig()
    result = GenerateRecommendation(knowledge_root).execute(technical_profile)

    # Contrat de sortie : au plus `final_k` hypothèses, jamais zéro, bornées [0,1].
    assert result.candidates, "expected at least one direction hypothesis"
    assert len(result.candidates) <= config.final_k
    assert all(0.0 <= item.score <= 1.0 for item in result.candidates)
    assert all(0.0 <= item.confidence <= 1.0 for item in result.candidates)
    assert all(0.0 <= item.uncertainty <= 1.0 for item in result.candidates)

    # Versionnage : la connaissance utilisée est exposée.
    assert result.knowledge_version == "v1"
    assert result.model_version == "deterministic-baseline-v1"
