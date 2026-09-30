from orientation.application.use_cases.generate_recommendation import GenerateRecommendation


def test_full_pipeline(knowledge_root, technical_profile) -> None:
    result = GenerateRecommendation(knowledge_root).execute(technical_profile)
    assert result.candidates
    assert result.audit.model_version == "deterministic-baseline-v1"
    assert all(item.explanation.facts for item in result.candidates)
