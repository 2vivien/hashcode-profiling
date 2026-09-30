from orientation.contracts.direction import Direction
from orientation.contracts.profile import StudentProfile
from orientation.contracts.skill import SkillGap

class SkillGapService:
    def calculate(self, profile: StudentProfile, direction: Direction) -> list[SkillGap]:
        current = {skill.skill_id: skill for skill in profile.skills}
        gaps: list[SkillGap] = []
        for skill_id, required in direction.skills.items():
            skill = current.get(skill_id)
            level = skill.level if skill else None
            gap = max(0.0, required - (level or 0.0))
            if gap:
                gaps.append(SkillGap(skill_id=skill_id, current_level=level, required_level=required, gap=gap, confidence=skill.confidence if skill else 0.0, priority=min(1.0, gap * required)))
        return sorted(gaps, key=lambda item: (-item.priority, item.skill_id))
