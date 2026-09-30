def confidence_from_evidence(base: float, evidence_count: int, minimum_evidence: int) -> float:
    factor = min(1.0, evidence_count / max(minimum_evidence, 1))
    return max(0.0, min(1.0, base * (0.5 + 0.5 * factor)))
