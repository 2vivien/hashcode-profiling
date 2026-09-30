from orientation.application.use_cases.generate_recommendation import GenerateRecommendation

def test_golden_recommendation_is_deterministic(knowledge_root,technical_profile) -> None:
    engine=GenerateRecommendation(knowledge_root)
    first=engine.execute(technical_profile)
    second=engine.execute(technical_profile)
    assert [(x.direction_id,x.score) for x in first.candidates] == [(x.direction_id,x.score) for x in second.candidates]
    assert first.audit.candidate_set == second.audit.candidate_set
    assert first.candidates
    assert first.candidates[0].direction_id in {"software-engineering","cybersecurity","data-science","network-engineering"}
