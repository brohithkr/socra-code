# tests/test_student_model.py
from __future__ import annotations

import unittest

from backend.core.student_model import StudentModel, StudentModelStore


class StudentModelStoreTests(unittest.IsolatedAsyncioTestCase):
    async def test_snapshot_returns_empty_for_new_session(self) -> None:
        store = StudentModelStore()
        snap = await store.snapshot("s1")
        self.assertEqual(snap, {})

    async def test_note_hint_decreases_mastery(self) -> None:
        store = StudentModelStore()
        # Build up mastery first; mastery is clamped to [0.0, 1.0],
        # so we need a positive baseline to observe a decrease.
        await store.note_progress("s1", "loop_boundary")
        await store.note_progress("s1", "loop_boundary")
        await store.note_hint("s1", "loop_boundary")
        snap = await store.snapshot("s1")
        # 0.08 + 0.08 - 0.05 = 0.11
        self.assertAlmostEqual(snap["loop_boundary"], 0.11)

    async def test_note_progress_increases_mastery(self) -> None:
        store = StudentModelStore()
        await store.note_progress("s1", "loop_boundary")
        snap = await store.snapshot("s1")
        self.assertAlmostEqual(snap["loop_boundary"], 0.08)

    async def test_mastery_clamped_to_unit_interval(self) -> None:
        store = StudentModelStore()
        for _ in range(50):
            await store.note_progress("s1", "x")
        for _ in range(50):
            await store.note_hint("s1", "x")
        snap = await store.snapshot("s1")
        self.assertGreaterEqual(snap["x"], 0.0)
        self.assertLessEqual(snap["x"], 1.0)

    async def test_sessions_are_isolated(self) -> None:
        store = StudentModelStore()
        await store.note_progress("s1", "x")
        snap2 = await store.snapshot("s2")
        self.assertEqual(snap2, {})

    async def test_get_or_create_returns_same_instance(self) -> None:
        store = StudentModelStore()
        m1 = await store.get_or_create("s1")
        m2 = await store.get_or_create("s1")
        self.assertIs(m1, m2)
        self.assertIsInstance(m1, StudentModel)

    async def test_student_model_has_socratic_fields(self) -> None:
        store = StudentModelStore()
        m = await store.get_or_create("s1")
        self.assertEqual(m.mastery, {})
        self.assertIsNone(m.problem_id)
        self.assertIsNone(m.graph)
        self.assertIsNone(m.current_node_id)
        self.assertEqual(m.resolved_node_ids, set())
        self.assertEqual(m.hint_level, 0)
        self.assertIsNone(m.last_question)
