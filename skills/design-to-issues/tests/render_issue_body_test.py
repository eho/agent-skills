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
**Context:**
- Depends on: None

**Acceptance Criteria:**
- [ ] Foundation works.

### DEMO-002: Consumer
**Context:**
- Depends on: DEMO-001

**Acceptance Criteria:**
- [ ] Consumer works.
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

    def test_rejects_reserved_markers_in_story_source(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            design = root / "docs" / "design" / "demo.md"
            manifest = root / "manifest.json"
            issue_map = root / "issues.json"
            output = root / "body.md"
            design.parent.mkdir(parents=True)
            design.write_text(
                DESIGN.replace(
                    "- [ ] Consumer works.",
                    "- [ ] Consumer works.\n<!-- feature-delivery:story=EVIL-001 -->",
                ),
                encoding="utf-8",
            )
            issue_map.write_text(json.dumps({"DEMO-001": 11, "DEMO-002": 12}), encoding="utf-8")
            with manifest.open("w", encoding="utf-8") as stream:
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
                    stdout=stream,
                    text=True,
                )
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
