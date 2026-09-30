import numpy as np
from sklearn.metrics import ndcg_score

def precision_at_k(relevance: np.ndarray, scores: np.ndarray, k: int = 5) -> float:
    order = np.argsort(-scores, axis=1)[:, :k]
    return float(np.mean(np.take_along_axis(relevance, order, axis=1).mean(axis=1)))

def recall_at_k(relevance: np.ndarray, scores: np.ndarray, k: int = 5) -> float:
    order = np.argsort(-scores, axis=1)[:, :k]
    hits = np.take_along_axis(relevance, order, axis=1).sum(axis=1)
    return float(np.mean(hits / np.maximum(relevance.sum(axis=1), 1)))

def ndcg_at_k(relevance: np.ndarray, scores: np.ndarray, k: int = 5) -> float:
    return float(np.mean([ndcg_score(relevance[i:i+1], scores[i:i+1], k=k)
                          for i in range(len(relevance))]))
