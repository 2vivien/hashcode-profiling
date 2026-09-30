from collections.abc import Callable
from dataclasses import dataclass

import numpy as np

from orientation.psychometrics.irt import (
    estimate_mirt,
    fisher_information_2pl,
    information_mirt,
    item_information,
    probability_2pl,
    standard_error_from_information,
)
from orientation.psychometrics.estimation import estimate_trait


@dataclass(frozen=True)
class CATResult:
    theta: float
    standard_error: float
    administered_items: tuple[str, ...]
    stopped: bool


class TwoPLCAT:
    def __init__(
        self,
        item_ids: list[str],
        discrimination: np.ndarray,
        difficulty: np.ndarray,
        target_se: float = 0.30,
        max_items: int = 30,
        min_items: int = 5,
    ) -> None:
        if len(item_ids) != len(discrimination) or len(item_ids) != len(difficulty):
            raise ValueError("item bank arrays must align")
        if min_items < 1 or max_items < min_items:
            raise ValueError("invalid CAT item bounds")
        self.item_ids = item_ids
        self.a = np.asarray(discrimination, dtype=np.float64)
        self.b = np.asarray(difficulty, dtype=np.float64)
        self.target_se = target_se
        self.max_items = min(max_items, len(item_ids))
        self.min_items = min_items

    def run(self, response_provider: Callable[[str], float]) -> CATResult:
        responses: list[float] = []
        administered: list[int] = []
        theta = 0.0
        for _ in range(self.max_items):
            available = [i for i in range(len(self.item_ids)) if i not in administered]
            if not available:
                break
            information = [
                fisher_information_2pl(theta, float(self.a[i]), float(self.b[i]))
                for i in available
            ]
            item_index = available[int(np.argmax(information))]
            response = float(response_provider(self.item_ids[item_index]))
            if response not in (0.0, 1.0):
                raise ValueError("2PL CAT responses must be binary")
            administered.append(item_index)
            responses.append(response)
            n = len(responses)
            theta = estimate_trait(
                np.asarray(responses),
                self.a[administered],
                self.b[administered],
                initial=theta,
            )
            total_information = sum(
                item_information(theta, float(self.a[i]), float(self.b[i]))
                for i in administered
            )
            se = float(1.0 / np.sqrt(max(total_information, 1e-9)))
            if n >= self.min_items and se <= self.target_se:
                return CATResult(theta, se, tuple(self.item_ids[i] for i in administered), True)
        total_information = sum(
            item_information(theta, float(self.a[i]), float(self.b[i]))
            for i in administered
        )
        se = float(1.0 / np.sqrt(max(total_information, 1e-9)))
        return CATResult(theta, se, tuple(self.item_ids[i] for i in administered), False)


@dataclass(frozen=True)
class MIRTResult:
    theta: tuple[float, ...]
    standard_error: tuple[float, ...]
    administered_items: tuple[str, ...]
    stopped: bool


class MIRT_CAT:
    def __init__(
        self,
        item_ids: list[str],
        discriminations: np.ndarray,
        difficulties: np.ndarray,
        target_se: float = 0.30,
        max_items: int = 40,
        min_items: int = 8,
    ) -> None:
        a = np.asarray(discriminations, dtype=np.float64)
        b = np.asarray(difficulties, dtype=np.float64)
        if a.ndim != 2 or b.ndim != 1 or a.shape[0] != len(item_ids) or len(b) != len(item_ids):
            raise ValueError("MIRT item bank arrays must align")
        self.item_ids = item_ids
        self.a = a
        self.b = b
        self.target_se = target_se
        self.max_items = min(max_items, len(item_ids))
        self.min_items = min_items

    def run(self, response_provider: Callable[[str], float]) -> MIRTResult:
        responses: list[float] = []
        administered: list[int] = []
        theta = np.zeros(self.a.shape[1], dtype=np.float64)
        for _ in range(self.max_items):
            available = [i for i in range(len(self.item_ids)) if i not in administered]
            if not available:
                break
            scores = []
            for i in available:
                info = information_mirt(theta, self.a[i], float(self.b[i]))
                scores.append(float(np.trace(info)))
            item_index = available[int(np.argmax(scores))]
            response = float(response_provider(self.item_ids[item_index]))
            if response not in (0.0, 1.0):
                raise ValueError("MIRT CAT responses must be binary")
            administered.append(item_index)
            responses.append(response)
            theta = estimate_mirt(
                np.asarray(responses),
                self.a[administered],
                self.b[administered],
                initial=theta,
            )
            total_info = sum(
                (information_mirt(theta, self.a[i], float(self.b[i])) for i in administered),
                start=np.zeros((self.a.shape[1], self.a.shape[1])),
            )
            se = standard_error_from_information(total_info)
            if len(responses) >= self.min_items and float(np.max(se)) <= self.target_se:
                return MIRTResult(
                    tuple(theta),
                    tuple(float(value) for value in se),
                    tuple(self.item_ids[i] for i in administered),
                    True,
                )
        total_info = sum(
            (information_mirt(theta, self.a[i], float(self.b[i])) for i in administered),
            start=np.zeros((self.a.shape[1], self.a.shape[1])),
        )
        se = standard_error_from_information(total_info)
        return MIRTResult(
            tuple(theta),
            tuple(float(value) for value in se),
            tuple(self.item_ids[i] for i in administered),
            False,
        )
