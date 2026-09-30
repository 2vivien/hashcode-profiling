from math import sqrt
from orientation.contracts.direction import Direction
from orientation.contracts.profile import StudentProfile
from orientation.contracts.scoring import MatchResult

def cosine_overlap(student: dict[str,float], target: dict[str,float]) -> float:
    keys = set(student) | set(target)
    if not keys:
        return 0.5
    a = [student.get(k,0.0) for k in keys]
    b = [target.get(k,0.0) for k in keys]
    na, nb = sqrt(sum(x*x for x in a)), sqrt(sum(y*y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return max(0.0, min(1.0, sum(x*y for x,y in zip(a,b))/(na*nb)))

class VectorMatcher:
    def match(self, profile: StudentProfile, direction: Direction, dimension: str) -> MatchResult:
        student = getattr(profile, dimension)
        target = getattr(direction, dimension)
        if not student or not target:
            return MatchResult(score=0.5, confidence=0.0, missing_data=[dimension])
        evidence = [f"{dimension}:{key}" for key in sorted(set(student) & set(target))]
        return MatchResult(score=cosine_overlap(student,target), confidence=min(1.0,len(evidence)/len(target)), evidence=evidence)
