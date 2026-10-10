from pathlib import Path

from orientation.application.use_cases.generate_recommendation import GenerateRecommendation
from orientation.contracts.profile import StudentProfile

V2 = Path(__file__).parents[2] / "data" / "knowledge" / "v2"


def _profile() -> StudentProfile:
    return StudentProfile(
        student_id="v2-enrich",
        interests={"investigative": 0.9, "realistic": 0.8},
        abilities={"logical": 0.9, "verbal": 0.5},
        subjects={"mathematics": 0.8, "computer_science": 0.9},
        values={"autonomy": 0.8, "innovation": 0.9},
        skills=[
            {
                "skill_id": "programming",
                "level": 0.8,
                "confidence": 0.8,
                "source": "declared",
                "status": "declared",
            }
        ],
    )


def test_v2_knowledge_loads_occupations_and_formations() -> None:
    service = GenerateRecommendation(V2)
    bundle = service.knowledge()
    assert bundle.version == "v2"
    assert len(bundle.directions) == 12
    assert len(bundle.occupations) == 24
    assert len(bundle.formations) == 20


def test_recommendation_exposes_occupation_and_formation_paths() -> None:
    result = GenerateRecommendation(V2).execute(_profile())
    assert result.candidates

    with_occupations = [item for item in result.candidates if item.occupation_paths]
    assert with_occupations, "expected at least one direction with occupation paths"

    for item in with_occupations:
        assert len(item.occupation_paths) <= 3
        for path in item.occupation_paths:
            assert 0.0 <= path.match <= 100.0
            assert 0.0 <= path.confidence <= 1.0
            assert path.title

    with_formations = [item for item in result.candidates if item.formations]
    assert with_formations, "expected at least one direction with formations"
    levels = [f.level for f in with_formations[0].formations]
    assert levels == sorted(levels), "formations should be ordered from most accessible"


def test_occupation_paths_are_scored_against_the_profile() -> None:
    technical = GenerateRecommendation(V2).execute(_profile())
    technical_ids = {
        path.occupation_id for item in technical.candidates for path in item.occupation_paths
    }
    assert any(
        "software" in occupation_id or "data" in occupation_id for occupation_id in technical_ids
    )
