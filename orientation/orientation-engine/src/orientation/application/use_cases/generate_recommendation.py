import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path

from orientation.audit.service import AuditService
from orientation.config.recommendation import RecommendationConfig
from orientation.contracts.direction import Direction
from orientation.contracts.formation import Formation
from orientation.contracts.profile import StudentProfile
from orientation.contracts.recommendation import (
    FormationPath,
    OccupationPath,
    Recommendation,
    RecommendationItem,
)
from orientation.domain.skills.gaps import SkillGapService
from orientation.explanation.facts import ExplanationService
from orientation.exploration.service import ExplorationService
from orientation.infrastructure.knowledge.loader import KnowledgeLoader
from orientation.infrastructure.knowledge.manifest import load_manifest
from orientation.infrastructure.knowledge.remote import RemoteKnowledge
from orientation.infrastructure.knowledge.validator import KnowledgeValidator
from orientation.occupation_knowledge.models import OccupationMatch, OccupationRecord
from orientation.occupation_knowledge.scoring import OccupationScorer
from orientation.recommendation.candidate_generation.service import CandidateGenerationService
from orientation.recommendation.constraints.service import ConstraintService
from orientation.recommendation.diversification.service import DiversificationService
from orientation.recommendation.matching.service import MatchingService
from orientation.recommendation.ranking.service import RankingService
from orientation.recommendation.scoring.hybrid_score import HybridScorer
from orientation.recommendation.uncertainty.service import UncertaintyService


@dataclass(frozen=True)
class KnowledgeBundle:
    version: str
    directions: list[Direction]
    occupations: list[OccupationRecord] = field(default_factory=list)
    formations: list[Formation] = field(default_factory=list)


class GenerateRecommendation:
    def __init__(
        self,
        knowledge_root: Path,
        model_version: str = "deterministic-baseline-v1",
        remote: RemoteKnowledge | None = None,
    ) -> None:
        self.model_version = model_version
        self.remote = remote
        self.config = RecommendationConfig()
        self.config.validate()
        self.loader = KnowledgeLoader(knowledge_root)
        self.validator = KnowledgeValidator()
        self.candidates = CandidateGenerationService()
        self.constraints = ConstraintService()
        self.matching = MatchingService()
        self.gaps = SkillGapService()
        self.scorer = HybridScorer(self.config)
        self.uncertainty = UncertaintyService()
        self.ranking = RankingService()
        self.diversification = DiversificationService()
        self.explanations = ExplanationService()
        self.exploration = ExplorationService()
        self.occupation_scorer = OccupationScorer()
        self.audit = AuditService()

    def knowledge(self) -> KnowledgeBundle:
        """Connaissance utilisée (data-service ou repli JSON)."""
        return self._load_knowledge()

    def _load_knowledge(self) -> KnowledgeBundle:
        """data-service d'abord, repli JSON local."""
        if self.remote is not None:
            remote_directions = self.remote.directions()
            if remote_directions:
                return KnowledgeBundle(
                    version=self.remote.version,
                    directions=remote_directions,
                    occupations=self.remote.occupations() or [],
                    formations=self.remote.formations() or [],
                )
        manifest = load_manifest(self.loader.repository.root)
        if not manifest.version:
            raise ValueError("unsupported_knowledge_version")
        return KnowledgeBundle(
            version=manifest.version,
            directions=self.loader.load_directions(),
            occupations=self.loader.repository.occupations(),
            formations=self.loader.repository.formations(),
        )

    def _resolve_paths(self, direction: Direction, profile: StudentProfile, bundle: KnowledgeBundle) -> tuple[list[OccupationPath], list[FormationPath]]:
        """Voies métier scorées + formations accessibles (les plus accessibles d'abord)."""
        by_occupation = {item.occupation_id: item for item in bundle.occupations}
        scored: list[tuple[OccupationMatch, OccupationRecord]] = []
        for occupation_id in direction.occupations:
            record = by_occupation.get(occupation_id)
            if record is None:
                continue
            scored.append((self.occupation_scorer.score(profile, record), record))
        scored.sort(key=lambda pair: (-pair[0].score, -pair[0].confidence, pair[0].title))

        paths = [
            OccupationPath(
                occupation_id=match.occupation_id,
                title=match.title,
                match=round(match.score, 1),
                confidence=round(match.confidence, 3),
                recommendation_class=match.recommendation_class,
                key_skills=[skill for skill, _ in sorted(record.skills.items(), key=lambda item: -item[1])[:3]],
            )
            for match, record in scored[:3]
        ]

        by_formation = {item.formation_id: item for item in bundle.formations}
        available = [by_formation[formation_id] for formation_id in direction.formations if formation_id in by_formation]
        available.sort(key=lambda item: (item.level, item.duration_years or 0))
        formations = [
            FormationPath(
                formation_id=item.formation_id,
                title=item.title,
                level=item.level,
                duration_years=item.duration_years,
            )
            for item in available
        ]
        return paths, formations

    def execute(self, profile: StudentProfile) -> Recommendation:
        bundle = self._load_knowledge()
        knowledge_version = bundle.version
        directions = bundle.directions
        self.validator.validate(directions, expected_version=knowledge_version)
        by_id = {direction.direction_id: direction for direction in directions}
        generated = self.candidates.generate(profile, directions)
        items: list[RecommendationItem] = []
        for candidate in generated:
            direction = by_id[candidate.direction_id]
            if self.constraints.evaluate(profile, direction) == "fail":
                continue
            matches = self.matching.all_matches(profile, direction)
            gaps = self.gaps.calculate(profile, direction)
            penalty = min(
                1.0,
                sum(gap.gap * gap.required_level for gap in gaps) / max(len(direction.skills), 1),
            )
            breakdown = self.scorer.score(matches, penalty)
            confidence = max(0.0, min(1.0, breakdown.confidence * (1 - 0.25 * penalty)))
            uncertainty = self.uncertainty.calculate(profile, confidence)
            items.append(
                RecommendationItem(
                    direction_id=direction.direction_id,
                    direction_name=direction.canonical_name,
                    taxonomy=direction.taxonomy,
                    score=breakdown.compatibility,
                    confidence=confidence,
                    uncertainty=uncertainty,
                    score_breakdown=breakdown,
                    skill_gaps=gaps,
                )
            )
        ranked = self.ranking.rank(items)[: self.config.top_k]
        selected = self.diversification.diversify(ranked, self.config.final_k, self.config.diversification_lambda)
        final: list[RecommendationItem] = []
        for item in selected:
            item.explanation = self.explanations.build(item)
            item.explorations = self.exploration.ideas(item)
            item.occupation_paths, item.formations = self._resolve_paths(by_id[item.direction_id], profile, bundle)
            final.append(item)
        scores = {item.direction_id: item.score for item in final}
        uncertainties = {item.direction_id: item.uncertainty for item in final}
        ranking = [item.direction_id for item in final]
        canonical = json.dumps(profile.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))
        recommendation_id = "rec-" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:24]
        audit = self.audit.build(
            recommendation_id,
            profile.student_id,
            profile.profile_version,
            knowledge_version,
            ranking,
            scores,
            uncertainties,
            [item.direction_id for item in generated],
        )
        return Recommendation(
            recommendation_id=recommendation_id,
            profile_version=profile.profile_version,
            model_version=self.model_version,
            knowledge_version=knowledge_version,
            candidates=final,
            created_at=audit.timestamp,
            audit=audit,
        )
