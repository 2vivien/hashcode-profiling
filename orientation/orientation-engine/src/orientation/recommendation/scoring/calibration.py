def clamp_compatibility(score: float) -> float:
    """Keep a compatibility score in [0,1]; this is not probability calibration."""
    return max(0.0, min(1.0, score))
