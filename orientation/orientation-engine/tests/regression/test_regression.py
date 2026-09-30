from orientation.application.use_cases.generate_recommendation import GenerateRecommendation


def test_ranking_is_stable(knowledge_root, technical_profile) -> None:
    result = GenerateRecommendation(knowledge_root).execute(technical_profile)
    assert result.audit.ranking == [item.direction_id for item in result.candidates]
