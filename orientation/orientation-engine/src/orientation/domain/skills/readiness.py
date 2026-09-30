from orientation.contracts.direction import Direction
from orientation.contracts.profile import StudentProfile
from orientation.contracts.skill import SkillGap

def readiness(profile: StudentProfile, direction: Direction) -> list[SkillGap]:
    current={skill.skill_id:skill for skill in profile.skills}
    return [
        SkillGap(skill_id=skill_id,current_level=current.get(skill_id).level if skill_id in current else 0.0,required_level=required,gap=max(0.0,required-(current.get(skill_id).level if skill_id in current else 0.0)),confidence=current.get(skill_id).confidence if skill_id in current else 0.0,priority=required)
        for skill_id,required in direction.skills.items()
    ]
