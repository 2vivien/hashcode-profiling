from __future__ import annotations  # noqa

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


AnswerValue = str | int
QuestionBlock = Literal["A", "B", "C", "D", "adaptive"]


class AnswerOption(BaseModel):
    model_config = ConfigDict(extra="forbid")
    option_id: str
    label: str
    value: float | None = None
    latent_weights: dict[str, float] = Field(default_factory=dict)
    tags: tuple[str, ...] = ()


class Question(BaseModel):
    model_config = ConfigDict(extra="forbid")
    question_id: str
    block: QuestionBlock
    text: str
    response_type: Literal["single", "multi", "likert", "ranked"]
    min_selections: int = Field(default=1, ge=0)
    max_selections: int = Field(default=1, ge=1)
    options: tuple[AnswerOption, ...] = Field(min_length=2)
    dimensions: tuple[str, ...] = Field(min_length=1)
    required: bool = True

    @model_validator(mode="after")
    def validate_selection_bounds(self) -> Question:
        if self.min_selections > self.max_selections:
            raise ValueError("min_selections cannot exceed max_selections")
        if self.max_selections > len(self.options):
            raise ValueError("max_selections exceeds option count")
        ids = [option.option_id for option in self.options]
        if len(ids) != len(set(ids)):
            raise ValueError("option ids must be unique per question")
        return self


class Answer(BaseModel):
    model_config = ConfigDict(extra="forbid")
    question_id: str
    option_ids: tuple[str, ...] = Field(min_length=1)
    confidence: float = Field(default=0.8, ge=0, le=1)
    answered_at: datetime | None = None


class AssessmentSubmission(BaseModel):
    model_config = ConfigDict(extra="forbid")
    assessment_id: str
    session_id: str
    student_id: str
    instrument_version: str
    answers: tuple[Answer, ...] = Field(min_length=1)


class DimensionEstimate(BaseModel):
    value: float = Field(ge=0, le=1)
    confidence: float = Field(ge=0, le=1)
    raw_mean: float
    z_score: float
    evidence_count: int = Field(ge=0)


class LatentProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")
    profile_version: str
    questionnaire_version: str
    riasec: dict[str, DimensionEstimate]
    signals: dict[str, DimensionEstimate] = Field(default_factory=dict)
    abilities: dict[str, DimensionEstimate]
    values: dict[str, DimensionEstimate]
    work_style: dict[str, DimensionEstimate]
    environment: dict[str, DimensionEstimate]
    learning: dict[str, DimensionEstimate]
    adaptability: dict[str, DimensionEstimate]
    constraints: dict[str, str | float | bool | tuple[str, ...]] = Field(default_factory=dict)
    interest_efficacy_gap: dict[str, float] = Field(default_factory=dict)
    riasec_entropy: float = Field(ge=0, le=1)
    profile_confidence: float = Field(ge=0, le=1)
    contradictions: tuple[str, ...] = ()
    answered_count: int = Field(ge=0)
    total_questions: int = Field(ge=1)


class AdaptiveQuestionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    profile_confidence: float = Field(ge=0, le=1)
    maximum_questions: int = Field(default=3, ge=0, le=3)
    answered_question_ids: tuple[str, ...] = ()


class AdaptivePair(BaseModel):
    question_id: str
    dimension: str
    option_a: str
    option_b: str
    information_gain: float = Field(ge=0)
