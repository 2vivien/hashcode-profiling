from dataclasses import dataclass


@dataclass(frozen=True)
class ScoringWeights:
    interest: float = 0.25
    ability: float = 0.20
    skill: float = 0.20
    value: float = 0.10
    subject: float = 0.15
    trajectory: float = 0.10
    skill_gap: float = 0.15

    @property
    def positive(self) -> tuple[float, ...]:
        return (
            self.interest,
            self.ability,
            self.skill,
            self.value,
            self.subject,
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
