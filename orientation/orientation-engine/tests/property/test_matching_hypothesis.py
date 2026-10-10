from hypothesis import given
from hypothesis import strategies as st
from pydantic import ValidationError

from orientation.contracts.profile import StudentProfile
from orientation.recommendation.matching.vector import cosine_overlap

_unit = st.floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False)
_vector = st.dictionaries(st.text(min_size=1, max_size=4), _unit, max_size=6)


@given(_vector)
def test_cosine_self_is_within_bounds(vector: dict[str, float]) -> None:
    score = cosine_overlap(vector, vector)
    assert 0.0 <= score <= 1.0


@given(_vector, _vector)
def test_cosine_is_symmetric(left: dict[str, float], right: dict[str, float]) -> None:
    assert abs(cosine_overlap(left, right) - cosine_overlap(right, left)) < 1e-9


@given(_vector)
def test_profile_accepts_normalized_dimensions(dimension: dict[str, float]) -> None:
    profile = StudentProfile(student_id="hyp", interests=dimension)
    assert profile.student_id == "hyp"


@given(st.floats(min_value=1.0001, max_value=10, allow_nan=False, allow_infinity=False))
def test_profile_rejects_out_of_range_value(value: float) -> None:
    try:
        StudentProfile(student_id="hyp", interests={"x": value})
    except (ValueError, ValidationError):
        return
    raise AssertionError("out-of-range profile value was accepted")
