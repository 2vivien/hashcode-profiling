from typing import Literal

from orientation.assessment_v1.models import AnswerOption, Question


def _likert(
    question_id: str,
    block: Literal["A", "B", "C", "D"],
    text: str,
    dimensions: tuple[str, ...],
) -> Question:
    labels = (
        ("1", "Pas du tout d'accord", -1.0),
        ("2", "Plutôt pas d'accord", -0.5),
        ("3", "Neutre / difficile à dire", 0.0),
        ("4", "Plutôt d'accord", 0.5),
        ("5", "Tout à fait d'accord", 1.0),
    )
    return Question(
        question_id=question_id,
        block=block,
        text=text,
        response_type="likert",
        options=tuple(
            AnswerOption(
                option_id=f"{question_id.lower()}_{code}",
                label=label,
                value=value,
            )
            for code, label, value in labels
        ),
        dimensions=dimensions,
    )


def _choice(
    question_id: str,
    block: Literal["A", "B", "C", "D"],
    text: str,
    dimensions: tuple[str, ...],
    options: tuple[tuple[str, str, dict[str, float]], ...],
    *,
    multi: bool = False,
    max_selections: int = 1,
) -> Question:
    return Question(
        question_id=question_id,
        block=block,
        text=text,
        response_type="multi" if multi else "single",
        min_selections=1,
        max_selections=max_selections,
        options=tuple(
            AnswerOption(option_id=option_id, label=label, latent_weights=weights)
            for option_id, label, weights in options
        ),
        dimensions=dimensions,
    )


def build_question_bank() -> tuple[Question, ...]:
    q: list[Question] = []

    # A — interests and breadth of occupational activity.
    for i, (dimension, text) in enumerate(
        (
            ("realistic", "J'aime fabriquer, réparer, installer ou manipuler des objets, outils ou équipements."),
            ("investigative", "J'aime comprendre les causes d'un phénomène, analyser des informations et résoudre des problèmes complexes."),
            ("artistic", "J'aime imaginer, concevoir ou donner une forme originale à des idées."),
            ("social", "J'aime expliquer, accompagner, écouter ou aider d'autres personnes."),
            ("enterprising", "J'aime défendre une idée, négocier, prendre des initiatives ou mobiliser d'autres personnes."),
            ("conventional", "J'aime organiser, classer, vérifier et structurer des informations ou des processus."),
        ),
        1,
    ):
        q.append(_likert(f"Q{i:02d}", "A", text, (dimension,)))

    q.extend(
        [
            _choice(
                "Q07", "A",
                "Parmi ces types d'activités, lesquelles pourrais-tu pratiquer régulièrement avec intérêt ?",
                ("activity_preference",),
                (
                    ("build", "Construire, réparer ou installer", {"realistic": 1.0, "technical": 0.5}),
                    ("analyze", "Analyser des données, faits ou informations", {"investigative": 1.0}),
                    ("create", "Concevoir, écrire, dessiner ou créer", {"artistic": 1.0}),
                    ("care", "Accompagner, enseigner ou prendre soin", {"social": 1.0}),
                    ("lead", "Diriger, vendre, négocier ou développer un projet", {"enterprising": 1.0}),
                    ("organize", "Planifier, contrôler ou gérer des informations", {"conventional": 1.0}),
                    ("nature", "Observer ou travailler avec le vivant et la nature", {"life_science": 0.8, "realistic": 0.4}),
                    ("operate", "Faire fonctionner ou surveiller des équipements", {"realistic": 0.8, "technical": 0.8}),
                    ("research", "Expérimenter et produire de nouvelles connaissances", {"investigative": 1.0, "research": 1.0}),
                    ("communicate", "Présenter, informer ou convaincre un public", {"social": 0.6, "enterprising": 0.7}),
                ),
                multi=True,
                max_selections=4,
            ),
            _choice(
                "Q08", "A",
                "Dans quel type d'environnement aimerais-tu surtout résoudre des problèmes ?",
                ("work_environment_interest",),
                (
                    ("field", "Sur le terrain, avec des déplacements", {"realistic": 0.8, "mobility": 0.6}),
                    ("lab", "Laboratoire ou environnement expérimental", {"investigative": 1.0}),
                    ("studio", "Atelier, studio ou espace de création", {"artistic": 1.0}),
                    ("people", "Lieu centré sur les personnes", {"social": 1.0}),
                    ("business", "Entreprise, commerce ou projet", {"enterprising": 1.0}),
                    ("office", "Bureau ou environnement administratif structuré", {"conventional": 1.0}),
                    ("nature", "Ferme, environnement naturel ou extérieur", {"realistic": 0.7, "life_science": 0.8}),
                    ("technical", "Installation technique, usine ou infrastructure", {"realistic": 1.0, "technical": 1.0}),
                ),
            ),
            _choice(
                "Q09", "A",
                "Quel résultat te donnerait le plus de satisfaction ?",
                ("outcome_preference",),
                (
                    ("physical", "Un objet, une installation ou un système qui fonctionne", {"realistic": 1.0, "technical": 0.7}),
                    ("discovery", "Une explication, une analyse ou une découverte", {"investigative": 1.0, "research": 0.8}),
                    ("creation", "Une création originale ou esthétique", {"artistic": 1.0}),
                    ("progress", "Une personne ou un groupe qui progresse", {"social": 1.0}),
                    ("growth", "Un projet qui grandit ou atteint ses objectifs", {"enterprising": 1.0}),
                    ("order", "Un processus plus fiable, organisé ou efficace", {"conventional": 1.0}),
                ),
            ),
            _choice(
                "Q10", "A",
                "Quand tu rencontres un nouveau sujet, qu'est-ce qui t'attire d'abord ?",
                ("curiosity",),
                (
                    ("mechanism", "Comprendre comment cela fonctionne", {"investigative": 1.0}),
                    ("practice", "Essayer immédiatement par moi-même", {"realistic": 0.7, "experimental": 0.5}),
                    ("possibility", "Imaginer ce que je pourrais créer avec", {"artistic": 1.0}),
                    ("usefulness", "Comprendre qui cela peut aider", {"social": 1.0}),
                    ("opportunity", "Voir les opportunités que cela peut créer", {"enterprising": 1.0}),
                    ("method", "Comprendre les règles, méthodes et procédures", {"conventional": 1.0}),
                ),
            ),
            _choice(
                "Q11", "A",
                "Quel type de problème te donne le plus envie de chercher une solution ?",
                ("problem_type",),
                (
                    ("technical", "Un problème technique ou matériel", {"realistic": 0.9, "technical": 1.0}),
                    ("logical", "Un problème logique ou mathématique", {"investigative": 1.0, "logical": 1.0}),
                    ("scientific", "Une question sur le vivant, la matière ou la nature", {"investigative": 1.0, "life_science": 0.7}),
                    ("human", "Une difficulté rencontrée par des personnes", {"social": 1.0}),
                    ("organizational", "Un problème d'organisation ou de processus", {"conventional": 1.0}),
                    ("commercial", "Un problème de marché, de vente ou de développement", {"enterprising": 1.0}),
                    ("creative", "Un problème qui demande une solution originale", {"artistic": 1.0}),
                ),
            ),
            _choice(
                "Q12", "A",
                "Si tu devais apprendre un nouveau domaine pendant un mois, quelle approche te conviendrait le mieux ?",
                ("learning_mode_preference",),
                (
                    ("manual", "Faire beaucoup de pratique", {"realistic": 0.8}),
                    ("theory", "Lire et comprendre les principes", {"investigative": 0.8}),
                    ("project", "Réaliser un projet concret", {"project_learning": 1.0}),
                    ("people", "Apprendre avec un formateur ou un groupe", {"social": 0.8}),
                    ("challenge", "Me fixer un objectif ambitieux", {"enterprising": 0.8}),
                    ("structured", "Suivre une méthode ou un programme précis", {"conventional": 0.8}),
                ),
            ),
        ]
    )

    # B — abilities, learning, academic evidence and transfer.
    for qid, dim, text in (
        ("Q13", "numerical", "Je me sens capable de comprendre des nombres, calculs, graphiques ou données."),
        ("Q14", "verbal", "Je me sens capable de comprendre un texte complexe et d'en extraire l'essentiel."),
        ("Q15", "logical", "Je me sens capable de repérer une logique, une règle ou une relation dans un problème."),
        ("Q16", "technical_learning", "Je me sens capable d'apprendre rapidement un nouvel outil, logiciel, appareil ou système."),
        ("Q17", "problem_solving", "Je me sens capable de résoudre un problème que je n'ai jamais rencontré auparavant."),
        ("Q18", "communication", "Je me sens capable d'expliquer clairement une idée à quelqu'un d'autre."),
    ):
        q.append(_likert(qid, "B", text, (dim,)))

    q.extend(
        [
            _choice(
                "Q19", "B",
                "Dans quels domaines scolaires ou d'apprentissage te sens-tu actuellement le plus à l'aise ?",
                ("subjects",),
                (
                    ("math", "Mathématiques / statistiques", {"mathematics": 1.0, "numerical": 0.6}),
                    ("physical", "Physique / chimie", {"physical_science": 1.0, "technical": 0.5}),
                    ("life", "SVT / biologie / environnement", {"life_science": 1.0}),
                    ("language", "Langues / français / expression", {"language": 1.0, "verbal": 0.6}),
                    ("humanities", "Histoire / géographie / sciences humaines", {"social_science": 1.0}),
                    ("economics", "Économie / gestion / commerce", {"economics": 1.0}),
                    ("technology", "Informatique / technologie", {"technology": 1.0, "technical": 0.5}),
                    ("arts", "Arts / design / création", {"arts": 1.0}),
                    ("practical", "Travaux pratiques / atelier / activités manuelles", {"practical": 1.0, "realistic": 0.6}),
                ),
                multi=True,
                max_selections=4,
            ),
            _choice(
                "Q20", "B",
                "Comment évoluent généralement tes résultats quand tu investis du temps dans un domaine ?",
                ("trajectory",),
                (
                    ("improving", "Ils progressent nettement", {"growth": 1.0}),
                    ("stable_high", "Ils restent bons et stables", {"stability": 1.0}),
                    ("stable", "Ils restent moyens mais réguliers", {"stability": 0.5}),
                    ("volatile", "Ils varient beaucoup", {"volatility": 1.0}),
                    ("declining", "Ils diminuent malgré mes efforts", {"decline": 1.0}),
                    ("unknown", "Je n'ai pas assez de recul", {"unknown": 1.0}),
                ),
            ),
            _likert("Q21", "B", "Quand quelque chose est difficile au début, je peux continuer jusqu'à progresser.", ("persistence",)),
            _likert("Q22", "B", "Je peux apprendre seul avec des livres, cours ou ressources numériques.", ("self_directed_learning",)),
            _choice(
                "Q23", "B",
                "Quand tu dois apprendre une compétence nouvelle, quelles méthodes t'aident le plus ?",
                ("learning_strategy",),
                (
                    ("practice", "Pratiquer directement", {"project_learning": 1.0}),
                    ("examples", "Étudier des exemples puis reproduire", {"imitation_learning": 1.0}),
                    ("theory", "Comprendre la théorie avant de pratiquer", {"theoretical_learning": 1.0}),
                    ("coach", "Être accompagné par quelqu'un", {"social_learning": 1.0}),
                    ("feedback", "Faire des essais et corriger avec du feedback", {"iterative_learning": 1.0}),
                    ("documentation", "Suivre une documentation ou procédure", {"structured_learning": 1.0}),
                ),
                multi=True,
                max_selections=3,
            ),
            _likert("Q24", "B", "Je suis prêt à suivre une formation longue si elle ouvre une trajectoire qui m'intéresse vraiment.", ("education_duration_tolerance",)),
        ]
    )

    # C — values, work context and lifestyle.
    q.extend(
        [
            _choice(
                "Q25", "C",
                "Sélectionne les éléments les plus importants pour ton futur travail.",
                ("values",),
                (
                    ("income", "Bon niveau de revenu", {"income": 1.0}),
                    ("stability", "Stabilité / sécurité", {"stability": 1.0}),
                    ("autonomy", "Autonomie / liberté", {"autonomy": 1.0}),
                    ("impact", "Avoir un impact utile", {"impact": 1.0}),
                    ("creativity", "Créer / innover", {"creativity": 1.0}),
                    ("recognition", "Reconnaissance / responsabilité", {"recognition": 1.0}),
                    ("learning", "Apprendre continuellement", {"learning": 1.0}),
                    ("balance", "Équilibre vie personnelle / travail", {"balance": 1.0}),
                    ("mobility", "Mobilité / découverte", {"mobility": 1.0}),
                    ("entrepreneurship", "Créer ou développer une activité", {"entrepreneurship": 1.0}),
                    ("service", "Servir une cause ou une communauté", {"service": 1.0}),
                    ("mastery", "Devenir très compétent dans un domaine", {"mastery": 1.0}),
                ),
                multi=True,
                max_selections=5,
            ),
            _choice(
                "Q26", "C",
                "Quel niveau de contact humain souhaites-tu dans ton activité ?",
                ("human_interaction",),
                (
                    ("very_low", "Très faible", {"human_interaction": 0.0}),
                    ("low", "Faible", {"human_interaction": 0.25}),
                    ("medium", "Équilibré", {"human_interaction": 0.5}),
                    ("high", "Élevé", {"human_interaction": 0.75}),
                    ("very_high", "Très élevé", {"human_interaction": 1.0}),
                ),
            ),
            _choice(
                "Q27", "C",
                "Quel niveau de mouvement physique préfères-tu ?",
                ("physical_activity",),
                (
                    ("sedentary", "Presque toujours assis", {"physical_activity": 0.0}),
                    ("light", "Un peu de mouvement", {"physical_activity": 0.25}),
                    ("mixed", "Équilibré", {"physical_activity": 0.5}),
                    ("active", "Souvent en mouvement", {"physical_activity": 0.75}),
                    ("very_active", "Très actif / terrain", {"physical_activity": 1.0}),
                ),
            ),
            _choice(
                "Q28", "C",
                "Quel cadre de travail te convient le mieux ?",
                ("work_context",),
                (
                    ("structured", "Très structuré, avec procédures claires", {"structure_preference": 1.0}),
                    ("guided", "Cadre clair mais avec une marge de liberté", {"structure_preference": 0.75}),
                    ("balanced", "Équilibre entre cadre et liberté", {"structure_preference": 0.5}),
                    ("autonomous", "Grande autonomie dans la manière de travailler", {"structure_preference": 0.25}),
                    ("entrepreneurial", "Créer moi-même le cadre et les méthodes", {"structure_preference": 0.0, "entrepreneurship": 1.0}),
                ),
            ),
            _choice(
                "Q29", "C",
                "Comment préfères-tu collaborer ?",
                ("teamwork",),
                (
                    ("solo", "Principalement seul", {"teamwork": 0.0}),
                    ("small", "Petite équipe", {"teamwork": 0.35}),
                    ("balanced", "Seul et en équipe selon les tâches", {"teamwork": 0.5}),
                    ("team", "Équipe régulière", {"teamwork": 0.75}),
                    ("people", "Interaction constante avec les autres", {"teamwork": 1.0}),
                ),
            ),
            _choice(
                "Q30", "C",
                "Quel rythme d'activité te correspond le mieux ?",
                ("work_rhythm",),
                (
                    ("predictable", "Rythme très prévisible", {"predictability": 1.0}),
                    ("planned", "Activités planifiées avec quelques changements", {"predictability": 0.75}),
                    ("mixed", "Mélange de routine et de nouveauté", {"predictability": 0.5}),
                    ("dynamic", "Beaucoup de changements et de projets", {"predictability": 0.25}),
                    ("unpredictable", "J'aime les situations très changeantes", {"predictability": 0.0, "uncertainty_tolerance": 1.0}),
                ),
            ),
            _choice(
                "Q31", "C",
                "Quelle mobilité géographique serais-tu prêt à accepter pour une trajectoire qui te correspond ?",
                ("mobility",),
                (
                    ("local", "Rester dans ma zone actuelle", {"mobility": 0.0}),
                    ("regional", "Me déplacer dans ma région", {"mobility": 0.25}),
                    ("national", "Changer de ville dans mon pays", {"mobility": 0.5}),
                    ("international", "Changer de pays si nécessaire", {"mobility": 0.75}),
                    ("global", "Une carrière très mobile m'intéresse", {"mobility": 1.0}),
                ),
            ),
            _choice(
                "Q32", "C",
                "Quel niveau d'incertitude peux-tu accepter au début d'une trajectoire ?",
                ("uncertainty_tolerance",),
                (
                    ("very_low", "J'ai besoin de beaucoup de stabilité", {"uncertainty_tolerance": 0.0}),
                    ("low", "Plutôt stable", {"uncertainty_tolerance": 0.25}),
                    ("medium", "Équilibré", {"uncertainty_tolerance": 0.5}),
                    ("high", "Je peux m'adapter facilement", {"uncertainty_tolerance": 0.75}),
                    ("very_high", "Le changement ne me dérange pas", {"uncertainty_tolerance": 1.0}),
                ),
            ),
        ]
    )

    # D — adaptability, agency, constraints and current clarity.
    q.extend(
        [
            _likert("Q33", "D", "Je m'adapte rapidement lorsque mes priorités ou mon environnement changent.", ("adaptability",)),
            _likert("Q34", "D", "Quand je ne sais pas quoi faire, je cherche activement des informations et des solutions.", ("agency",)),
            _likert("Q35", "D", "Je peux prendre une décision même lorsque je ne dispose pas de toutes les informations.", ("decision_under_uncertainty",)),
            _likert("Q36", "D", "Je sais identifier ce que je ne maîtrise pas encore et trouver comment progresser.", ("metacognition",)),
            _choice(
                "Q37", "D",
                "Combien de temps de formation avant une activité concrète te paraît acceptable ?",
                ("constraints",),
                (
                    ("weeks", "Quelques semaines", {"training_horizon": 0.0}),
                    ("months", "Quelques mois", {"training_horizon": 0.2}),
                    ("one_two_years", "1 à 2 ans", {"training_horizon": 0.4}),
                    ("three_years", "Environ 3 ans", {"training_horizon": 0.6}),
                    ("five_years", "4 à 5 ans", {"training_horizon": 0.8}),
                    ("long", "Plus de 5 ans", {"training_horizon": 1.0}),
                    ("unknown", "Je ne sais pas encore", {"training_horizon": 0.5}),
                ),
            ),
            _choice(
                "Q38", "D",
                "Quelles contraintes doivent être prises en compte maintenant ?",
                ("constraints",),
                (
                    ("budget", "Budget de formation limité", {"budget_constraint": 1.0}),
                    ("work", "Besoin de travailler rapidement", {"time_constraint": 1.0}),
                    ("location", "Déménagement difficile", {"mobility_constraint": 1.0}),
                    ("internet", "Accès Internet / matériel limité", {"resource_constraint": 1.0}),
                    ("family", "Obligations familiales importantes", {"family_constraint": 1.0}),
                    ("hours", "Contraintes horaires", {"schedule_constraint": 1.0}),
                    ("health", "Contraintes personnelles à prendre en compte", {"personal_constraint": 1.0}),
                    ("none", "Aucune contrainte importante", {"no_constraint": 1.0}),
                ),
                multi=True,
                max_selections=4,
            ),
            _choice(
                "Q39", "D",
                "Quel niveau de risque financier serais-tu prêt à accepter au début d'une trajectoire ?",
                ("risk_tolerance",),
                (
                    ("none", "Très faible", {"risk_tolerance": 0.0}),
                    ("low", "Faible", {"risk_tolerance": 0.25}),
                    ("medium", "Modéré", {"risk_tolerance": 0.5}),
                    ("high", "Élevé", {"risk_tolerance": 0.75}),
                    ("very_high", "Très élevé", {"risk_tolerance": 1.0}),
                ),
            ),
            _choice(
                "Q40", "D",
                "Laquelle de ces affirmations te décrit le mieux aujourd'hui ?",
                ("career_clarity",),
                (
                    ("exploring", "Je découvre encore ce qui me correspond", {"career_clarity": 0.0}),
                    ("several", "J'ai plusieurs pistes sérieuses", {"career_clarity": 0.35}),
                    ("direction", "J'ai une direction mais je veux la vérifier", {"career_clarity": 0.65}),
                    ("focused", "J'ai une direction assez claire", {"career_clarity": 0.85}),
                    ("committed", "Je suis déjà engagé dans une direction précise", {"career_clarity": 1.0}),
                ),
            ),
        ]
    )

    if len(q) != 40:
        raise RuntimeError(f"V1 question bank must contain exactly 40 questions, got {len(q)}")
    if len({question.question_id for question in q}) != 40:
        raise RuntimeError("question ids must be unique")
    return tuple(q)


QUESTIONS_V1 = build_question_bank()
QUESTION_BY_ID = {question.question_id: question for question in QUESTIONS_V1}
