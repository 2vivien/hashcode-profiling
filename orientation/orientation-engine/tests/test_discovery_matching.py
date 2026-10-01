from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from orientation.assessment_v1.longitudinal import incorporate_observations
from orientation.contracts.common import DataState, Observation, SourceType
from orientation.contracts.profile import StudentProfile
from orientation.occupation_knowledge.models import OccupationRecord
from orientation.occupation_knowledge.scoring import OccupationScorer


def profile() -> StudentProfile:
    return StudentProfile(
        student_id="student-1",
        assessment_confidence=0.8,
        interests={"realistic": 0.8, "investigative": 0.7},
        abilities={"logical": 0.8, "technical_learning": 0.7},
        self_efficacy={"logical": 0.8},
        values={"autonomy": 0.8, "learning": 0.8},
        environment={"structure_preference": 0.4, "teamwork": 0.5},
        learning={"persistence": 0.8},
    )


def occupation(identifier: str, title: str, group: str, skill: str) -> OccupationRecord:
    return OccupationRecord(
        occupation_id=identifier,
        source="esco",
        source_version="v1.2.1",
        title=title,
        isco_major_group=group,
        riasec={"realistic": 0.8, "investigative": 0.7},
        abilities={"logical": 0.8},
        skills={skill: 1.0},
        skill_ids=(skill,),
        data_completeness=0.9,
        evidence_count=10,
    )


def test_rank_diversifies_major_groups() -> None:
    records = [
        occupation("a", "A", "2", "s1"),
        occupation("b", "B", "2", "s2"),
        occupation("c", "C", "2", "s3"),
        occupation("d", "D", "7", "s4"),
    ]
    matches = OccupationScorer().rank(profile(), records, limit=3)
    assert {item.isco_major_group for item in matches} == {"2", "7"}


def test_longitudinal_observation_updates_profile() -> None:
    p = profile().model_copy(
        update={
            "observations": [
                Observation(
                    dimension="interest",
                    value=0.2,
                    confidence=1.0,
                    source="behavior",
                    status=SourceType.BEHAVIOR,
                )
            ]
        }
    )
    updated = incorporate_observations(p)
    assert updated.interests["interest"] == 0.2


def test_contract_accepts_unknown_constraint_state() -> None:
    p = profile().model_copy(update={"constraints": {"budget": DataState.UNKNOWN}})
    assert p.constraints["budget"] == DataState.UNKNOWN
