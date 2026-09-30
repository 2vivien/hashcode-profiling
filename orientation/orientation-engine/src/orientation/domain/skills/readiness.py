from orientation.contracts.direction import Direction
from orientation.contracts.profile import StudentProfile
from orientation.contracts.skill import SkillGap


def readiness(profile: StudentProfile, direction: Direction) -> list[SkillGap]:
    current = {skill.skill_id: skill for skill in profile.skills}
    gaps: list[SkillGap] = []
    for skill_id, required in direction.skills.items():
        skill = current.get(skill_id)
        current_level = skill.level if skill else 0.0
        gaps.append(
            SkillGap(
                skill_id=skill_id,
                current_level=current_level,
                required_level=required,
                gap=max(0.0, required - current_level),
                confidence=skill.confidence if skill else 0.0,
                priority=required,
            )
        )
    return gaps
