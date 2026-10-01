from orientation.assessment_v1.engine import AssessmentV1Engine
from orientation.assessment_v1.models import AssessmentSubmission, LatentProfile
from orientation.contracts.profile import StudentProfile


class AssessmentProfileService:
    def __init__(self) -> None:
        self.engine = AssessmentV1Engine()

    def build_latent_profile(self, submission: AssessmentSubmission) -> LatentProfile:
        return self.engine.build_profile(submission)

    def to_student_profile(self, submission: AssessmentSubmission) -> StudentProfile:
        latent = self.build_latent_profile(submission)
        return StudentProfile(
            student_id=submission.student_id,
            profile_version=latent.profile_version,
            interests={key: value.value for key, value in latent.riasec.items()},
            abilities={key: value.value for key, value in latent.abilities.items()},
            values={key: value.value for key, value in latent.values.items()},
            self_efficacy={key: value.value for key, value in latent.abilities.items()},
            adaptability={key: value.value for key, value in latent.adaptability.items()},
            environment={key: value.value for key, value in latent.environment.items()},
            constraints=latent.constraints,
        )
