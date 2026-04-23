from __future__ import annotations

from collections import OrderedDict
from pathlib import Path
from typing import List

from ..rag.index import RAGIndex


class RAGEngine:
    def __init__(
        self,
        index_dir: Path,
        embed_model: str,
        auto_build: bool,
        code_kb_dir: Path,
        cache_size: int = 128,
    ) -> None:
        self.index = RAGIndex(
            index_dir=index_dir,
            embed_model=embed_model,
            auto_build=auto_build,
            code_kb_dir=code_kb_dir,
        )
        self.cache_size = max(0, cache_size)
        self._cache: OrderedDict[tuple[str, int], List[str]] = OrderedDict()

    def search(self, query: str, top_k: int = 3) -> List[str]:
        cache_key = (query, top_k)
        if self.cache_size > 0 and cache_key in self._cache:
            self._cache.move_to_end(cache_key)
            return list(self._cache[cache_key])

        results = self.index.search(query=query, top_k=top_k)
        snippets = []
        for doc in results:
            text = doc.get("text", "")
            meta = doc.get("metadata", {})
            header = f"Source: {meta.get('source','unknown')} | Path: {meta.get('path','')}"
            snippets.append(f"{header}\n{text}")
        if self.cache_size > 0:
            self._cache[cache_key] = list(snippets)
            self._cache.move_to_end(cache_key)
            while len(self._cache) > self.cache_size:
                self._cache.popitem(last=False)
        return snippets
