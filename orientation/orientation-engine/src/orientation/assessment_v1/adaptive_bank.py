from orientation.assessment_v1.models import AdaptivePair, AnswerOption, Question  # noqa: I001


ADAPTIVE_QUESTIONS = (
    Question(
        question_id="adaptive_ri",
        block="adaptive",
        text="Entre ces deux activités, laquelle t'attire le plus spontanément ?",
        response_type="single",
        options=(
            AnswerOption(option_id="investigative", label="Chercher pourquoi un phénomène fonctionne ainsi", latent_weights={"investigative": 1.0}),
            AnswerOption(option_id="artistic", label="Imaginer une manière originale de le représenter ou le créer", latent_weights={"artistic": 1.0}),
        ),
        dimensions=("investigative", "artistic"),
    ),
    Question(
        question_id="adaptive_rs",
        block="adaptive",
        text="Entre ces deux activités, laquelle t'attire le plus spontanément ?",
        response_type="single",
        options=(
            AnswerOption(option_id="realistic", label="Construire, manipuler ou réparer quelque chose", latent_weights={"realistic": 1.0}),
            AnswerOption(option_id="social", label="Accompagner une personne et l'aider à progresser", latent_weights={"social": 1.0}),
        ),
        dimensions=("realistic", "social"),
    ),
    Question(
        question_id="adaptive_ec", block="adaptive",
        text="Entre ces deux activités, laquelle t'attire le plus spontanément ?",
        response_type="single",
        options=(
            AnswerOption(option_id="enterprising", label="Faire avancer un projet, convaincre ou négocier", latent_weights={"enterprising": 1.0}),
            AnswerOption(option_id="conventional", label="Mettre en place un système fiable et bien organisé", latent_weights={"conventional": 1.0}),
        ),
        dimensions=("enterprising", "conventional"),
    ),
    Question(
        question_id="adaptive_ia", block="adaptive",
        text="Entre ces deux satisfactions, laquelle te ressemble davantage ?",
        response_type="single",
        options=(
            AnswerOption(option_id="investigative", label="Découvrir une explication que personne ne m'avait donnée", latent_weights={"investigative": 1.0}),
            AnswerOption(option_id="artistic", label="Transformer une idée en création originale", latent_weights={"artistic": 1.0}),
        ),
        dimensions=("investigative", "artistic"),
    ),
    Question(
        question_id="adaptive_se", block="adaptive",
        text="Dans un projet collectif, quel rôle t'attire le plus ?",
        response_type="single",
        options=(
            AnswerOption(option_id="social", label="Faire progresser les personnes et faciliter la collaboration", latent_weights={"social": 1.0}),
            AnswerOption(option_id="enterprising", label="Donner une direction, décider et faire avancer le projet", latent_weights={"enterprising": 1.0}),
        ),
        dimensions=("social", "enterprising"),
    ),
)

ADAPTIVE_BY_ID = {question.question_id: question for question in ADAPTIVE_QUESTIONS}


def as_pair(question_id: str, information_gain: float) -> AdaptivePair:
    question = ADAPTIVE_BY_ID[question_id]
    return AdaptivePair(
        question_id=question.question_id,
        dimension=":".join(question.dimensions),
        option_a=question.options[0].option_id,
        option_b=question.options[1].option_id,
        information_gain=information_gain,
    )
