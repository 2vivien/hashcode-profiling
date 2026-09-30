from collections import defaultdict
from orientation.contracts.candidate import Candidate
from orientation.contracts.direction import Direction
from orientation.contracts.profile import StudentProfile

class CandidateGenerationService:
    def generate(self, profile: StudentProfile, directions: list[Direction]) -> list[Candidate]:
        sources: dict[str,set[str]] = defaultdict(set)
        skill_ids = {skill.skill_id for skill in profile.skills}
        for direction in directions:
            if set(profile.interests) & set(direction.interests):
                sources[direction.direction_id].add("interest")
            if set(profile.abilities) & set(direction.abilities):
                sources[direction.direction_id].add("ability")
            if skill_ids & set(direction.skills):
                sources[direction.direction_id].add("skill")
            if set(profile.subjects) & set(direction.subjects):
                sources[direction.direction_id].add("subject")
        if not sources:
            return [Candidate(direction_id=direction.direction_id,generation_sources=["baseline"]) for direction in directions]
        return [Candidate(direction_id=key,generation_sources=sorted(value)) for key,value in sorted(sources.items())]
