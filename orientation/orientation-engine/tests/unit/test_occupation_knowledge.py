from orientation.contracts.profile import StudentProfile
from orientation.occupation_knowledge.models import OccupationRecord
from orientation.occupation_knowledge.scoring import OccupationScorer


def test_score_is_bounded_and_explainable() -> None:
    profile = StudentProfile(
        student_id="s1",
        assessment_confidence=0.9,
        interests={"investigative": 0.9, "realistic": 0.8},
        abilities={"logical": 0.9, "problem_solving": 0.8},
        values={"autonomy": 0.8, "learning": 0.9},
        self_efficacy={"logical": 0.9},
        adaptability={"adaptability": 0.8},
        environment={"uncertainty_tolerance": 0.7},
    )
    occupation = OccupationRecord(
        occupation_id="test:developer",
        source="onet",
        source_version="31.0",
        title="Software developer",
        riasec={"investigative": 0.9, "realistic": 0.7},
        abilities={"logical": 0.9, "problem_solving": 0.9},
        values={"autonomy": 0.8, "learning": 0.8},
        environment={"uncertainty_tolerance": 0.7},
        evidence_count=12,
        data_completeness=0.9,
    )
    result = OccupationScorer().score(profile, occupation)
    assert 0 <= result.score <= 100
    assert 0 <= result.confidence <= 1
    assert result.components


def test_missing_occupation_evidence_does_not_become_perfect_fit() -> None:
    profile = StudentProfile(student_id="s1", assessment_confidence=1.0, interests={"social": 1.0})
    occupation = OccupationRecord(
        occupation_id="test:unknown",
        source="esco",
        source_version="1.2.1",
        title="Unknown occupation",
    )
    result = OccupationScorer().score(profile, occupation)
    assert result.confidence < 0.8
    assert result.score < 80


def test_taxonomy_has_all_isco_major_groups() -> None:
    from orientation.occupation_knowledge.taxonomy import ISCO_MAJOR_GROUPS

    assert tuple(group.code for group in ISCO_MAJOR_GROUPS) == tuple(str(i) for i in range(10))
