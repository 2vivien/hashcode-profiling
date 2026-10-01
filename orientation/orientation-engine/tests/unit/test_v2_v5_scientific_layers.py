from pathlib import Path

import numpy as np

from orientation.evaluation.offpolicy import doubly_robust, inverse_propensity_score
from orientation.evaluation.ranking import ndcg_at_k, precision_at_k, recall_at_k
from orientation.learning.bandits import LinUCB
from orientation.learning.calibration import ScoreCalibrator
from orientation.learning.graph import GraphEdge, KnowledgeGraph
from orientation.learning.rgcn import RGCNConfig, RGCNModel
from orientation.psychometrics.cat import MIRT_CAT, TwoPLCAT
from orientation.psychometrics.irt import estimate_mirt, probability_2pl
from orientation.semantic.vector_index import NumpyVectorIndex


def test_mirt_probability_and_estimation() -> None:
    probability = probability_2pl(0.0, 1.0, 0.0)
    assert probability == 0.5
    theta = estimate_mirt(
        np.array([1.0, 0.0, 1.0]),
        np.array([[1.0, 0.0], [0.0, 1.0], [0.8, 0.8]]),
        np.array([0.0, 0.0, 0.0]),
    )
    assert theta.shape == (2,)


def test_two_pl_cat_selects_informative_items() -> None:
    responses = {"i1": 1.0, "i2": 0.0, "i3": 1.0}
    cat = TwoPLCAT(
        ["i1", "i2", "i3"],
        np.array([1.0, 1.0, 1.0]),
        np.array([0.0, 0.0, 0.0]),
        min_items=2,
        max_items=3,
    )
    result = cat.run(responses.__getitem__)
    assert len(result.administered_items) >= 2


def test_mirt_cat_runs() -> None:
    responses = {"a": 1.0, "b": 0.0, "c": 1.0}
    cat = MIRT_CAT(
        ["a", "b", "c"],
        np.array([[1.0, 0.0], [0.0, 1.0], [0.8, 0.8]]),
        np.zeros(3),
        min_items=2,
        max_items=3,
    )
    result = cat.run(responses.__getitem__)
    assert len(result.theta) == 2


def test_bandit_propensity_matches_policy() -> None:
    policy = LinUCB(2, epsilon=0.1)
    action = policy.select(
        {"a": np.array([1.0, 0.0]), "b": np.array([0.0, 1.0])},
        rng=np.random.default_rng(4),
    )
    assert 0.0 < action.propensity < 1.0


def test_offpolicy_estimators_use_action_match_and_propensity() -> None:
    rewards = np.array([1.0, 0.0])
    logged = np.array(["a", "b"])
    target = np.array(["a", "a"])
    propensities = np.array([0.5, 0.5])
    ips = inverse_propensity_score(rewards, logged, target, propensities)
    dr = doubly_robust(
        rewards,
        logged,
        target,
        propensities,
        np.array([0.5, 0.5]),
    )
    assert ips.value == 1.0
    assert dr.value == 1.0


def test_calibration_requires_both_classes() -> None:
    calibrator = ScoreCalibrator("sigmoid")
    scores = np.linspace(-2.0, 2.0, 20)
    labels = np.array([0, 1] * 10)
    report = calibrator.fit(scores, labels)
    assert report.sample_count == 20
    assert np.all(
        (calibrator.predict(scores) >= 0)
        & (calibrator.predict(scores) <= 1)
    )


def test_graph_and_rgcn() -> None:
    graph = KnowledgeGraph()
    graph.add_edges([GraphEdge("skill", "training", "DEVELOPS_SKILL")])
    assert graph.score("skill", "training") > 0
    model = RGCNModel(RGCNConfig(hidden_dim=4, epochs=10, learning_rate=0.02))
    features = np.eye(3)
    edges = np.array([[0, 1], [1, 2]])
    relations = np.array([0, 1])
    labels = np.array([0, 1, 1])
    model.fit(features, edges, relations, labels)
    predictions = model.predict(features, edges, relations)
    assert predictions.shape == (3, 2)


def test_ranking_metrics() -> None:
    relevance = np.array([[1.0, 0.0, 1.0]])
    scores = np.array([[0.9, 0.1, 0.8]])
    assert precision_at_k(relevance, scores, 2) == 1.0
    assert recall_at_k(relevance, scores, 2) == 1.0
    assert ndcg_at_k(relevance, scores, 2) > 0.9


def test_vector_index_persists(tmp_path: Path) -> None:
    index = NumpyVectorIndex()
    index.fit(
        ["a", "b"],
        np.array([[1.0, 0.0], [0.0, 1.0]], dtype=np.float32),
    )
    path = tmp_path / "vectors.npz"
    index.save(path)
    restored = NumpyVectorIndex()
    restored.load(path)
    assert restored.search(np.array([1.0, 0.0]), 1)[0].document_id == "a"
