#!/usr/bin/env python3

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
CONTRACT = SCRIPTS / "story_contract.py"
RENDER = SCRIPTS / "render_issue_body.py"

DESIGN = """**Status:** Revised

## Architecture

Shared contract.

## User Stories

### DEMO-001: Foundation
**Outcome:** A durable foundation is available.

**Context:**
- Depends on: None
- Out of scope: Consumer behavior.

**Acceptance Criteria:**
- [ ] Foundation works.

**Verification:**
- Run the foundation tests.

### DEMO-002: Consumer
**Outcome:** A consumer can use the foundation.

**Context:**
- Depends on: DEMO-001
- Out of scope: Foundation changes.

**Acceptance Criteria:**
- [ ] Consumer works.

**Verification:**
- Run the consumer tests.
"""


class RenderIssueBodyTest(unittest.TestCase):
    def test_render_is_repeatable_and_uses_exact_source(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            design = root / "docs" / "design" / "demo.md"
            manifest = root / "manifest.json"
            issue_map = root / "issues.json"
            first = root / "first.md"
            second = root / "second.md"
            design.parent.mkdir(parents=True)
            design.write_text(DESIGN, encoding="utf-8")
            issue_map.write_text(json.dumps({"DEMO-001": 11, "DEMO-002": 12}), encoding="utf-8")
            with manifest.open("w", encoding="utf-8") as output:
                subprocess.run(
                    [
                        sys.executable,
                        str(CONTRACT),
                        str(design),
                        "--repo-root",
                        str(root),
                        "--include-source",
                    ],
                    check=True,
                    stdout=output,
                    text=True,
                )

            command = [
                sys.executable,
                str(RENDER),
                "--manifest",
                str(manifest),
                "--story-id",
                "DEMO-002",
                "--issue-map",
                str(issue_map),
                "--design-url",
                "https://github.example/blob/main/docs/design/demo.md",
            ]
            subprocess.run(command + ["--output", str(first)], check=True)
            subprocess.run(command + ["--output", str(second)], check=True)

            self.assertEqual(first.read_bytes(), second.read_bytes())
            body = first.read_text(encoding="utf-8")
            self.assertIn("### DEMO-002: Consumer", body)
            self.assertIn("- Depends on: #11 (`DEMO-001`)", body)
            self.assertNotIn("### DEMO-001: Foundation", body)
            self.assertEqual(body.count("feature-delivery:story=DEMO-002"), 1)

    def test_renderer_keeps_defense_against_unvalidated_reserved_marker(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = root / "manifest.json"
            issue_map = root / "issues.json"
            output = root / "body.md"
            source = DESIGN[DESIGN.index("### DEMO-002") :]
            source = source.replace(
                "- [ ] Consumer works.",
                "- [ ] Consumer works.\n<!-- feature-delivery:story=EVIL-001 -->",
            )
            manifest.write_text(
                json.dumps(
                    {
                        "design_identity": "docs/design/demo.md",
                        "stories": [
                            {
                                "id": "DEMO-002",
                                "dependencies": ["DEMO-001"],
                                "source": source,
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            issue_map.write_text(json.dumps({"DEMO-001": 11, "DEMO-002": 12}), encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(RENDER),
                    "--manifest",
                    str(manifest),
                    "--story-id",
                    "DEMO-002",
                    "--issue-map",
                    str(issue_map),
                    "--design-url",
                    "https://github.example/design",
                    "--output",
                    str(output),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("reserved feature-delivery marker", result.stderr)


if __name__ == "__main__":
    unittest.main()
