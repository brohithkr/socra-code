from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class Problem:
    problem_id: str
    title: str
    language: str
    statement: str
    starter_code: str
    buggy_code: Optional[str]
    bug_desc: Optional[str]
    bug_fixes: Optional[str]
    topic: Optional[str]
    source: str
    kind: str
