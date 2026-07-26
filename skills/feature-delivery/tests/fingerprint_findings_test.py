#!/usr/bin/env python3

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
import json
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "fingerprint_findings.py"


class FingerprintFindingsTest(unittest.TestCase):
    def fingerprint(self, content: object) -> list[dict[str, str]]:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "findings.json"
            path.write_text(json.dumps(content), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(path)],
                check=True,
                capture_output=True,
                text=True,
            )
        return json.loads(result.stdout)

    def finding(self, stable_key: str, behavior: str = "Incorrect behavior") -> dict[str, str]:
        return {
            "stable_key": stable_key,
            "severity": "High",
            "location": "app.ts:2",
            "behavior": behavior,
            "impact": "Breaks the contract",
            "required_change": "Correct it",
        }

    def test_fingerprints_findings_individually(self) -> None:
        first = self.fingerprint([self.finding("app:validator")])
        expanded = self.fingerprint(
            [self.finding("app:validator", "Reworded behavior"), self.finding("api:auth")]
        )
        self.assertEqual(first[0]["id"], next(
            item["id"] for item in expanded if item["stable_key"] == "app:validator"
        ))

    def test_rejects_duplicate_stable_keys(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "findings.json"
            path.write_text(
                json.dumps([self.finding("same"), self.finding("same")]),
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(path)],
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("duplicate stable_key", result.stderr)


if __name__ == "__main__":
    unittest.main()
