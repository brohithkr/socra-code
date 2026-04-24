from __future__ import annotations

import unittest

from backend.core.utils import parse_json


class ParseJsonTests(unittest.TestCase):
    def test_extracts_clean_json(self) -> None:
        self.assertEqual(parse_json('{"a": 1}'), {"a": 1})

    def test_extracts_json_with_surrounding_text(self) -> None:
        text = 'Here is the result: {"a": 1, "b": "x"} done.'
        self.assertEqual(parse_json(text), {"a": 1, "b": "x"})

    def test_extracts_last_json_object(self) -> None:
        text = '{"first": 1} ignore {"second": 2}'
        # Greedy span is invalid JSON; fallback extracts the last object
        result = parse_json(text)
        self.assertEqual(result, {"second": 2})

    def test_raises_when_fallback_also_fails(self) -> None:
        text = '{"a": 1} text {bad json}'
        with self.assertRaises(ValueError):
            parse_json(text)

    def test_raises_when_no_json(self) -> None:
        with self.assertRaises(ValueError):
            parse_json("no braces here")
