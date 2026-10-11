"""Pile de scoring : ce qui est actif, ce qui ne l'est pas, et pourquoi."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from orientation.contracts.scoring import ScoreBreakdown
from orientation.engine.registry import ModelRegistry
from orientation.engine.stack import FairnessGuard, RecommendationStack, ScoredCandidate, vectorize
from orientation.psychometrics.bridge import ItemBank, estimate_abilities


def breakdown(value: float) -> ScoreBreakdown:
    return ScoreBreakdown(
        interest_fit=value,
        ability_fit=value,
        skill_fit=value,
        value_fit=value,
        subject_fit=value,
        self_efficacy_fit=value,
        adaptability_fit=value,
        environment_fit=value,
        trajectory_fit=value,
        semantic_fit=0.0,
        graph_fit=0.0,
        skill_gap_penalty=0.0,
        confidence=0.5,
        compatibility=value,
    )


@pytest.fixture
def empty_registry(tmp_path: Path) -> ModelRegistry:
    return ModelRegistry(tmp_path / "models")


# --- registre ------------------------------------------------------


def test_registry_reports_missing_task(empty_registry: ModelRegistry) -> None:
    assert empty_registry.get("lamdamart") is None
    assert empty_registry.describe() == []
    with pytest.raises(FileNotFoundError):
        empty_registry.require("lamdamart")


def test_registry_roundtrip(empty_registry: ModelRegistry) -> None:
    empty_registry.register(
        "lamdamart",
        {"trees": [[1.0]]},
        version="lm-1",
        trained_at="2026-10-10",
        training_samples=120,
        metrics={"ndcg": 0.71},
        training_data_version="v3",
    )
    artifact = empty_registry.require("lamdamart")
    assert artifact.available
    assert artifact.training_samples == 120
    assert artifact.metrics["ndcg"] == 0.71
    assert empty_registry.describe()[0]["task"] == "lamdamart"


def test_registry_ignores_corrupt_metadata(empty_registry: ModelRegistry) -> None:
    path = empty_registry.root / "lamdamart.meta.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("{pas du json", encoding="utf-8")
    assert empty_registry.get("lamdamart") is None


# --- pile ----------------------------------------------------------


def test_stack_is_transparent_when_nothing_is_trained(empty_registry: ModelRegistry) -> None:
    result = RecommendationStack(empty_registry).apply({"a": breakdown(0.8), "b": breakdown(0.6)})
    learned = [outcome.name for outcome in result.outcomes if outcome.active and outcome.name != "fairness"]
    assert learned == []
    assert result.model_version == "deterministic-baseline-v1"
    # Chaque couche apprise doit dire pourquoi elle n'a pas joué.
    for outcome in result.outcomes:
        if outcome.name != "fairness":
            assert not outcome.active
            assert outcome.reason


def test_stack_reports_trained_model(empty_registry: ModelRegistry) -> None:
    empty_registry.register(
        "lamdamart",
        {"trees": []},
        version="lm-1",
        trained_at="2026-10-10",
        training_samples=200,
    )
    result = RecommendationStack(empty_registry).apply({"a": breakdown(0.8)})
    ranking = next(outcome for outcome in result.outcomes if outcome.name == "ranking")
    assert ranking.active
    assert result.model_version == "deterministic-baseline-v1+ranking"


def test_stack_refuses_calibration_with_tiny_sample(empty_registry: ModelRegistry) -> None:
    empty_registry.register("calibration", {}, version="c1", trained_at="2026-10-10", training_samples=8)
    result = RecommendationStack(empty_registry).apply({"a": breakdown(0.5)})
    outcome = next(item for item in result.outcomes if item.name == "calibration")
    assert not outcome.active
    assert "8 < 20" in outcome.reason


def test_bandit_stays_off_without_exploration(empty_registry: ModelRegistry) -> None:
    empty_registry.register("bandit", {}, version="b1", trained_at="2026-10-10", training_samples=50)
    result = RecommendationStack(empty_registry).apply({"a": breakdown(0.5)}, allow_exploration=False)
    assert not next(item for item in result.outcomes if item.name == "bandit").active
    result = RecommendationStack(empty_registry).apply({"a": breakdown(0.5)}, allow_exploration=True)
    assert next(item for item in result.outcomes if item.name == "bandit").active


def test_stack_keeps_base_score_for_audit(empty_registry: ModelRegistry) -> None:
    result = RecommendationStack(empty_registry).apply({"a": breakdown(0.7)})
    assert all(candidate.base_score == candidate.score for candidate in result.candidates)


# --- garde-fou d'équité --------------------------------------------


def test_fairness_guard_damps_only_skewed_output() -> None:
    guard = FairnessGuard(threshold=0.5, damping=0.1)
    candidates = [
        ScoredCandidate("dir-f1", 0.9, 0.9),
        ScoredCandidate("dir-f2", 0.85, 0.85),
        ScoredCandidate("dir-m1", 0.8, 0.8),
    ]
    adjusted, outcome, report = guard.apply(candidates, {"dir-f1": "female", "dir-f2": "female"})
    assert outcome.active
    assert report["part_metiers_feminins"] == pytest.approx(2 / 3, abs=1e-3)
    # Le genre du marché ne sert qu'à mesurer : les autres métiers sont intacts.
    untouched = next(item for item in adjusted if item.direction_id == "dir-m1")
    assert untouched.score == 0.8
    assert untouched.base_score == 0.8
    assert max(item.score for item in adjusted) < 0.9


def test_fairness_guard_inactive_without_data() -> None:
    guard = FairnessGuard()
    candidates = [ScoredCandidate("a", 0.9, 0.9), ScoredCandidate("b", 0.8, 0.8)]
    adjusted, outcome, _ = guard.apply(candidates, {})
    assert not outcome.active
    assert [item.score for item in adjusted] == [0.9, 0.8]


def test_fairness_guard_handles_empty_candidates() -> None:
    _adjusted, outcome, _report = FairnessGuard().apply([], {"a": "female"})
    assert not outcome.active


def test_vectorize_shape_is_stable() -> None:
    matrix = vectorize([breakdown(0.5), breakdown(0.6)])
    assert matrix.shape == (2, 13)
    assert matrix.dtype == np.float64


# --- pont psychométrique ------------------------------------------


def test_psychometrics_degrades_without_calibrated_bank() -> None:
    estimate = estimate_abilities({"q1": 1.0}, ItemBank(), fallback={"investigative": 0.7})
    assert not estimate.calibrated
    assert estimate.method == "heuristic-mean"
    assert estimate.theta == {"investigative": 0.7}


def test_psychometrics_estimates_with_calibrated_bank() -> None:
    bank = ItemBank(dimensions=("a", "b"))
    # Items à discriminating distincts : sinon les deux réponses se compensent
    # exactement et le MIRT reste à zéro (les vecteurs de test s'annulaient).
    bank.add("q1", [1.0, 0.0], [0.0, 0.0])
    bank.add("q2", [0.0, 1.0], [0.0, 0.0])
    estimate = estimate_abilities({"q1": 1.0, "q2": 0.0}, bank)
    assert estimate.calibrated
    assert estimate.method == "mirt-2pl"
    assert set(estimate.theta) == {"a", "b"}
    # Un item réussi contre un item raté doit tirer le trait « a » vers le haut.
    assert estimate.theta["a"] > estimate.theta["b"]


def test_item_bank_rejects_partial_dimensions() -> None:
    bank = ItemBank(dimensions=("a", "b"))
    with pytest.raises(ValueError):
        bank.add("q1", [1.0], [0.0])


def test_item_bank_ignores_uncalibrated_items() -> None:
    bank = ItemBank(dimensions=("a",))
    bank.add("q1", [1.0], [0.0])
    estimate = estimate_abilities({"q1": 1.0, "inconnu": 0.0}, bank)
    assert estimate.calibrated
    assert set(estimate.theta) == {"a"}


def test_item_bank_loads_from_registry(tmp_path: Path) -> None:
    registry = ModelRegistry(tmp_path / "models")
    registry.register(
        "item_bank",
        {"dimensions": ["a", "b"], "items": {"q1": {"a": [1.0, 0.5], "b": [0.0, 1.0]}}},
        version="bank-1",
        trained_at="2026-10-10",
        training_samples=500,
    )
    bank = ItemBank.from_registry(root=tmp_path / "models")
    assert bank.calibrated
    assert bank.size == 1
    assert bank.dimensions == ("a", "b")


def test_item_bank_missing_registry_is_empty(tmp_path: Path) -> None:
    bank = ItemBank.from_registry(root=tmp_path / "absent")
    assert not bank.calibrated
    assert bank.size == 0


def test_registry_meta_is_valid_json(tmp_path: Path) -> None:
    registry = ModelRegistry(tmp_path)
    registry.register("graph", {"w": [1]}, version="g1", trained_at="2026-10-10", training_samples=10)
    payload = json.loads((tmp_path / "graph.meta.json").read_text(encoding="utf-8"))
    assert payload["task"] == "graph"
    assert payload["training_data_version"] is None


# --- perimetre geographique ----------------------------------------


def test_coverage_declares_france(tmp_path: Path) -> None:
    from orientation.infrastructure.knowledge.coverage import load_coverage

    path = tmp_path / "coverage.json"
    path.write_text(
        '{"version":"v3","countries":["FR"],"languages":["fr"],"country_names":{"FR":"France"},"authority":"France Travail","coverage":{"type":"national","completeness":"complete"}}',
        encoding="utf-8",
    )
    coverage = load_coverage(path)
    assert coverage.countries == ("FR",)
    assert coverage.country_count == 1
    assert coverage.is_national
    assert coverage.describe()["country_names"]["FR"] == "France"


def test_missing_coverage_does_not_crash(tmp_path: Path) -> None:
    from orientation.infrastructure.knowledge.coverage import load_coverage

    coverage = load_coverage(tmp_path / "absent.json")
    assert coverage.countries == ()
    assert "non renseignee" in coverage.note or "non renseignée" in coverage.note


def test_corrupt_coverage_is_reported_not_fatal(tmp_path: Path) -> None:
    from orientation.infrastructure.knowledge.coverage import load_coverage

    path = tmp_path / "coverage.json"
    path.write_text("{pas du json", encoding="utf-8")
    assert load_coverage(path).countries == ()


def test_shipped_coverage_is_french() -> None:
    from orientation.infrastructure.knowledge.coverage import load_coverage

    shipped = load_coverage()
    # Le depot est francais : le dire evite qu'on croie a une couverture mondiale.
    assert shipped.countries == ("FR",)
    assert "France" in shipped.authority
