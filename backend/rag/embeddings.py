from __future__ import annotations

from typing import Iterable, List
import numpy as np
from sentence_transformers import SentenceTransformer


class EmbeddingModel:
    def __init__(self, model_name: str) -> None:
        self.model_name = model_name
        self._model = SentenceTransformer(model_name)

    def encode(self, texts: Iterable[str], batch_size: int = 32) -> np.ndarray:
        embeddings = self._model.encode(
            list(texts),
            batch_size=batch_size,
            show_progress_bar=False,
            normalize_embeddings=True,
        )
        return np.asarray(embeddings, dtype="float32")

    @property
    def dimension(self) -> int:
        return self._model.get_sentence_embedding_dimension()
