from orientation.assessment_v1.engine import AssessmentV1Engine
from orientation.assessment_v1.models import AssessmentSubmission, LatentProfile, Question
from orientation.assessment_v1.question_bank import QUESTIONS_V1
from orientation.contracts.profile import StudentProfile


class AssessmentProfileService:
    def __init__(self) -> None:
        self.engine = AssessmentV1Engine()

    def questions(self) -> tuple[Question, ...]:
        return QUESTIONS_V1

    def build_latent_profile(self, submission: AssessmentSubmission) -> LatentProfile:
        return self.engine.build_profile(submission)

    def to_student_profile(self, submission: AssessmentSubmission) -> StudentProfile:
        latent = self.build_latent_profile(submission)
        subjects: dict[str, float] = {}
        constraints: dict[str, float | str | bool | list[str]] = {}
        signals = {key: estimate.value for key, estimate in latent.signals.items()}
        for key in ("mathematics", "physical_science", "life_science", "language", "social_science", "economics", "technology", "arts", "practical"):
            if key in signals:
                subjects[key] = signals[key]
        for answer in submission.answers:
            question = next(item for item in QUESTIONS_V1 if item.question_id == answer.question_id)
            for option in question.options:
                if option.option_id not in answer.option_ids:
                    continue
                if answer.question_id == "Q19":
                    for key in option.latent_weights:
                        subjects[key] = max(subjects.get(key, 0.0), 0.8)
                if answer.question_id == "Q38":
                    constraints["selected"] = list(answer.option_ids)

        return StudentProfile(
            student_id=submission.student_id,
            profile_version=latent.profile_version,
            questionnaire_version=latent.questionnaire_version,
            assessment_confidence=latent.profile_confidence,
            riasec_entropy=latent.riasec_entropy,
            contradictions=latent.contradictions,
            interests={key: value.value for key, value in latent.riasec.items()},
            abilities={key: value.value for key, value in latent.abilities.items()},
            values={key: value.value for key, value in latent.values.items()},
            subjects=subjects,
            self_efficacy={key: value.value for key, value in latent.abilities.items()},
            adaptability={key: value.value for key, value in latent.adaptability.items()},
            environment={
                **{key: value.value for key, value in latent.environment.items()},
                **{key: value.value for key, value in latent.work_style.items()},
            },
            learning={
                **{key: value.value for key, value in latent.learning.items()},
                **{
                    key: value
                    for key, value in signals.items()
                    if key
                    in {
                        "project_learning",
                        "imitation_learning",
                        "theoretical_learning",
                        "social_learning",
                        "iterative_learning",
                        "structured_learning",
                    }
                },
            },
            trajectory={key: value.value for key, value in latent.learning.items() if key == "persistence"},
            constraints=constraints,
        )
