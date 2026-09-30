from orientation.contracts.explanation import Explanation, ExplanationFact
from orientation.contracts.recommendation import RecommendationItem

class ExplanationService:
    def build(self,item: RecommendationItem) -> Explanation:
        facts = [
            ExplanationFact(kind="positive",dimension="interest",direction_id=item.direction_id,statement_key="interest_fit",value=item.score_breakdown.interest_fit),
            ExplanationFact(kind="positive",dimension="ability",direction_id=item.direction_id,statement_key="ability_fit",value=item.score_breakdown.ability_fit),
            ExplanationFact(kind="evidence",dimension="skills",direction_id=item.direction_id,statement_key="skill_fit",value=item.score_breakdown.skill_fit),
            ExplanationFact(kind="uncertainty",dimension="confidence",direction_id=item.direction_id,statement_key="confidence",value=item.confidence),
        ]
        if item.skill_gaps:
            facts.append(ExplanationFact(kind="explore",dimension="skills",direction_id=item.direction_id,statement_key="skill_gaps",value=len(item.skill_gaps)))
        return Explanation(facts=facts)
