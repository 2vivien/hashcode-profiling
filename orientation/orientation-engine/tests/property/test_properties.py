from orientation.recommendation.matching.vector import cosine_overlap


def test_cosine_bounds_for_sparse_vectors() -> None:
    for left, right in [
        ({}, {}),
        ({"a": 1}, {"b": 1}),
        ({"a": 0.5}, {"a": 0.5}),
        ({"a": 1, "b": 0}, {"a": 0, "b": 1}),
    ]:
        score = cosine_overlap(left, right)
        assert 0 <= score <= 1
