# Orientation data lifecycle

Knowledge sources:
1. ESCO official releases.
2. O*NET official database releases.
3. Otheloo local formations, institutions, diplomas, admissions, cost, duration, language, location and opportunities.
4. Otheloo product events: observations, candidate sets, ranking positions, feedback, exploration and outcomes.

Rules:
- Knowledge Base data is not a training dataset.
- Every record keeps source, version, timestamp and provenance.
- Missing is not zero.
- Contradictions are retained for evaluation.
- Local mappings require review.
- Training data uses time-based splits to prevent leakage.
- Product feedback is evidence, not automatic truth.
- Real user data requires the applicable consent, privacy and de-identification controls.

The production ranking dataset must contain a stable event identifier, student pseudonym, direction identifier, candidate position, model/knowledge versions, feature snapshot, feedback event, outcome and timestamp.
