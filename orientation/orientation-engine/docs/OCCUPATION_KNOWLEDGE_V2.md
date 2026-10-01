# Otheloo Occupation Knowledge V2

## Purpose

The recommendation engine compares a latent student profile against a broad occupational universe. It must not hard-code a small list of popular careers or turn a technology answer directly into a single job.

## Global coverage

ISCO-08 is the international hierarchical backbone. It contains 10 major groups, 43 sub-major groups, 130 minor groups and 436 unit groups.

ESCO v1.2.1 adds a multilingual occupational and skills layer. Its occupations are mapped to ISCO-08 and its current release contains 3,039 occupation concepts.

O*NET 31.0 adds 1,016 O*NET-SOC occupations and detailed information about interests, skills, abilities, work styles, tasks, work context, education and job zones.

The three sources have different scopes and must not be treated as interchangeable. ESCO is the multilingual occupation/skills backbone; ISCO is the global hierarchy; O*NET is a detailed occupational evidence source.

## Ten ISCO domains

1. Forces armées
2. Management
3. Professions intellectuelles et scientifiques
4. Professions intermédiaires
5. Administration
6. Services et vente
7. Agriculture, sylviculture et pêche
8. Industrie, artisanat et construction
9. Machines, installations et assemblage
10. Professions élémentaires

A recommendation may therefore cover technical, scientific, health, education, legal, business, creative, social, service, agricultural, industrial, craft and operational careers instead of assuming that all users want digital careers.

## Score and confidence

The V2 compatibility score is a bounded 0-100 engineering score based on interests, abilities, skills, values, environment, work style, self-efficacy, adaptability and evidence completeness.

Compatibility and confidence are deliberately separate: compatibility answers how closely the available profile evidence matches occupation evidence; confidence answers how much evidence exists and how reliable the assessment/source coverage is.

The score is not a probability of success, salary, employability or future outcome.

## Recommendation classes

- strong_fit: high compatibility plus sufficient evidence;
- good_fit: meaningful compatibility with adequate evidence;
- adjacent: a plausible neighbouring path with identifiable gaps;
- exploration: a discovery option where evidence or compatibility is insufficient for a stronger class.

This replaces a meaningless catch-all result. Unknown or weakly evidenced occupations remain visible only as explicit exploration/adjacent options with their gaps.

## Explanation

Every recommendation carries source/version, ISCO group, component scores, positive evidence, gaps, evidence count and confidence. The UI can therefore explain why a direction matched instead of displaying an unexplained percentage.

## Ingestion

Do not hand-write thousands of occupation records. For ESCO, download the official language package and ingest occupations, ISCOGroups and occupationSkillRelations; for richer skill matching also ingest skills, skillsHierarchy, digitalSkillsCollection, greenSkillsCollection and transversal-skill relations.

For O*NET, use the official 31.0 package and ingest Occupation Data, Career Interest Types, Essential Skills, Transferable Skills, Abilities, Work Styles, Work Activities, Work Context, Education, Job Zones and Tasks.

The repository contains deterministic parsers and source manifests. The upstream datasets remain versioned external inputs so Otheloo never fabricates occupational facts.

## Scientific guardrail

The questionnaire and scoring system are engineering instruments, not validated psychometric tests. Real Otheloo pilot data is required before learning weights or claiming empirical validity.
