from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class OffPolicyEstimate:
    value: float
    effective_sample_size: float


def inverse_propensity_score(
    rewards: np.ndarray,
    logged_actions: np.ndarray,
    target_actions: np.ndarray,
    logged_propensities: np.ndarray,
    min_propensity: float = 1e-3,
) -> OffPolicyEstimate:
    rewards_array = np.asarray(rewards, dtype=np.float64)
    logged = np.asarray(logged_actions)
    target = np.asarray(target_actions)
    propensities = np.asarray(logged_propensities, dtype=np.float64)
    if not (rewards_array.shape == logged.shape == target.shape == propensities.shape):
        raise ValueError("off-policy arrays must align")
    if np.any((propensities <= 0) | (propensities > 1)):
        raise ValueError("logged propensities must be in (0,1]")
    mask = logged == target
    weights = np.zeros_like(rewards_array)
    weights[mask] = 1.0 / np.maximum(propensities[mask], min_propensity)
    value = float(np.mean(weights * rewards_array))
    squared = float(np.sum(weights**2))
    ess = float((np.sum(weights) ** 2) / max(squared, 1e-12))
    return OffPolicyEstimate(value, ess)


def doubly_robust(
    rewards: np.ndarray,
    logged_actions: np.ndarray,
    target_actions: np.ndarray,
    logged_propensities: np.ndarray,
    baseline_rewards: np.ndarray,
    min_propensity: float = 1e-3,
) -> OffPolicyEstimate:
    rewards_array = np.asarray(rewards, dtype=np.float64)
    logged = np.asarray(logged_actions)
    target = np.asarray(target_actions)
    propensities = np.asarray(logged_propensities, dtype=np.float64)
    baseline = np.asarray(baseline_rewards, dtype=np.float64)
    if not (
        rewards_array.shape == logged.shape == target.shape == propensities.shape == baseline.shape
    ):
        raise ValueError("off-policy arrays must align")
    if np.any((propensities <= 0) | (propensities > 1)):
        raise ValueError("logged propensities must be in (0,1]")
    mask = logged == target
    correction = np.zeros_like(rewards_array)
    correction[mask] = (rewards_array[mask] - baseline[mask]) / np.maximum(
        propensities[mask], min_propensity
    )
    values = baseline + correction
    weights = np.zeros_like(rewards_array)
    weights[mask] = 1.0 / np.maximum(propensities[mask], min_propensity)
    ess = float((np.sum(weights) ** 2) / max(np.sum(weights**2), 1e-12))
    return OffPolicyEstimate(float(np.mean(values)), ess)


def replay_match(logged_actions: np.ndarray, target_actions: np.ndarray) -> np.ndarray:
    logged = np.asarray(logged_actions)
    target = np.asarray(target_actions)
    if logged.shape != target.shape:
        raise ValueError("actions must align")
    return logged == target
