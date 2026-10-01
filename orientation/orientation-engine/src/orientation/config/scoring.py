from dataclasses import dataclass


@dataclass(frozen=True)
class ScoringWeights:
    interest: float = 0.20
    ability: float = 0.15
    skill: float = 0.15
    value: float = 0.10
    subject: float = 0.10
    self_efficacy: float = 0.10
    adaptability: float = 0.05
    environment: float = 0.05
    trajectory: float = 0.10
    skill_gap: float = 0.10

    @property
    def positive(self) -> tuple[float, ...]:
        return (
            self.interest,
            self.ability,
            self.skill,
            self.value,
            self.subject,
            self.self_efficacy,
            self.adaptability,
            self.environment,
            self.trajectory,
        )

    def validate(self) -> None:
        values = self.positive
        if any(value < 0 for value in values):
            raise ValueError("Positive score weights cannot be negative")
        if self.skill_gap < 0:
            raise ValueError("skill_gap cannot be negative")
        if sum(values) <= 0:
            raise ValueError("At least one positive score weight is required")
