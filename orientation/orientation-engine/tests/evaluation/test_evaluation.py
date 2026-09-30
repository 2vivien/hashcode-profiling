from orientation.recommendation.uncertainty.propagation import propagate_uncertainty


def test_uncertainty_increases_when_confidence_decreases() -> None:
    assert propagate_uncertainty(0.2) > propagate_uncertainty(0.8)
