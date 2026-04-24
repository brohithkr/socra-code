from __future__ import annotations

import json
from typing import Any


def parse_json(text: str) -> dict[str, Any]:
    """Extract a JSON object from a string that may contain surrounding text.

    Finds the first '{' and last '}', parses the span between them.
    If the greedy span fails to parse, falls back to the last standalone
    JSON object (from the last '{' up to and including the last '}').
    Raises ValueError if no JSON object is found or parsing fails.
    """
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON object found in text")
    try:
        return json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        # Greedy span had non-JSON content between objects; try the last object
        last_start = text.rfind("{", 0, end)
        if last_start == -1 or last_start == start:
            raise ValueError("No JSON object found in text")
        try:
            return json.loads(text[last_start : end + 1])
        except json.JSONDecodeError:
            raise ValueError("Failed to parse JSON object from text")
