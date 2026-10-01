from collections.abc import Sequence

import numpy as np


class SentenceTransformer:
    def __init__(self, model_name: str) -> None: ...
    def encode_query(
        self,
        sentences: Sequence[str],
        **kwargs: object,
    ) -> np.ndarray: ...
    def encode_document(
        self,
        sentences: Sequence[str],
        **kwargs: object,
    ) -> np.ndarray: ...