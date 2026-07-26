#!/usr/bin/env python3

from __future__ import annotations

import re
import unittest
from pathlib import Path


SKILLS_ROOT = Path(__file__).resolve().parents[2]
CONTRACTS = SKILLS_ROOT / "feature-delivery" / "references" / "contracts.md"


def template(path: Path, handoff: str) -> str:
    content = path.read_text(encoding="utf-8")
    pattern = rf"```markdown\n## {re.escape(handoff)}\n(.*?)```"
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        raise AssertionError(f"{handoff} template missing from {path}")
    return match.group(1).strip()


class HandoffContractsTest(unittest.TestCase):
    def assert_contract(self, handoff: str, specialist: str) -> None:
        self.assertEqual(
            template(CONTRACTS, handoff),
            template(SKILLS_ROOT / specialist / "SKILL.md", handoff),
        )

    def test_issue_sync(self) -> None:
        self.assert_contract("Issue Sync Handoff", "design-to-issues")

    def test_implementation(self) -> None:
        self.assert_contract("Implementation Handoff", "user-story-implementer")
        self.assert_contract("Implementation Handoff", "user-story-delivery")

    def test_review(self) -> None:
        self.assert_contract("Review Handoff", "user-story-reviewer")
        self.assert_contract("Review Handoff", "user-story-delivery")

    def test_carry_forward_review(self) -> None:
        self.assert_contract("Carry-Forward Review Handoff", "user-story-reviewer")

    def test_final_audit(self) -> None:
        self.assert_contract("Final Audit Handoff", "post-implementation-reviewer")


if __name__ == "__main__":
    unittest.main()
