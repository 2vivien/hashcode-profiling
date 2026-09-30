from orientation.recommendation.matching.vector import cosine_overlap


def test_cosine_bounds() -> None:
    assert 0 <= cosine_overlap({"a": 1}, {"a": 0.5}) <= 1
