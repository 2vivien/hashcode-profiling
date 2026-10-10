# Trace des issues créées — 2026-10-10

Créées via `gh issue create` sur 2vivien/hashcode-profiling :

- #10 [AUDIT] État code V1-V5 – prêt vs non prêt
- #11 [ARCHITECTURE] Architecture actuelle non optimisée pour API et communication inter-outils
- #12 [CORE] Proposer nouvelle architecture au cœur : transport + pipeline + événement bus
- #13 [CODE] Remplacer GenerateRecommendation global par PipelineOrchestrator injecté
- #14 [CODE] Ajouter événement bus minimal au cœur pour inter-outils
- #15 [ARCH] Séparer inference stateless et workers batch dans le dépôt

Références locales :
- orientation/31-audit-coherence-code-blueprint-v1-v5.md
- orientation/25-blueprint-implementation-moteur.md
- orientation/18-industrialisation-microservices-donnees-regles.md
- orientation/13-architecture-technique.md
- orientation/26-blueprint-technique-code-environnement-modeles.md

# Mise à jour — résolution en cours
- #13 : PipelineOrchestrator injecté (fichier créé, routes nettoyées) — OPEN
- #14 : Bus minimal (schemas + event_bus créés) — OPEN
- #15 : Workers séparés (inference/training/batch/audit créés) — OPEN
- Principe validé : Otheloo = 1er consommateur REST, service indépendant, pas d'intégration dans backend Node
