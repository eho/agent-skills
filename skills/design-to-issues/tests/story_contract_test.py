#!/usr/bin/env python3

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "story_contract.py"


def manifest(root: Path, content: str, mode: str = "delivery") -> dict[str, object]:
    design = root / "docs" / "design" / "sample.md"
    design.parent.mkdir(parents=True, exist_ok=True)
    design.write_bytes(content.encode("utf-8"))
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            str(design),
            "--repo-root",
            str(root),
            "--mode",
            mode,
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def rejected(
    root: Path, content: str, mode: str = "delivery"
) -> subprocess.CompletedProcess[str]:
    design = root / "docs" / "design" / "invalid.md"
    design.parent.mkdir(parents=True, exist_ok=True)
    design.write_text(content, encoding="utf-8")
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            str(design),
            "--repo-root",
            str(root),
            "--mode",
            mode,
        ],
        check=False,
        capture_output=True,
        text=True,
    )


BASE = """**Status:** Revised

## Architecture Overview

Use contract A.

## User Stories

### DEMO-001: Foundation
**Outcome:** A durable foundation is available.

**Context:**
- Depends on: None
- Out of scope: Consumer behavior.

**Acceptance Criteria:**
- [ ] Foundation works.

**Verification:**
- Run the foundation unit tests.

### DEMO-002: Consumer
**Outcome:** A consumer can use the foundation.

**Context:**
- Depends on: DEMO-001
- Out of scope: Replacing the foundation.

**Acceptance Criteria:**
- [ ] Consumer works.

**Verification:**
- Run the consumer integration tests.

## Future Extensions

None.
"""


class StoryContractTest(unittest.TestCase):
    def test_extracts_composite_identity_and_dependencies(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = manifest(Path(directory), BASE)
        self.assertEqual(result["design_identity"], "docs/design/sample.md")
        self.assertEqual(result["status"], "Revised")
        self.assertEqual([story["id"] for story in result["stories"]], ["DEMO-001", "DEMO-002"])
        self.assertEqual(result["stories"][1]["dependencies"], ["DEMO-001"])

    def test_author_accepts_draft_but_delivery_rejects_it(self) -> None:
        draft = BASE.replace("**Status:** Revised", "**Status:** Draft")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            authored = manifest(root, draft, mode="author")
            delivered = rejected(root, draft, mode="delivery")
        self.assertEqual(authored["status"], "Draft")
        self.assertNotEqual(delivered.returncode, 0)
        self.assertIn("delivery mode requires Status: Revised", delivered.stderr)

    def test_rejects_missing_duplicate_and_unsupported_statuses(self) -> None:
        cases = {
            "missing": (
                BASE.replace("**Status:** Revised\n\n", "", 1),
                "exactly one Status",
            ),
            "duplicate": (
                BASE.replace(
                    "**Status:** Revised",
                    "**Status:** Revised\n**Status:** Draft",
                    1,
                ),
                "exactly one Status",
            ),
            "active": (
                BASE.replace("**Status:** Revised", "**Status:** Active", 1),
                "unsupported actionable design status: Active",
            ),
            "implemented": (
                BASE.replace("**Status:** Revised", "**Status:** Implemented", 1),
                "unsupported actionable design status: Implemented",
            ),
        }
        for name, (content, message) in cases.items():
            with self.subTest(case=name), tempfile.TemporaryDirectory() as directory:
                result = rejected(Path(directory), content, mode="author")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(message, result.stderr)

    def test_shared_design_change_changes_document_not_story_revision(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            original = manifest(root, BASE)
            changed = manifest(root, BASE.replace("contract A", "contract B"))
        self.assertNotEqual(original["design_revision"], changed["design_revision"])
        self.assertEqual(
            [story["story_revision"] for story in original["stories"]],
            [story["story_revision"] for story in changed["stories"]],
        )

    def test_story_change_changes_both_revisions(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            original = manifest(root, BASE)
            changed = manifest(root, BASE.replace("Foundation works.", "Foundation is durable."))
        self.assertNotEqual(original["design_revision"], changed["design_revision"])
        self.assertNotEqual(
            original["stories"][0]["story_revision"],
            changed["stories"][0]["story_revision"],
        )

    def test_normalization_ignores_crlf_and_trailing_horizontal_space(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            unix = manifest(root, BASE)
            windows = manifest(root, BASE.replace("\n", "  \r\n"))
        self.assertEqual(unix["design_revision"], windows["design_revision"])
        self.assertEqual(
            [story["story_revision"] for story in unix["stories"]],
            [story["story_revision"] for story in windows["stories"]],
        )

    def test_rejects_malformed_story_heading(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = rejected(Path(directory), BASE.replace("### DEMO-002:", "### Consumer:"))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("exactly one stable story ID", result.stderr)

    def test_rejects_missing_dependency_declaration(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = rejected(Path(directory), BASE.replace("- Depends on: None\n", "", 1))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("exactly one 'Depends on:'", result.stderr)

    def test_rejects_unknown_and_accepts_forward_dependencies(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            unknown = rejected(root, BASE.replace("Depends on: DEMO-001", "Depends on: DEMO-999"))
            forward = manifest(
                root,
                BASE.replace("Depends on: None", "Depends on: DEMO-002", 1).replace(
                    "Depends on: DEMO-001", "Depends on: None"
                ),
            )
        self.assertNotEqual(unknown.returncode, 0)
        self.assertIn("unknown story", unknown.stderr)
        self.assertEqual(forward["stories"][0]["dependencies"], ["DEMO-002"])

    def test_rejects_dependency_cycles(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = rejected(
                Path(directory),
                BASE.replace("Depends on: None", "Depends on: DEMO-002", 1),
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("cyclic story dependencies", result.stderr)

    def test_rejects_self_dependency(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = rejected(
                Path(directory),
                BASE.replace("Depends on: DEMO-001", "Depends on: DEMO-002"),
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("cannot depend on itself", result.stderr)

    def test_ignores_headings_and_dependencies_in_fenced_examples(self) -> None:
        example = BASE.replace(
            "Use contract A.",
            """Use contract A.

```markdown
## User Stories
### FAKE-999: Example
- Depends on: FAKE-998
```""",
        ).replace(
            "**Acceptance Criteria:**\n- [ ] Foundation works.",
            """```shell
# Depends on: FAKE-999
```

**Acceptance Criteria:**
- [ ] Foundation works.""",
        )
        with tempfile.TemporaryDirectory() as directory:
            result = manifest(Path(directory), example)
        self.assertEqual([story["id"] for story in result["stories"]], ["DEMO-001", "DEMO-002"])
        self.assertEqual(result["stories"][0]["dependencies"], [])

    def test_rejects_partially_valid_dependency_value(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = rejected(
                Path(directory),
                BASE.replace("Depends on: DEMO-001", "Depends on: DEMO-001 plus malformed-token"),
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("malformed dependency metadata", result.stderr)

    def test_rejects_natural_language_dependency_list(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = rejected(
                Path(directory),
                BASE.replace(
                    "Depends on: DEMO-001",
                    "Depends on: DEMO-001 and DEMO-002",
                ),
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("malformed dependency metadata", result.stderr)

    def test_rejects_n_a_dependency_sentinel(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = rejected(
                Path(directory),
                BASE.replace("Depends on: None", "Depends on: N/A", 1),
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("malformed dependency metadata", result.stderr)

    def test_rejects_missing_required_story_contract_fields(self) -> None:
        cases = {
            "Outcome": BASE.replace(
                "**Outcome:** A durable foundation is available.\n\n", "", 1
            ),
            "Out of scope": BASE.replace(
                "- Out of scope: Consumer behavior.\n", "", 1
            ),
            "Acceptance Criteria": BASE.replace(
                "**Acceptance Criteria:**\n- [ ] Foundation works.\n\n", "", 1
            ),
            "Verification": BASE.replace(
                "**Verification:**\n- Run the foundation unit tests.\n\n", "", 1
            ),
        }
        for expected, content in cases.items():
            with self.subTest(field=expected), tempfile.TemporaryDirectory() as directory:
                result = rejected(Path(directory), content)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(expected, result.stderr)

    def test_rejects_reserved_management_marker_before_rendering(self) -> None:
        marked = BASE.replace(
            "- [ ] Consumer works.",
            "- [ ] Consumer works.\n<!-- feature-delivery:story=EVIL-001 -->",
        )
        with tempfile.TemporaryDirectory() as directory:
            result = rejected(Path(directory), marked)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("reserved feature-delivery marker", result.stderr)

    def test_required_sections_do_not_consume_later_unrelated_items(self) -> None:
        empty_acceptance = BASE.replace(
            "**Acceptance Criteria:**\n- [ ] Foundation works.",
            """**Acceptance Criteria:**

- **Later Checklist:**
  - [ ] This is not an acceptance criterion.""",
            1,
        )
        empty_verification = BASE.replace(
            "**Verification:**\n- Run the foundation unit tests.",
            """**Verification:**

- **Later Checks:**
  - Run a command outside the verification section.""",
            1,
        )
        cases = {
            "acceptance": (
                empty_acceptance,
                "at least one acceptance-criteria checkbox",
            ),
            "verification": (
                empty_verification,
                "at least one verification instruction",
            ),
        }
        for name, (content, message) in cases.items():
            with self.subTest(section=name), tempfile.TemporaryDirectory() as directory:
                result = rejected(Path(directory), content)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(message, result.stderr)

    def test_rejects_duplicate_required_story_fields_and_sections(self) -> None:
        cases = {
            "Outcome": BASE.replace(
                "**Outcome:** A durable foundation is available.",
                """**Outcome:** A durable foundation is available.
**Outcome:** A duplicate outcome.""",
                1,
            ),
            "Out of scope": BASE.replace(
                "- Out of scope: Consumer behavior.",
                """- Out of scope: Consumer behavior.
- Out of scope: Duplicate boundary.""",
                1,
            ),
            "Acceptance Criteria": BASE.replace(
                "**Verification:**",
                """**Acceptance Criteria:**
- [ ] Duplicate criteria.

**Verification:**""",
                1,
            ),
            "Verification": BASE.replace(
                "- Run the foundation unit tests.",
                """- Run the foundation unit tests.

**Verification:**
- Run duplicate verification.""",
                1,
            ),
        }
        for expected, content in cases.items():
            with self.subTest(field=expected), tempfile.TemporaryDirectory() as directory:
                result = rejected(Path(directory), content)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(f"exactly one", result.stderr)
            self.assertIn(expected, result.stderr)

    def test_rejects_required_story_field_ordering(self) -> None:
        outcome_after_criteria = BASE.replace(
            "**Outcome:** A durable foundation is available.\n\n",
            "",
            1,
        ).replace(
            "**Verification:**",
            """**Outcome:** A durable foundation is available.

**Verification:**""",
            1,
        )
        scope_after_criteria = BASE.replace(
            "- Out of scope: Consumer behavior.\n",
            "",
            1,
        ).replace(
            "**Verification:**",
            """- Out of scope: Consumer behavior.

**Verification:**""",
            1,
        )
        verification_before_criteria = BASE.replace(
            """**Acceptance Criteria:**
- [ ] Foundation works.

**Verification:**
- Run the foundation unit tests.""",
            """**Verification:**
- Run the foundation unit tests.

**Acceptance Criteria:**
- [ ] Foundation works.""",
            1,
        )
        cases = {
            "Outcome": (
                outcome_after_criteria,
                "'Outcome:' before 'Acceptance Criteria:'",
            ),
            "Out of scope": (
                scope_after_criteria,
                "'Out of scope:' before 'Acceptance Criteria:'",
            ),
            "Acceptance before Verification": (
                verification_before_criteria,
                "'Acceptance Criteria:' before 'Verification:'",
            ),
        }
        for name, (content, message) in cases.items():
            with self.subTest(order=name), tempfile.TemporaryDirectory() as directory:
                result = rejected(Path(directory), content)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(message, result.stderr)

    def test_accepts_bold_story_metadata_and_comma_dependencies(self) -> None:
        extended = BASE.replace(
            "- Depends on: None",
            "- **Depends on:** None",
            1,
        ).replace(
            "- Depends on: DEMO-001",
            "- **Depends on:** DEMO-001, DEMO-003",
        ).replace(
            "- Out of scope: Consumer behavior.",
            "- **Out of scope:** Consumer behavior.",
        ).replace(
            "### DEMO-002: Consumer",
            """### DEMO-003: Adapter
**Outcome:** An adapter exposes the foundation.

**Context:**
- **Depends on:** DEMO-001
- **Out of scope:** Consumer behavior.

**Acceptance Criteria:**
- [ ] The adapter exposes the foundation.

**Verification:**
- Run the adapter tests.

### DEMO-002: Consumer""",
        )
        with tempfile.TemporaryDirectory() as directory:
            result = manifest(Path(directory), extended)
        self.assertEqual(
            [story["id"] for story in result["stories"]],
            ["DEMO-001", "DEMO-003", "DEMO-002"],
        )
        self.assertEqual(
            result["stories"][2]["dependencies"],
            ["DEMO-001", "DEMO-003"],
        )


if __name__ == "__main__":
    unittest.main()
