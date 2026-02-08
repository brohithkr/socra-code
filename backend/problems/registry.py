from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from .ingest import build_problem_bank


class ProblemRegistry:
    def __init__(self, problems_path: Path, code_kb_dir: Path) -> None:
        self.problems_path = problems_path
        self.code_kb_dir = code_kb_dir
        self._problems: Dict[str, dict] = {}
        self._load()

    def _load(self) -> None:
        if not self.problems_path.exists():
            build_problem_bank(self.code_kb_dir, self.problems_path)
        if not self.problems_path.exists():
            return
        self._problems.clear()
        with self.problems_path.open("r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                data = json.loads(line)
                self._problems[data["id"]] = data

    def list(self, language: Optional[str] = None, kind: Optional[str] = None, limit: int = 50) -> List[dict]:
        items = list(self._problems.values())
        if language:
            items = [p for p in items if p.get("language") == language]
        if kind:
            items = [p for p in items if p.get("kind") == kind]
        return items[:limit]

    def get(self, problem_id: str) -> Optional[dict]:
        return self._problems.get(problem_id)
