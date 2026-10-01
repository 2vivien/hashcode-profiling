from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from orientation.assessment_v1.longitudinal import incorporate_observations
from orientation.assessment_v1.question_bank import QUESTIONS_V1
from orientation.occupation_knowledge.onet_package import read_onet_zip
from orientation.occupation_knowledge.packages import read_esco_zip
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
                    source=SourceType.OBSERVED,
                    state=DataState.KNOWN,
                )
            ]
        }
    )
    updated = incorporate_observations(p)
    assert updated.interests["interest"] == 0.2


def test_contract_accepts_unknown_constraint_state() -> None:
    p = profile().model_copy(update={"constraints": {"budget": DataState.UNKNOWN}})
    assert p.constraints["budget"] == DataState.UNKNOWN


def test_questionnaire_retains_40_closed_questions() -> None:
    assert len(QUESTIONS_V1) == 40
    assert all(question.options for question in QUESTIONS_V1)
    assert all(question.response_type != "ranked" for question in QUESTIONS_V1)


def test_official_archive_readers_preserve_relations(tmp_path: Path) -> None:
    esco_zip = tmp_path / "esco.zip"
    with ZipFile(esco_zip, "w", ZIP_DEFLATED) as archive:
        archive.writestr("occupations_en.csv", "conceptUri,preferredLabel,altLabels,description,iscoGroup\\nuri:1,Engineer,Ingénieur,Build systems,21\\n")
        archive.writestr("skills_en.csv", "conceptUri,preferredLabel\\nskill:1,Problem solving\\nskill:2,Communication\\n")
        archive.writestr("occupationSkillRelations.csv", "occupationUri,skillUri,relationType\\nuri:1,skill:1,essential\\nuri:1,skill:2,optional\\n")
    records = read_esco_zip(esco_zip)
    assert records[0].essential_skill_ids == ("skill:1",)
    assert records[0].optional_skill_ids == ("skill:2",)

    onet_zip = tmp_path / "onet.zip"
    with ZipFile(onet_zip, "w", ZIP_DEFLATED) as archive:
        archive.writestr("Occupation Data.txt", "O*NET-SOC Code\\tTitle\\tDescription\\n11-1011.00\\tManager\\tManage work\\n")
        archive.writestr("Job Zones.txt", "O*NET-SOC Code\\tTitle\\tJob Zone\\n11-1011.00\\tManager\\t4\\n")
        archive.writestr("Abilities.txt", "O*NET-SOC Code\\tElement Name\\tData Value\\n11-1011.00\\tProblem Solving\\t5.0\\n")
    onet = read_onet_zip(onet_zip)
    assert onet[0].job_zone == 4
    assert onet[0].abilities["Problem Solving"] > 0.6
