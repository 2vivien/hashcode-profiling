from orientation.contracts.recommendation import RecommendationItem


def diversify(
    items: list[RecommendationItem], final_k: int, lambda_value: float
) -> list[RecommendationItem]:
    selected: list[RecommendationItem] = []
    remaining = list(items)
    while remaining and len(selected) < final_k:

        def objective(item: RecommendationItem) -> tuple[float, str]:
            similarity = max(
                (1.0 if item.taxonomy == chosen.taxonomy else 0.0 for chosen in selected),
                default=0.0,
            )
            return (lambda_value * item.score - (1 - lambda_value) * similarity, item.direction_id)

        best = max(remaining, key=objective)
        selected.append(best)
        remaining.remove(best)
    return selected
