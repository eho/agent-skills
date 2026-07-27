#!/usr/bin/env python3

from __future__ import annotations

import unittest
from pathlib import Path


SKILLS_ROOT = Path(__file__).resolve().parents[2]


def read(relative: str) -> str:
    return (SKILLS_ROOT / relative).read_text(encoding="utf-8")


class EfficiencyContractsTest(unittest.TestCase):
    def test_feature_uses_incremental_rehydration(self) -> None:
        content = read("feature-delivery/SKILL.md")
        self.assertIn("Rehydrate the completed story, its dependents", content)
        self.assertIn("before final audit", content)
        self.assertIn("smallest useful context", content)

    def test_runtime_budget_survives_agent_replacement(self) -> None:
        content = read("feature-delivery/references/contracts.md")
        self.assertIn("A new agent inherits consumed attempts", content)
        self.assertIn("owner-manual", content)
        self.assertIn("not a pass", content)

    def test_exact_head_broad_evidence_can_be_reused(self) -> None:
        implementer = read("user-story-implementer/SKILL.md")
        reviewer = read("user-story-reviewer/SKILL.md")
        self.assertIn("reusable exact-head result", implementer)
        self.assertIn("immutable exact-head broad-gate result", reviewer)

    def test_audit_is_exhaustive_after_a_blocker(self) -> None:
        content = read("post-implementation-reviewer/SKILL.md")
        self.assertIn("Complete every audit category even after discovering a blocker", content)
        self.assertIn("one exhaustive finding set", content)

    def test_simulator_ledger_is_shared(self) -> None:
        feature = read("feature-delivery/SKILL.md")
        content = read("ios-simulator-automation/SKILL.md")
        self.assertIn("use `ios-simulator-automation`", feature)
        self.assertIn("retry budgets survive agents and resumed turns", content)
        self.assertIn("runtime ledger", content)


if __name__ == "__main__":
    unittest.main()
