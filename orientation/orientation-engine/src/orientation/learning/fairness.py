from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class GroupMetric:
    group: str
    positive_rate: float
    true_positive_rate: float
    mean_score: float
    count: int


@dataclass(frozen=True)
class FairnessReport:
    groups: tuple[GroupMetric, ...]
    demographic_parity_gap: float
    equal_opportunity_gap: float


def fairness_report(
    groups: np.ndarray,
    scores: np.ndarray,
    labels: np.ndarray,
    threshold: float = 0.5,
) -> FairnessReport:
    group_array = np.asarray(groups)
    score_array = np.asarray(scores, dtype=np.float64)
    label_array = np.asarray(labels, dtype=np.int64)
    if not (len(group_array) == len(score_array) == len(label_array)):
        raise ValueError("groups, scores and labels must align")
    if not np.all(np.isin(label_array, (0, 1))):
        raise ValueError("fairness labels must be binary")
    metrics: list[GroupMetric] = []
    for group in np.unique(group_array):
        mask = group_array == group
        predictions = score_array[mask] >= threshold
        positives = label_array[mask] == 1
        tpr_denominator = int(positives.sum())
        tpr = float(np.sum(predictions & positives) / max(tpr_denominator, 1))
        metrics.append(
            GroupMetric(
                group=str(group),
                positive_rate=float(np.mean(predictions)),
                true_positive_rate=tpr,
                mean_score=float(np.mean(score_array[mask])),
                count=int(mask.sum()),
            )
        )
    positive_rates = [metric.positive_rate for metric in metrics]
    true_positive_rates = [metric.true_positive_rate for metric in metrics]
    return FairnessReport(
        groups=tuple(metrics),
        demographic_parity_gap=float(max(positive_rates) - min(positive_rates)),
        equal_opportunity_gap=float(max(true_positive_rates) - min(true_positive_rates)),
    )
