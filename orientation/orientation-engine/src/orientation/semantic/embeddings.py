from typing import Protocol, Sequence, cast

import numpy as np


class _SentenceEncoder(Protocol):
    def encode_query(self, sentences: Sequence[str], **kwargs: object) -> np.ndarray: ...

    def encode_document(self, sentences: Sequence[str], **kwargs: object) -> np.ndarray: ...


class SentenceTransformerEncoder:
    def __init__(
        self,
        model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    ) -> None:
        self.model_name = model_name
        self._model: _SentenceEncoder | None = None

    def _load(self) -> _SentenceEncoder:
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = cast(_SentenceEncoder, SentenceTransformer(self.model_name))
        return self._model

    def encode_documents(self, texts: Sequence[str]) -> np.ndarray:
        result = self._load().encode_document(
            list(texts),
            normalize_embeddings=True,
            convert_to_numpy=True,
        )
        return np.asarray(result, dtype=np.float32)

    def encode_query(self, texts: Sequence[str]) -> np.ndarray:
        result = self._load().encode_query(
            list(texts),
            normalize_embeddings=True,
            convert_to_numpy=True,
        )
        return np.asarray(result, dtype=np.float32)
