#!/usr/bin/env python3

from __future__ import annotations

import re
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SKILL = SKILL_ROOT / "SKILL.md"


class SkillContractTest(unittest.TestCase):
    def test_main_skill_stays_compact(self) -> None:
        content = SKILL.read_text(encoding="utf-8")
        self.assertLessEqual(len(content.splitlines()), 45)
        self.assertLessEqual(len(content.split()), 450)

    def test_every_local_reference_exists(self) -> None:
        content = SKILL.read_text(encoding="utf-8")
        references = re.findall(r"\]\((references/[^)]+)\)", content)
        self.assertEqual(len(references), 3)
        for relative in references:
            self.assertTrue((SKILL_ROOT / relative).is_file(), relative)

    def test_lightweight_and_formal_paths_are_distinct(self) -> None:
        content = SKILL.read_text(encoding="utf-8")
        self.assertIn("For a healthy one-agent check", content)
        self.assertIn("Use the runtime ledger", content)
        self.assertIn("Evidence completeness is not product approval", content)

    def test_independent_review_reuses_only_infrastructure(self) -> None:
        content = SKILL.read_text(encoding="utf-8")
        self.assertIn("must perform and record fresh behavioral observations", content)

    def test_formal_scope_uses_unique_criterion_ids(self) -> None:
        content = SKILL.read_text(encoding="utf-8")
        self.assertIn("feature-unique ID", content)
        self.assertIn("successful independent checks", content)
        self.assertIn("move the ledger to `CLEANED`, then emit", content)

    def test_instructions_do_not_invent_ledger_states(self) -> None:
        content = "\n".join(
            path.read_text(encoding="utf-8")
            for path in [SKILL, *(SKILL_ROOT / "references").glob("*.md")]
        )
        for obsolete in ("APP_STABLE", "ENVIRONMENT_FAILURE", "MANUAL_REQUIRED"):
            self.assertNotIn(obsolete, content)


if __name__ == "__main__":
    unittest.main()
