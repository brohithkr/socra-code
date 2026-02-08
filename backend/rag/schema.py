from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass
class Document:
    doc_id: str
    text: str
    metadata: Dict[str, str]
