from __future__ import annotations

from pathlib import Path
from typing import List

from ..rag.index import RAGIndex


class RAGEngine:
    def __init__(self, index_dir: Path, embed_model: str, auto_build: bool, code_kb_dir: Path) -> None:
        self.index = RAGIndex(
            index_dir=index_dir,
            embed_model=embed_model,
            auto_build=auto_build,
            code_kb_dir=code_kb_dir,
        )

    def search(self, query: str, top_k: int = 3) -> List[str]:
        results = self.index.search(query=query, top_k=top_k)
        snippets = []
        for doc in results:
            text = doc.get("text", "")
            meta = doc.get("metadata", {})
            header = f"Source: {meta.get('source','unknown')} | Path: {meta.get('path','')}"
            snippets.append(f"{header}\n{text}")
        return snippets
