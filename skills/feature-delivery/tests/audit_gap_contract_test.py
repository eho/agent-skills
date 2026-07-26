#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "audit_gap_contract.py"
SPEC = importlib.util.spec_from_file_location("audit_gap_contract", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def payload() -> dict[str, object]:
    return {
        "stable_key": "integration:event-forwarding",
        "design_identity": "docs/design/demo.md",
        "design_revision": "a" * 64,
        "category": "integration-gap",
        "affected_stories": ["DEMO-001", "DEMO-002"],
        "evidence": ["The combined path drops an event."],
        "required_remediation": "Preserve the event across the boundary.",
        "acceptance_criteria": ["The event reaches the consumer exactly once."],
        "verification": ["Run the integration test."],
        "dependencies": ["DEMO-001", "DEMO-002"],
    }


class AuditGapContractTest(unittest.TestCase):
    def test_is_deterministic_and_changes_with_contract(self) -> None:
        original = MODULE.build_contract(payload())
        reordered = MODULE.build_contract(dict(reversed(list(payload().items()))))
        changed_payload = payload()
        changed_payload["required_remediation"] = "Reject the event explicitly."
        changed = MODULE.build_contract(changed_payload)
        self.assertEqual(original, reordered)
        self.assertRegex(original["gap_id"], r"^GAP-[0-9A-F]{12}$")
        self.assertEqual(original["gap_id"], changed["gap_id"])
        self.assertNotEqual(original["gap_revision"], changed["gap_revision"])

    def test_rejects_non_binary_empty_criteria(self) -> None:
        value = payload()
        value["acceptance_criteria"] = []
        with self.assertRaises(ValueError):
            MODULE.build_contract(value)


if __name__ == "__main__":
    unittest.main()
