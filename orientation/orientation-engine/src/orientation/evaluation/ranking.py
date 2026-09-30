import numpy as np
from sklearn.metrics import ndcg_score


def _validate(relevance: np.ndarray, scores: np.ndarray, k: int) -> None:
    if relevance.ndim != 2 or scores.ndim != 2 or relevance.shape != scores.shape:
        raise ValueError("relevance and scores must be aligned 2D arrays")
    if not 1 <= k <= relevance.shape[1]:
        raise ValueError("k must be within the candidate dimension")


def precision_at_k(
    relevance: np.ndarray,
    scores: np.ndarray,
    k: int = 5,
    positive_threshold: float = 1.0,
) -> float:
    _validate(relevance, scores, k)
    order = np.argsort(-scores, axis=1)[:, :k]
    hits = np.take_along_axis(relevance >= positive_threshold, order, axis=1)
    return float(np.mean(hits.mean(axis=1)))


def recall_at_k(
    relevance: np.ndarray,
    scores: np.ndarray,
    k: int = 5,
    positive_threshold: float = 1.0,
) -> float:
    _validate(relevance, scores, k)
    order = np.argsort(-scores, axis=1)[:, :k]
    hits = np.take_along_axis(relevance >= positive_threshold, order, axis=1).sum(axis=1)
    available = (relevance >= positive_threshold).sum(axis=1)
    return float(np.mean(hits / np.maximum(available, 1)))


def average_precision_at_k(
    relevance: np.ndarray,
    scores: np.ndarray,
    k: int = 5,
    positive_threshold: float = 1.0,
) -> float:
    _validate(relevance, scores, k)
    values: list[float] = []
    for row in range(len(relevance)):
        order = np.argsort(-scores[row])[:k]
        binary = (relevance[row, order] >= positive_threshold).astype(np.float64)
        cumulative = np.cumsum(binary)
        precision = cumulative / np.arange(1, k + 1)
        denominator = max(float(binary.sum()), 1.0)
        values.append(float(np.sum(precision * binary) / denominator))
    return float(np.mean(values))


def reciprocal_rank(
    relevance: np.ndarray,
    scores: np.ndarray,
    positive_threshold: float = 1.0,
) -> float:
    if relevance.ndim != 2 or scores.shape != relevance.shape:
        raise ValueError("relevance and scores must be aligned 2D arrays")
    ranks: list[float] = []
    for row in range(len(relevance)):
        order = np.argsort(-scores[row])
        hits = np.flatnonzero(relevance[row, order] >= positive_threshold)
        ranks.append(float(1.0 / (hits[0] + 1)) if len(hits) else 0.0)
    return float(np.mean(ranks))


def ndcg_at_k(relevance: np.ndarray, scores: np.ndarray, k: int = 5) -> float:
    _validate(relevance, scores, k)
    return float(np.mean([
        ndcg_score(relevance[i:i + 1], scores[i:i + 1], k=k)
        for i in range(len(relevance))
    ]))
