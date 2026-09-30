from orientation.application.use_cases.generate_recommendation import GenerateRecommendation


def test_golden_technical_profile(knowledge_root, technical_profile) -> None:
    result = GenerateRecommendation(knowledge_root).execute(technical_profile)
    assert len(result.candidates) <= 8
    assert all(item.score >= 0 for item in result.candidates)
    assert all(item.uncertainty >= 0 for item in result.candidates)
