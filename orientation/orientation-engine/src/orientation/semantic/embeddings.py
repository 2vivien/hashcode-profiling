from dataclasses import dataclass
from typing import Sequence
import numpy as np

@dataclass(frozen=True)
class EmbeddingDocument:
    document_id: str
    text: str

class SentenceTransformerEncoder:
    def __init__(self, model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2") -> None:
        self.model_name = model_name
        self._model: object | None = None

    def _load(self) -> object:
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def encode(self, texts: Sequence[str]) -> np.ndarray:
        model = self._load()
        result = model.encode(list(texts), normalize_embeddings=True, convert_to_numpy=True)
        return np.asarray(result, dtype=np.float32)
