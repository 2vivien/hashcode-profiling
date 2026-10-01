from orientation.assessment_v1.engine import AssessmentV1Engine
from orientation.assessment_v1.models import AssessmentSubmission, LatentProfile
from orientation.assessment_v1.question_bank import QUESTIONS_V1
from orientation.contracts.profile import StudentProfile


class AssessmentProfileService:
    def __init__(self) -> None:
        self.engine = AssessmentV1Engine()

    def questions(self):
        return QUESTIONS_V1

    def build_latent_profile(self, submission: AssessmentSubmission) -> LatentProfile:
        return self.engine.build_profile(submission)

    def to_student_profile(self, submission: AssessmentSubmission) -> StudentProfile:
        latent = self.build_latent_profile(submission)
        subjects: dict[str, float] = {}
        constraints: dict[str, float | str | bool | list[str]] = {}
        for answer in submission.answers:
            if answer.question_id == "Q19":
                selected = set(answer.option_ids)
                question = next(item for item in QUESTIONS_V1 if item.question_id == "Q19")
                for option in question.options:
                    if option.option_id in selected:
                        subjects.update({key: 0.8 for key in option.latent_weights})
            elif answer.question_id == "Q38":
                constraints["selected"] = list(answer.option_ids)
        return StudentProfile(
            student_id=submission.student_id,
            profile_version=latent.profile_version,
            interests={key: value.value for key, value in latent.riasec.items()},
            abilities={key: value.value for key, value in latent.abilities.items()},
            values={key: value.value for key, value in latent.values.items()},
            subjects=subjects,
            self_efficacy={key: value.value for key, value in latent.abilities.items()},
            adaptability={key: value.value for key, value in latent.adaptability.items()},
            environment={key: value.value for key, value in latent.environment.items()},
            constraints=constraints,
        )
