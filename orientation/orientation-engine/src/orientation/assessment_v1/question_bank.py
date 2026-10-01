from orientation.assessment_v1.models import AnswerOption, Question


def _likert(question_id: str, block: str, text: str, dimensions: tuple[str, ...], prefix: str) -> Question:
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
            AnswerOption(option_id=f"{prefix}_{code}", label=label, value=value)
            for code, label, value in labels
        ),
        dimensions=dimensions,
    )


def _choice(question_id: str, block: str, text: str, dimensions: tuple[str, ...], options: tuple[tuple[str, str, dict[str, float]], ...], *, multi: bool = False, max_selections: int = 1) -> Question:
    return Question(
        question_id=question_id,
        block=block,
        text=text,
        response_type="multi" if multi else "single",
        min_selections=1,
        max_selections=max_selections,
        options=tuple(AnswerOption(option_id=i, label=l, latent_weights=w) for i, l, w in options),
        dimensions=dimensions,
    )


def build_question_bank() -> tuple[Question, ...]:
    q: list[Question] = []
    # A — interests / RIASEC. Wording deliberately avoids naming occupations.
    riasec = (
        ("realistic", "J'aime fabriquer, réparer, installer ou manipuler des objets, outils ou équipements."),
        ("investigative", "J'aime comprendre les causes d'un phénomène, analyser des informations et résoudre des problèmes complexes."),
        ("artistic", "J'aime imaginer, créer ou donner une forme originale à des idées."),
        ("social", "J'aime expliquer, accompagner, écouter ou aider d'autres personnes."),
        ("enterprising", "J'aime défendre une idée, négocier, prendre des initiatives ou entraîner d'autres personnes."),
        ("conventional", "J'aime organiser, classer, vérifier et structurer des informations ou des processus."),
    )
    for i, (dim, text) in enumerate(riasec, 1):
        q.append(_likert(f"Q{i:02d}", "A", text, (dim,), f"q{i:02d}"))

    q.extend([
        _choice("Q07", "A", "Quand tu dois résoudre un problème, quelle approche te vient le plus naturellement ?", ("problem_solving",), (
            ("decompose", "Le décomposer en petites étapes", {"analytical": 1.0}),
            ("experiment", "Essayer plusieurs solutions et observer le résultat", {"experimental": 1.0}),
            ("research", "Chercher des informations et des exemples", {"research": 1.0}),
            ("ask", "Demander à quelqu'un qui s'y connaît", {"collaborative": 1.0}),
            ("intuitive", "Commencer par une intuition puis l'affiner", {"creative_problem_solving": 1.0}),
        )),
        _choice("Q08", "A", "Quel type de résultat te satisfait le plus ?", ("activity_preference",), (
            ("concrete", "Un objet, système ou résultat concret", {"realistic": 1.0}),
            ("knowledge", "Une explication ou découverte", {"investigative": 1.0}),
            ("creation", "Une création originale", {"artistic": 1.0}),
            ("human", "Une personne aidée ou qui progresse", {"social": 1.0}),
            ("growth", "Un projet qui progresse et produit un résultat", {"enterprising": 1.0}),
            ("order", "Un système mieux organisé", {"conventional": 1.0}),
        )),
        _choice("Q09", "A", "Quelles activités pourrais-tu pratiquer longtemps sans qu'on te pousse ?", ("activity_preference",), (
            ("solve", "Résoudre des problèmes", {"investigative": 1.0}),
            ("create", "Créer / concevoir", {"artistic": 1.0}),
            ("help", "Expliquer / aider", {"social": 1.0}),
            ("analyze", "Analyser des données ou informations", {"investigative": 0.8, "conventional": 0.2}),
            ("build", "Construire / réparer", {"realistic": 1.0}),
            ("sell", "Présenter / vendre / négocier", {"enterprising": 1.0}),
            ("organize", "Organiser / planifier", {"conventional": 1.0}),
        ), multi=True, max_selections=3),
        _choice("Q10", "A", "Quand tu veux découvrir un nouveau domaine, qu'est-ce qui t'attire d'abord ?", ("curiosity",), (
            ("how", "Comprendre comment cela fonctionne", {"investigative": 1.0}),
            ("do", "Essayer par moi-même", {"realistic": 0.7, "experimental": 0.3}),
            ("create", "Voir ce que je peux créer avec", {"artistic": 1.0}),
            ("people", "Comprendre son utilité pour les personnes", {"social": 1.0}),
            ("opportunity", "Voir quelles opportunités cela ouvre", {"enterprising": 1.0}),
            ("structure", "Comprendre les règles et méthodes", {"conventional": 1.0}),
        )),
        _choice("Q11", "A", "Quel environnement d'activité t'attire spontanément ?", ("environment_interest",), (
            ("nature", "Nature / vivant / terrain", {"life_science": 1.0, "realistic": 0.5}),
            ("lab", "Laboratoire / expérimentation", {"investigative": 1.0}),
            ("studio", "Studio / création", {"artistic": 1.0}),
            ("people", "Lieu où l'on accompagne des personnes", {"social": 1.0}),
            ("business", "Entreprise / projet / commerce", {"enterprising": 1.0}),
            ("office", "Environnement organisé / administratif", {"conventional": 1.0}),
        )),
        _choice("Q12", "A", "À quel point serais-tu prêt à explorer un domaine que tu connais peu avant de l'écarter ?", ("openness",), (
            ("low", "Très peu", {"openness": -1.0}),
            ("medium_low", "Peu", {"openness": -0.5}),
            ("neutral", "Cela dépend", {"openness": 0.0}),
            ("medium_high", "Beaucoup", {"openness": 0.5}),
            ("high", "Très facilement", {"openness": 1.0}),
        )),
    ])

    # B — abilities, self-efficacy, academic trajectory.
    ability_items = (
        ("Q13", "numerical", "Je me sens capable de comprendre des nombres, des calculs ou des données."),
        ("Q14", "verbal", "Je me sens capable de comprendre un texte complexe et d'en extraire l'essentiel."),
        ("Q15", "logical", "Je me sens capable de repérer une logique, une règle ou une relation dans un problème."),
        ("Q16", "technical_learning", "Je me sens capable d'apprendre rapidement un nouvel outil, logiciel, appareil ou système."),
        ("Q17", "problem_solving", "Je me sens capable de résoudre un problème que je n'ai jamais rencontré auparavant."),
        ("Q18", "communication", "Je me sens capable d'expliquer clairement une idée à quelqu'un d'autre."),
    )
    for qid, dim, text in ability_items:
        q.append(_likert(qid, "B", text, (dim,), qid.lower()))
    q.extend([
        _choice("Q19", "B", "Quelles matières ou domaines scolaires te semblent actuellement les plus faciles ?", ("subjects",), (
            ("math", "Mathématiques", {"mathematics": 1.0}),
            ("science", "Sciences physiques / chimiques", {"physical_science": 1.0}),
            ("life", "SVT / sciences du vivant", {"life_science": 1.0}),
            ("language", "Langues / français / expression", {"language": 1.0}),
            ("social", "Histoire / géographie / sciences humaines", {"social_science": 1.0}),
            ("economics", "Économie / gestion", {"economics": 1.0}),
            ("technology", "Informatique / technologie", {"technology": 1.0}),
            ("arts", "Arts / création", {"arts": 1.0}),
        ), multi=True, max_selections=4),
        _choice("Q20", "B", "Comment décrirais-tu l'évolution de tes résultats dans les domaines qui t'intéressent ?", ("trajectory",), (
            ("improving", "Ils progressent", {"growth": 1.0}),
            ("stable_high", "Ils sont bons et stables", {"stability": 1.0}),
            ("stable", "Ils sont plutôt stables", {"stability": 0.5}),
            ("volatile", "Ils varient beaucoup", {"volatility": 1.0}),
            ("declining", "Ils diminuent actuellement", {"decline": 1.0}),
            ("unknown", "Je ne sais pas / je n'ai pas assez de recul", {"unknown": 1.0}),
        )),
        _likert("Q21", "B", "Quand quelque chose est difficile au début, je peux continuer à apprendre jusqu'à le maîtriser.", ("persistence",), "q21"),
        _likert("Q22", "B", "Je suis capable d'apprendre seul avec des ressources disponibles en ligne ou dans des livres.", ("self_directed_learning",), "q22"),
        _likert("Q23", "B", "Je préfère apprendre une compétence en la pratiquant sur un projet réel.", ("project_learning",), "q23"),
        _likert("Q24", "B", "Je peux accepter une formation longue si elle ouvre une trajectoire qui m'intéresse vraiment.", ("education_duration_tolerance",), "q24"),
    ])

    # C — values and lifestyle.
    q.extend([
        _choice("Q25", "C", "Sélectionne les éléments les plus importants pour ton futur travail.", ("values",), (
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
        ), multi=True, max_selections=5),
        _choice("Q26", "C", "Quel niveau de contact humain souhaites-tu dans ton activité ?", ("human_interaction",), (
            ("very_low", "Très faible", {"human_interaction": 0.0}),
            ("low", "Faible", {"human_interaction": 0.25}),
            ("medium", "Équilibré", {"human_interaction": 0.5}),
            ("high", "Élevé", {"human_interaction": 0.75}),
            ("very_high", "Très élevé", {"human_interaction": 1.0}),
        )),
        _choice("Q27", "C", "Quel niveau de mouvement physique préfères-tu ?", ("physical_activity",), (
            ("sedentary", "Presque toujours assis", {"physical_activity": 0.0}),
            ("light", "Un peu de mouvement", {"physical_activity": 0.25}),
            ("mixed", "Équilibré", {"physical_activity": 0.5}),
            ("active", "Souvent en mouvement", {"physical_activity": 0.75}),
            ("very_active", "Très actif / terrain", {"physical_activity": 1.0}),
        )),
        _choice("Q28", "C", "Quel niveau d'incertitude peux-tu accepter dans ton activité ?", ("uncertainty_tolerance",), (
            ("very_low", "J'ai besoin de beaucoup de stabilité", {"uncertainty_tolerance": 0.0}),
            ("low", "Plutôt stable", {"uncertainty_tolerance": 0.25}),
            ("medium", "Équilibré", {"uncertainty_tolerance": 0.5}),
            ("high", "Je peux m'adapter facilement", {"uncertainty_tolerance": 0.75}),
            ("very_high", "J'apprécie fortement l'incertitude et le changement", {"uncertainty_tolerance": 1.0}),
        )),
        _choice("Q29", "C", "Quel cadre de travail te convient le mieux ?", ("work_context",), (
            ("structured", "Très structuré", {"structure_preference": 1.0}),
            ("guided", "Avec un cadre mais une certaine liberté", {"structure_preference": 0.75}),
            ("balanced", "Équilibré", {"structure_preference": 0.5}),
            ("autonomous", "Très autonome", {"structure_preference": 0.25}),
            ("entrepreneurial", "Je préfère créer mon propre cadre", {"structure_preference": 0.0, "entrepreneurship": 1.0}),
        )),
        _choice("Q30", "C", "Quel mode de collaboration préfères-tu ?", ("teamwork",), (
            ("solo", "Principalement seul", {"teamwork": 0.0}),
            ("small", "Petite équipe", {"teamwork": 0.35}),
            ("balanced", "Seul et en équipe selon les tâches", {"teamwork": 0.5}),
            ("team", "Équipe régulière", {"teamwork": 0.75}),
            ("people", "Interaction constante avec les autres", {"teamwork": 1.0}),
        )),
        _likert("Q31", "C", "Je veux conserver une grande liberté dans la manière dont j'organise mon travail.", ("autonomy",), "q31"),
        _likert("Q32", "C", "Je serais prêt à changer de ville ou de pays pour une formation ou une trajectoire qui me correspond.", ("mobility",), "q32"),
    ])

    # D — adaptability, agency, constraints and consistency.
    q.extend([
        _likert("Q33", "D", "Je peux m'adapter rapidement lorsque mes priorités ou mon environnement changent.", ("adaptability",), "q33"),
        _likert("Q34", "D", "Quand je ne sais pas quoi faire, je suis capable de chercher activement des informations et des solutions.", ("agency",), "q34"),
        _likert("Q35", "D", "Je peux prendre une décision même lorsque je ne dispose pas de toutes les informations.", ("decision_under_uncertainty",), "q35"),
        _likert("Q36", "D", "Je sais identifier ce que je ne maîtrise pas encore et chercher comment progresser.", ("metacognition",), "q36"),
        _choice("Q37", "D", "Combien de temps de formation avant une activité concrète te paraît acceptable ?", ("constraints",), (
            ("weeks", "Quelques semaines", {"training_horizon": 0.0}),
            ("months", "Quelques mois", {"training_horizon": 0.2}),
            ("one_two_years", "1 à 2 ans", {"training_horizon": 0.4}),
            ("three_years", "Environ 3 ans", {"training_horizon": 0.6}),
            ("five_years", "4 à 5 ans", {"training_horizon": 0.8}),
            ("long", "Plus de 5 ans", {"training_horizon": 1.0}),
            ("unknown", "Je ne sais pas encore", {"training_horizon": 0.5}),
        )),
        _choice("Q38", "D", "Quelles contraintes doivent être prises en compte maintenant ?", ("constraints",), (
            ("budget", "Budget de formation limité", {"budget_constraint": 1.0}),
            ("work", "Besoin de travailler rapidement", {"time_constraint": 1.0}),
            ("location", "Déménagement difficile", {"mobility_constraint": 1.0}),
            ("internet", "Accès Internet / matériel limité", {"resource_constraint": 1.0}),
            ("family", "Obligations familiales importantes", {"family_constraint": 1.0}),
            ("hours", "Contraintes horaires", {"schedule_constraint": 1.0}),
            ("none", "Aucune contrainte importante", {"no_constraint": 1.0}),
        ), multi=True, max_selections=4),
        _choice("Q39", "D", "Quel niveau de risque financier es-tu prêt à accepter au début d'une trajectoire ?", ("risk_tolerance",), (
            ("none", "Très faible", {"risk_tolerance": 0.0}),
            ("low", "Faible", {"risk_tolerance": 0.25}),
            ("medium", "Modéré", {"risk_tolerance": 0.5}),
            ("high", "Élevé", {"risk_tolerance": 0.75}),
            ("very_high", "Très élevé", {"risk_tolerance": 1.0}),
        )),
        _choice("Q40", "D", "Laquelle de ces affirmations te décrit le mieux aujourd'hui ?", ("career_clarity",), (
            ("exploring", "Je découvre encore ce qui me correspond", {"career_clarity": 0.0}),
            ("several", "J'ai plusieurs pistes sérieuses", {"career_clarity": 0.35}),
            ("direction", "J'ai une direction mais je veux la vérifier", {"career_clarity": 0.65}),
            ("focused", "J'ai une direction assez claire", {"career_clarity": 0.85}),
            ("committed", "Je suis déjà engagé dans une direction précise", {"career_clarity": 1.0}),
        )),
    ])
    if len(q) != 40:
        raise RuntimeError(f"V1 question bank must contain exactly 40 questions, got {len(q)}")
    return tuple(q)


QUESTIONS_V1 = build_question_bank()
QUESTION_BY_ID = {question.question_id: question for question in QUESTIONS_V1}
