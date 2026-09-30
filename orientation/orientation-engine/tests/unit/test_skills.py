from orientation.domain.skills.readiness import readiness
from orientation.contracts.direction import Direction
from orientation.contracts.profile import StudentProfile

def test_missing_skill_is_gap() -> None:
    direction=Direction(direction_id="x",canonical_name="X",taxonomy="x",skills={"python":0.8})
    gaps=readiness(StudentProfile(student_id="x"),direction)
    assert gaps[0].gap == 0.8
