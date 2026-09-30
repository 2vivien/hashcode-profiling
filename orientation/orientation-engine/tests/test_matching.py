from orientation.recommendation.matching.vector import cosine_overlap

def test_cosine_overlap_identical() -> None:
    assert cosine_overlap({"a":1.0},{"a":1.0}) == 1.0

def test_unknown_dimension_is_neutral_not_zero() -> None:
    assert cosine_overlap({}, {}) == 0.5
