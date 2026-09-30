from orientation.contracts.scoring import MatchResult

def evidence_keys(match: MatchResult) -> list[str]:
    return sorted(match.evidence)
