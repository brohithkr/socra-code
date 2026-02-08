from __future__ import annotations

import json
from pathlib import Path
from typing import List, Dict

from ..config import settings
from ..problems.ingest import build_problem_bank


def load_treeinstruct(problems_path: Path, limit: int | None = None) -> List[Dict]:
    items: List[Dict] = []
    if not problems_path.exists():
        build_problem_bank(settings.code_kb_dir, problems_path)
    if not problems_path.exists():
        return items
    with problems_path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            item = json.loads(line)
            if item.get("source") != "treeinstruct":
                continue
            items.append(item)
            if limit and len(items) >= limit:
                break
    return items
