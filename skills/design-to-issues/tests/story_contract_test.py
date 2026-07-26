#!/usr/bin/env python3

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "story_contract.py"


def manifest(root: Path, content: str) -> dict[str, object]:
    design = root / "docs" / "design" / "sample.md"
    design.parent.mkdir(parents=True, exist_ok=True)
    design.write_bytes(content.encode("utf-8"))
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(design), "--repo-root", str(root)],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def rejected(root: Path, content: str) -> subprocess.CompletedProcess[str]:
    design = root / "docs" / "design" / "invalid.md"
    design.parent.mkdir(parents=True, exist_ok=True)
    design.write_text(content, encoding="utf-8")
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(design), "--repo-root", str(root)],
        check=False,
        capture_output=True,
        text=True,
    )


BASE = """**Status:** Revised

## Architecture Overview

Use contract A.

## User Stories

### DEMO-001: Foundation
**Context:**
- Depends on: None

**Acceptance Criteria:**
- [ ] Foundation works.

### DEMO-002: Consumer
**Context:**
- Depends on: DEMO-001

**Acceptance Criteria:**
- [ ] Consumer works.

## Future Extensions

None.
"""


class StoryContractTest(unittest.TestCase):
    def test_extracts_composite_identity_and_dependencies(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = manifest(Path(directory), BASE)
        self.assertEqual(result["design_identity"], "docs/design/sample.md")
        self.assertEqual([story["id"] for story in result["stories"]], ["DEMO-001", "DEMO-002"])
        self.assertEqual(result["stories"][1]["dependencies"], ["DEMO-001"])

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

    def test_rejects_unknown_or_forward_dependencies(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            unknown = rejected(root, BASE.replace("Depends on: DEMO-001", "Depends on: DEMO-999"))
            forward = rejected(root, BASE.replace("Depends on: None", "Depends on: DEMO-002", 1))
        self.assertNotEqual(unknown.returncode, 0)
        self.assertIn("unknown story", unknown.stderr)
        self.assertNotEqual(forward.returncode, 0)
        self.assertIn("must appear earlier", forward.stderr)

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


if __name__ == "__main__":
    unittest.main()
