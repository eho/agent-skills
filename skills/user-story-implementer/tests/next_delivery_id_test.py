#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "next_delivery_id.py"
SPEC = importlib.util.spec_from_file_location("next_delivery_id", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class NextDeliveryIdTest(unittest.TestCase):
    def test_increments_only_matching_composite_identity(self) -> None:
        first = MODULE.next_id("docs/design/demo.md", "DEMO-001", [])
        second = MODULE.next_id("docs/design/demo.md", "DEMO-001", [first])
        unrelated = MODULE.next_id("docs/other/demo.md", "DEMO-001", [first, second])
        self.assertTrue(first.endswith("-a1"))
        self.assertTrue(second.endswith("-a2"))
        self.assertTrue(unrelated.endswith("-a1"))
        self.assertNotEqual(first.rsplit("-a", 1)[0], unrelated.rsplit("-a", 1)[0])

    def test_rejects_unsafe_identity(self) -> None:
        with self.assertRaises(ValueError):
            MODULE.next_id("../demo.md", "DEMO-001", [])

    def test_accepts_canonical_audit_gap_id(self) -> None:
        value = MODULE.next_id("docs/design/demo.md", "GAP-12AB34CD56EF", [])
        self.assertTrue(value.endswith("-gap-12ab34cd56ef-a1"))


if __name__ == "__main__":
    unittest.main()
