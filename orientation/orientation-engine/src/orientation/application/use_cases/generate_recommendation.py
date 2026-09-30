from pathlib import Path
from uuid import uuid4
from orientation.audit.service import AuditService
from orientation.config.recommendation import RecommendationConfig
from orientation.contracts.profile import StudentProfile
from orientation.contracts.recommendation import Recommendation, RecommendationItem
from orientation.domain.skills.gaps import SkillGapService
from orientation.explanation.facts import ExplanationService
from orientation.exploration.service import ExplorationService
from orientation.infrastructure.knowledge.loader import KnowledgeLoader
from orientation.infrastructure.knowledge.validator import KnowledgeValidator
from orientation.recommendation.candidate_generation.service import CandidateGenerationService
from orientation.recommendation.constraints.service import ConstraintService
from orientation.recommendation.diversification.service import DiversificationService
from orientation.recommendation.matching.service import MatchingService
from orientation.recommendation.ranking.service import RankingService
from orientation.recommendation.scoring.hybrid_score import HybridScorer
from orientation.recommendation.uncertainty.service import UncertaintyService

class GenerateRecommendation:
    def __init__(self,knowledge_root:Path) -> None:
        self.config=RecommendationConfig()
        self.loader=KnowledgeLoader(knowledge_root)
        self.validator=KnowledgeValidator()
        self.candidates=CandidateGenerationService()
        self.constraints=ConstraintService()
        self.matching=MatchingService()
        self.gaps=SkillGapService()
        self.scorer=HybridScorer(self.config)
        self.uncertainty=UncertaintyService()
        self.ranking=RankingService()
        self.diversification=DiversificationService()
        self.explanations=ExplanationService()
        self.exploration=ExplorationService()
        self.audit=AuditService()

    def execute(self,profile:StudentProfile) -> Recommendation:
        directions=self.loader.load_directions()
        self.validator.validate(directions)
        by_id={direction.direction_id:direction for direction in directions}
        generated=self.candidates.generate(profile,directions)
        items:list[RecommendationItem]=[]
        for candidate in generated:
            direction=by_id[candidate.direction_id]
            if self.constraints.evaluate(profile,direction)=="fail":
                continue
            matches=self.matching.all_matches(profile,direction)
            gaps=self.gaps.calculate(profile,direction)
            penalty=min(1.0,sum(gap.gap*gap.required_level for gap in gaps)/max(len(direction.skills),1))
            breakdown=self.scorer.score(matches,penalty)
            confidence=max(0.0,min(1.0,breakdown.confidence*(1-0.25*penalty)))
            uncertainty=self.uncertainty.calculate(profile,confidence)
            items.append(RecommendationItem(direction_id=direction.direction_id,direction_name=direction.canonical_name,taxonomy=direction.taxonomy,score=breakdown.compatibility,confidence=confidence,uncertainty=uncertainty,score_breakdown=breakdown,skill_gaps=gaps))
        ranked=self.ranking.rank(items)[:self.config.top_k]
        selected=self.diversification.diversify(ranked,self.config.final_k,self.config.diversification_lambda)
        final:list[RecommendationItem]=[]
        for item in selected:
            item.explanation=self.explanations.build(item)
            item.explorations=self.exploration.ideas(item)
            final.append(item)
        scores={item.direction_id:item.score for item in final}
        uncertainties={item.direction_id:item.uncertainty for item in final}
        ranking=[item.direction_id for item in final]
        audit=self.audit.build(str(uuid4()),profile.student_id,profile.profile_version,"v1",ranking,scores,uncertainties,[item.direction_id for item in generated])
        return Recommendation(recommendation_id=str(uuid4()),profile_version=profile.profile_version,model_version="deterministic-baseline-v1",knowledge_version="v1",candidates=final,created_at=audit.timestamp,audit=audit)
