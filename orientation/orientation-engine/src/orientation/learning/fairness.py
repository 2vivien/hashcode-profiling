from dataclasses import dataclass
import numpy as np

@dataclass(frozen=True)
class GroupMetric:
    group: str
    positive_rate: float
    mean_score: float
    count: int

def group_metrics(groups: np.ndarray, scores: np.ndarray, threshold: float = 0.5) -> list[GroupMetric]:
    if len(groups) != len(scores):
        raise ValueError("groups and scores must align")
    result: list[GroupMetric] = []
    for group in np.unique(groups):
        mask = groups == group
        values = scores[mask]
        result.append(GroupMetric(str(group), float(np.mean(values >= threshold)),
                                  float(np.mean(values)), int(mask.sum())))
    return result
