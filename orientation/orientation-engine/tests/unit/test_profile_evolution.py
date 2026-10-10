from orientation.contracts.common import DataState, Observation, SourceType
from orientation.contracts.direction import Direction
from orientation.contracts.profile import StudentProfile
from orientation.domain.profile.evolution import ProfileEvolutionService, merge_value

service = ProfileEvolutionService()


def _profile(**overrides: object) -> StudentProfile:
    base: dict[str, object] = {
        "student_id": "evo-1",
        "profile_version": "v1",
        "assessment_confidence": 0.5,
        "interests": {"investigative": 0.4},
    }
    base.update(overrides)
    return StudentProfile(**base)  # type: ignore[arg-type]


def _direction(**overrides: object) -> Direction:
    base: dict[str, object] = {
        "direction_id": "software-engineering",
        "canonical_name": "Ingénierie logicielle",
        "taxonomy": "technology",
        "interests": {"investigative": 1.0},
    }
    base.update(overrides)
    return Direction(**base)  # type: ignore[arg-type]


def test_merge_value_is_precision_weighted() -> None:
    value, confidence = merge_value(0.4, 0.5, 0.9, 0.8, 0.85)
    assert 0.68 < value < 0.70
    assert confidence > 0.5


def test_unknown_state_is_ignored() -> None:
    profile = _profile()
    observation = Observation(
        dimension="interests",
        value={"investigative": 0.99},
        confidence=0.9,
        source=SourceType.ASSESSED,
        state=DataState.UNKNOWN,
    )
    result = service.apply_observations(profile, [observation])
    assert result.interests == profile.interests
    assert result.profile_version == "v1"


def test_observation_updates_value_and_version() -> None:
    profile = _profile()
    observation = Observation(
        dimension="interests",
        value={"investigative": 0.9},
        confidence=0.8,
        source=SourceType.OBSERVED,
    )
    result = service.apply_observations(profile, [observation])
    assert result.interests["investigative"] > profile.interests["investigative"]
    assert result.assessment_confidence > profile.assessment_confidence
    assert result.profile_version == "v2"


def test_skills_are_merged_by_id() -> None:
    profile = _profile(
        skills=[
            {
                "skill_id": "programming",
                "level": 0.5,
                "confidence": 0.6,
                "source": "declared",
                "status": "declared",
            }
        ]
    )
    observation = Observation(
        dimension="skills",
        value={"programming": 0.9},
        confidence=0.9,
        source=SourceType.ASSESSED,
    )
    result = service.apply_observations(profile, [observation])
    skill = next(s for s in result.skills if s.skill_id == "programming")
    assert skill.level > 0.5
    assert skill.status is SourceType.ASSESSED


def test_positive_feedback_moves_towards_direction() -> None:
    profile = _profile()
    result = service.apply_feedback(profile, "pertinent", _direction())
    assert result.interests["investigative"] > profile.interests["investigative"]
    assert result.profile_version == "v2"


def test_negative_feedback_moves_away() -> None:
    profile = _profile(interests={"investigative": 0.8})
    result = service.apply_feedback(profile, "pas_pertinent", _direction())
    assert result.interests["investigative"] < 0.8


def test_unknown_feedback_changes_nothing() -> None:
    profile = _profile()
    result = service.apply_feedback(profile, "je_ne_sais_pas", _direction())
    assert result.interests == profile.interests
    assert result.profile_version == "v1"


def test_feedback_does_not_invent_missing_dimension() -> None:
    profile = _profile(interests={})
    result = service.apply_feedback(profile, "pertinent", _direction())
    assert result.interests == {}
    assert result.profile_version == "v1"


def test_values_stay_in_range() -> None:
    profile = _profile(interests={"investigative": 0.95})
    for _ in range(20):
        profile = service.apply_feedback(profile, "pertinent", _direction())
    assert profile.interests["investigative"] <= 1.0
