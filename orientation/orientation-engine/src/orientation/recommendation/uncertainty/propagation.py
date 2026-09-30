def propagate_uncertainty(confidence: float, contradiction_count: int = 0) -> float:
    return max(0.0, min(1.0, 1.0 - confidence + min(0.5, contradiction_count * 0.1)))
