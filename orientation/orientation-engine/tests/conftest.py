from pathlib import Path

import pytest

from orientation.contracts.profile import StudentProfile


@pytest.fixture
def knowledge_root() -> Path:
    return Path(__file__).parents[1] / "data" / "knowledge" / "v1"


@pytest.fixture
def technical_profile() -> StudentProfile:
    return StudentProfile(
        student_id="golden-technical",
        interests={"realistic": 0.9, "investigative": 0.9, "conventional": 0.6},
        abilities={"logical": 0.9, "verbal": 0.5},
        subjects={"mathematics": 0.8, "computer_science": 0.95},
        values={"autonomy": 0.9, "innovation": 0.9},
        skills=[
            {
                "skill_id": "programming",
                "level": 0.85,
                "confidence": 0.9,
                "source": "assessment",
                "status": "assessed",
            },
            {
                "skill_id": "problem_solving",
                "level": 0.9,
                "confidence": 0.9,
                "source": "observed",
                "status": "observed",
            },
            {
                "skill_id": "networking",
                "level": 0.4,
                "confidence": 0.7,
                "source": "declared",
                "status": "declared",
            },
        ],
        trajectory={"mathematics": 0.8, "computer_science": 0.9},
    )
