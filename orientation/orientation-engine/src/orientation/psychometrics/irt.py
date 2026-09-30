import numpy as np


def sigmoid(value: np.ndarray | float) -> np.ndarray | float:
    clipped = np.clip(value, -40.0, 40.0)
    return 1.0 / (1.0 + np.exp(-clipped))


def probability_2pl(theta: float, discrimination: float, difficulty: float) -> float:
    return float(sigmoid(discrimination * (theta - difficulty)))


def fisher_information_2pl(
    theta: float,
    discrimination: float,
    difficulty: float,
) -> float:
    probability = probability_2pl(theta, discrimination, difficulty)
    return float(discrimination**2 * probability * (1.0 - probability))


def probability_mirt(
    theta: np.ndarray,
    discrimination: np.ndarray,
    difficulty: float,
) -> float:
    theta_vector = np.asarray(theta, dtype=np.float64)
    a_vector = np.asarray(discrimination, dtype=np.float64)
    if (
        theta_vector.ndim != 1
        or a_vector.ndim != 1
        or theta_vector.shape != a_vector.shape
    ):
        raise ValueError(
            "theta and discrimination must be aligned one-dimensional vectors"
        )
    return float(sigmoid(float(a_vector @ theta_vector - difficulty)))


def information_mirt(
    theta: np.ndarray,
    discrimination: np.ndarray,
    difficulty: float,
) -> np.ndarray:
    probability = probability_mirt(theta, discrimination, difficulty)
    a_vector = np.asarray(discrimination, dtype=np.float64)
    return probability * (1.0 - probability) * np.outer(a_vector, a_vector)


def estimate_mirt(
    responses: np.ndarray,
    discriminations: np.ndarray,
    difficulties: np.ndarray,
    initial: np.ndarray | None = None,
    iterations: int = 40,
    ridge: float = 1e-3,
) -> np.ndarray:
    responses_array = np.asarray(responses, dtype=np.float64)
    a_matrix = np.asarray(discriminations, dtype=np.float64)
    b_vector = np.asarray(difficulties, dtype=np.float64)
    if a_matrix.ndim != 2 or b_vector.ndim != 1 or responses_array.ndim != 1:
        raise ValueError(
            "MIRT inputs must have shapes [items, dimensions], [items], [items]"
        )
    if a_matrix.shape[0] != len(responses_array) or len(b_vector) != len(responses_array):
        raise ValueError("MIRT item arrays must align")
    theta = (
        np.zeros(a_matrix.shape[1], dtype=np.float64)
        if initial is None
        else np.asarray(initial, dtype=np.float64).copy()
    )
    if theta.shape != (a_matrix.shape[1],):
        raise ValueError("initial theta has the wrong dimension")
    for _ in range(iterations):
        probabilities = np.asarray([
            probability_mirt(theta, a_matrix[i], float(b_vector[i]))
            for i in range(len(responses_array))
        ])
        residual = responses_array - probabilities
        information = ridge * np.eye(a_matrix.shape[1], dtype=np.float64)
        gradient = -ridge * theta
        for i in range(len(responses_array)):
            a = a_matrix[i]
            gradient += residual[i] * a
            information += (
                probabilities[i]
                * (1.0 - probabilities[i])
                * np.outer(a, a)
            )
        try:
            step = np.linalg.solve(information, gradient)
        except np.linalg.LinAlgError:
            break
        theta = np.clip(theta + step, -6.0, 6.0)
        if float(np.linalg.norm(step)) < 1e-5:
            break
    return theta


def standard_error_from_information(information: np.ndarray) -> np.ndarray:
    matrix = np.asarray(information, dtype=np.float64)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError("information must be a square matrix")
    regularized = matrix + 1e-8 * np.eye(matrix.shape[0])
    return np.sqrt(np.diag(np.linalg.pinv(regularized)))
