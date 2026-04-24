from __future__ import annotations

import importlib
import unittest


class DependencyWiringTests(unittest.TestCase):
    def test_backend_deps_builds_pipeline_without_rag(self) -> None:
        deps = importlib.import_module("backend.deps")

        pipeline = deps.get_pipeline()

        self.assertIsNotNone(pipeline)
        self.assertFalse(hasattr(pipeline, "rag"))
        self.assertFalse(hasattr(pipeline, "rag_top_k"))

