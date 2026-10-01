# Otheloo V1 — Structured Assessment

## Purpose

The assessment is a closed-response instrument, not a career-name quiz. The 40 base items produce a latent profile that the existing deterministic recommendation engine can compare with versioned knowledge.

The pipeline is:

40Q -> validation -> normalization -> latent profile -> adaptive disambiguation -> StudentProfile -> candidate generation -> matching -> constraints -> scoring -> MMR -> explanations

Behavioral events are then appended independently so future ranking, bandit and graph models can learn from real Otheloo interactions.

## Item design

The bank is split into:

- A / Q01-Q12: interests and RIASEC signals.
- B / Q13-Q24: self-efficacy, subjects, learning and trajectory.
- C / Q25-Q32: work values, environment and lifestyle.
- D / Q33-Q40: adaptability, agency, constraints and career clarity.

Every answer is a finite option ID. There is no free-text answer in the V1 instrument.

The option-to-latent mapping is deliberately occupation-independent. An answer never says “this means software engineer”. It changes latent dimensions; the ESCO/O*NET knowledge layer determines which occupations are compatible.

## Normalization

RIASEC is normalized intra-individually across the six RIASEC dimensions. The implementation also exposes normalized Shannon entropy as a dispersion statistic. Entropy is not interpreted as psychological uncertainty by itself.

Profile confidence is separate and combines response coverage, respondent confidence and contradiction penalties.

The interest/effectiveness gaps are retained as directional signals rather than collapsed into a single score.

## Adaptive questions

When profile confidence is below 0.65, at most three predefined pairwise questions are selected. They resolve high-value ambiguities between latent directions. They never introduce free text.

## Knowledge matching

ESCO is treated as the occupational/skill knowledge layer. Its published classification provides unique concept identifiers, an occupations pillar and a skills/competences pillar, with occupation profiles containing relevant knowledge, skills and competences. The repository must pin the imported ESCO version in its knowledge manifest.

O*NET remains a complementary source for occupational interests, abilities, work activities and context. The engine must not invent an occupation mapping when the knowledge snapshot does not contain it.

## Telemetry

The event store is append-only and hash chained. Events include questionnaire completion, recommendation interactions, dwell time, favorites, comparisons, formation engagement, feedback and declared real choices.

The reward_for function is only a canonical event-to-signal mapping for dataset construction. It does not mean V3/V4/V5 are trained.

## Data status

No historical Otheloo behavior is fabricated. Until real events exist:

- V1 deterministic matching is active.
- V3 LambdaMART is not trained on Otheloo data.
- V4 contextual bandits are not online.
- V5 graph learning is not trained.

This separation is mandatory for scientific validity.
