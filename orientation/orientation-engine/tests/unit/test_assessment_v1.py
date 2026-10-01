from datetime import UTC, datetime

import pytest

from orientation.assessment_v1.engine import AssessmentV1Engine
from orientation.assessment_v1.models import AdaptiveQuestionRequest, Answer, AssessmentSubmission
from orientation.assessment_v1.question_bank import QUESTIONS_V1
from orientation.assessment_v1.telemetry import JsonlEventStore, make_event, reward_for


def _submission() -> AssessmentSubmission:
    answers = []
    for question in QUESTIONS_V1:
        option = question.options[0]
        answers.append(
            Answer(
                question_id=question.question_id,
                option_ids=(option.option_id,),
                confidence=0.9,
                answered_at=datetime.now(UTC),
            )
        )
    return AssessmentSubmission(
        assessment_id="a1",
        session_id="s1",
        student_id="student-1",
        instrument_version="othello-v1.0.0",
        answers=tuple(answers),
    )


def test_question_bank_is_exactly_40_and_closed() -> None:
    assert len(QUESTIONS_V1) == 40
    assert [q.question_id for q in QUESTIONS_V1] == [f"Q{i:02d}" for i in range(1, 41)]
    assert all(question.options for question in QUESTIONS_V1)
    assert all(len({option.option_id for option in question.options}) == len(question.options) for question in QUESTIONS_V1)


def test_profile_is_normalized_and_confidence_is_bounded() -> None:
    profile = AssessmentV1Engine().build_profile(_submission())
    for dimension in (profile.riasec, profile.abilities, profile.values, profile.work_style, profile.environment, profile.learning, profile.adaptability):
        assert all(0.0 <= estimate.value <= 1.0 for estimate in dimension.values())
        assert all(0.0 <= estimate.confidence <= 1.0 for estimate in dimension.values())
    assert 0.0 <= profile.riasec_entropy <= 1.0
    assert 0.0 <= profile.profile_confidence <= 1.0


def test_adaptive_questions_stop_when_confidence_is_high() -> None:
    profile = AssessmentV1Engine().build_profile(_submission())
    request = AdaptiveQuestionRequest(profile_confidence=profile.profile_confidence, maximum_questions=3)
    assert AssessmentV1Engine().adaptive_questions(profile, request) == ()


def test_invalid_option_is_rejected() -> None:
    submission = _submission().model_copy(update={"answers": (Answer(question_id="Q01", option_ids=("invalid",)),)})
    with pytest.raises(ValueError, match="invalid_option"):
        AssessmentV1Engine().build_profile(submission)


def test_event_store_is_immutable_and_verifiable(tmp_path) -> None:
    store = JsonlEventStore(tmp_path / "events.jsonl")
    event = make_event("JOB_FAVORITED", "student-1", direction_id="esco:1")
    stored = store.append(event.model_copy(update={"reward": reward_for(event)}))
    assert stored.context["chain_hash"]
    assert store.verify_chain()


def test_event_reward_for_dwell_time() -> None:
    event = make_event("JOB_DETAIL_DWELL_TIME", "student-1", payload={"seconds": 180})
    assert reward_for(event) == pytest.approx(0.15)
