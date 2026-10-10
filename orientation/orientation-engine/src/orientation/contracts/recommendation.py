from datetime import datetime

from pydantic import BaseModel, Field

from orientation.contracts.audit import AuditSnapshot
from orientation.contracts.explanation import Explanation
from orientation.contracts.exploration import ExplorationIdea
from orientation.contracts.scoring import ScoreBreakdown
from orientation.contracts.skill import SkillGap


class OccupationPath(BaseModel):
    """Voie métier concrète, scorée et expliquée."""

    occupation_id: str
    title: str
    match: float = Field(ge=0, le=100)
    confidence: float = Field(ge=0, le=1)
    recommendation_class: str = "exploration"
    key_skills: list[str] = Field(default_factory=list)


class FormationPath(BaseModel):
    """Parcours de formation associé (accessibilité, pas verdict)."""

    formation_id: str
    title: str
    level: float = Field(default=0.5, ge=0, le=1)
    duration_years: int | None = None


class RecommendationItem(BaseModel):
    direction_id: str
    direction_name: str
    taxonomy: str
    score: float = Field(ge=0, le=1)
    confidence: float = Field(ge=0, le=1)
    uncertainty: float = Field(ge=0, le=1)
    score_breakdown: ScoreBreakdown
    skill_gaps: list[SkillGap] = Field(default_factory=list)
    explanation: Explanation = Field(default_factory=Explanation)
    explorations: list[ExplorationIdea] = Field(default_factory=list)
    occupation_paths: list[OccupationPath] = Field(default_factory=list)
    formations: list[FormationPath] = Field(default_factory=list)


class LayerReport(BaseModel):
    """État réel d'une couche de la pile : active ou non, et pourquoi.

    Sans ce rapport, « le moteur utilise un modèle » reste une affirmation.
    """

    layer: str
    active: bool
    reason: str
    contribution: float = 0.0
    details: dict[str, object] = Field(default_factory=dict)


class Recommendation(BaseModel):
    recommendation_id: str
    profile_version: str
    model_version: str
    knowledge_version: str
    candidates: list[RecommendationItem] = Field(default_factory=list)
    created_at: datetime
    audit: AuditSnapshot
    layers: list[LayerReport] = Field(default_factory=list)
