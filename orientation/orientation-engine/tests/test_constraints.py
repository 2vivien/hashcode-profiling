from orientation.contracts.direction import Direction
from orientation.contracts.profile import StudentProfile
from orientation.recommendation.constraints.service import ConstraintService


def test_unknown_constraint_is_not_fail() -> None:
    profile = StudentProfile(student_id="x", constraints={"location": "Cotonou"})
    direction = Direction(
        direction_id="x", canonical_name="X", taxonomy="x", accessibility={"location": "Abidjan"}
    )
    assert ConstraintService().evaluate(profile, direction) == "unknown"
