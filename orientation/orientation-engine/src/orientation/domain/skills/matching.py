from orientation.contracts.direction import Direction
from orientation.contracts.profile import StudentProfile
from orientation.contracts.scoring import MatchResult


class SkillMatcher:
    def match(self, profile: StudentProfile, direction: Direction) -> MatchResult:
        student = {skill.skill_id: skill for skill in profile.skills}
        if not direction.skills:
            return MatchResult(score=0.5, confidence=0.0, evidence=["no_skill_requirement"])
        total = sum(direction.skills.values())
        matched = 0.0
        evidence: list[str] = []
        missing: list[str] = []
        for skill_id, required in direction.skills.items():
            current = student.get(skill_id)
            if current is None:
                missing.append(skill_id)
                continue
            matched += min(current.level / max(required, 0.01), 1.0) * required
            evidence.append(f"skill:{skill_id}")
        score = matched / total if total else 0.0
        confidence = sum(
            student[key].confidence for key in direction.skills if key in student
        ) / max(len(direction.skills), 1)
        return MatchResult(
            score=score, confidence=confidence, evidence=evidence, missing_data=missing
        )
