import numpy as np


def two_parameter(theta: float, slope: float, location: float) -> float:
    z = slope * (theta - location)
    return float(1.0 / (1.0 + np.exp(-np.clip(z, -40.0, 40.0))))


def item_information(theta: float, slope: float, location: float) -> float:
    value = two_parameter(theta, slope, location)
    return float(slope**2 * value * (1.0 - value))


def estimate_trait(
    responses: np.ndarray,
    slopes: np.ndarray,
    locations: np.ndarray,
    initial: float = 0.0,
    iterations: int = 30,
) -> float:
    theta = initial
    for _ in range(iterations):
        values = np.array([
            two_parameter(theta, a, b)
            for a, b in zip(slopes, locations, strict=True)
        ])
        score = float(np.sum(responses - values))
        information = float(np.sum(slopes**2 * values * (1.0 - values)))
        if information < 1e-8:
            break
        theta = float(np.clip(theta + score / information, -6.0, 6.0))
    return theta
