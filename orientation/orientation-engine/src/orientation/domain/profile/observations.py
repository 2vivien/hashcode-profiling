from orientation.contracts.common import Observation
def observation_key(observation: Observation) -> tuple[str,str]:
    return observation.dimension, observation.source.value
