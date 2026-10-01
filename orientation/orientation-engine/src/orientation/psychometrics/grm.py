import numpy as np


def cumulative_probability(
    theta: float,
    discrimination: float,
    threshold: float,
) -> float:
    z = discrimination * (theta - threshold)
    return float(1.0 / (1.0 + np.exp(-np.clip(z, -40.0, 40.0))))


def category_probabilities(
    theta: float,
    discrimination: float,
    thresholds: np.ndarray,
) -> np.ndarray:
    cumulative = np.array(
        [cumulative_probability(theta, discrimination, threshold) for threshold in thresholds]
    )
    upper = np.concatenate(([1.0], cumulative, [0.0]))
    return upper[:-1] - upper[1:]
