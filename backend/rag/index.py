from __future__ import annotations

import json
from pathlib import Path
from typing import List

import faiss
import numpy as np

from .embeddings import EmbeddingModel


class RAGIndex:
    def __init__(self, index_dir: Path, embed_model: str, auto_build: bool, code_kb_dir: Path) -> None:
        self.index_dir = index_dir
        self.embed_model_name = embed_model
        self.code_kb_dir = code_kb_dir
        self.auto_build = auto_build
        self._index = None
        self._docs: List[dict] = []
        self._embedder = EmbeddingModel(embed_model)
        self._load()

    def _load(self) -> None:
        index_path = self.index_dir / "faiss.index"
        docs_path = self.index_dir / "docs.jsonl"
        if not index_path.exists() or not docs_path.exists():
            if self.auto_build:
                from .ingest import build_index

                build_index(
                    code_kb_dir=self.code_kb_dir,
                    index_dir=self.index_dir,
                    embed_model=self.embed_model_name,
                )
            else:
                return
        if index_path.exists():
            self._index = faiss.read_index(str(index_path))
        self._docs = []
        if docs_path.exists():
            with docs_path.open("r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    self._docs.append(json.loads(line))

    def search(self, query: str, top_k: int = 3) -> List[dict]:
        if not self._index or not self._docs:
            return []
        qvec = self._embedder.encode([query])
        scores, idxs = self._index.search(qvec, top_k)
        results = []
        for score, idx in zip(scores[0], idxs[0]):
            if idx < 0:
                continue
            doc = self._docs[idx]
            doc = {**doc, "score": float(score)}
            results.append(doc)
        return results
