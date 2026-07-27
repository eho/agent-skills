#!/usr/bin/env python3

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = SKILL_ROOT / "scripts" / "runtime_manifest.py"


class RuntimeLedgerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.ledger = self.root / "runtime.json"
        self.environment = {
            **os.environ,
            "EXPO_PUBLIC_APP_ENV": "development-value",
        }

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def command(
        self, *arguments: str, check: bool = True
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *arguments],
            check=check,
            capture_output=True,
            text=True,
            env=self.environment,
        )

    def create(
        self,
        public_environment_key: str = "EXPO_PUBLIC_APP_ENV",
        check: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        return self.command(
            "create",
            "--output",
            str(self.ledger),
            "--project-root",
            str(self.root),
            "--revision",
            "abc123",
            "--device-udid",
            "SIM-UDID",
            "--runtime",
            "iOS 26.5",
            "--app-id",
            "com.example.app",
            "--artifact-identity",
            "Example.app@abc123",
            "--metro-port",
            "8081",
            "--metro-interface",
            "127.0.0.1",
            "--public-environment-key",
            public_environment_key,
            "--backend-topology",
            "private-lan",
            "--backend-probe-status",
            "reachable",
            "--session",
            "story-001",
            "--state-dir",
            str(self.root / "state"),
            "--criterion",
            "AC01",
            "--criterion",
            "AC02",
            check=check,
        )

    def phase(self, target: str) -> None:
        evidence = self.root / f"{target.lower()}.json"
        evidence.write_text(
            json.dumps({"phase": target, "revision": "abc123"}),
            encoding="utf-8",
        )
        self.command(
            "phase",
            "--ledger",
            str(self.ledger),
            "--to",
            target,
            "--evidence-ref",
            str(evidence),
        )

    def evidence(
        self,
        criterion: str,
        status: str,
        observer: str = "implementer",
    ) -> None:
        evidence = self.root / f"{criterion}-{status}-{observer}.json"
        evidence.write_text(
            json.dumps(
                {
                    "criterion": criterion,
                    "observer": observer,
                    "revision": "abc123",
                    "status": status,
                }
            ),
            encoding="utf-8",
        )
        self.command(
            "evidence",
            "--ledger",
            str(self.ledger),
            "--criterion",
            criterion,
            "--observer-id",
            observer,
            "--status",
            status,
            "--assertion-ref",
            str(evidence),
        )

    def handoff(self) -> dict:
        result = self.command("handoff", "--ledger", str(self.ledger))
        return json.loads(result.stdout)

    def activate(self) -> None:
        self.phase("READY")
        self.phase("ACTIVE")

    def test_phase_help_explains_the_lifecycle(self) -> None:
        result = self.command("phase", "--help")
        self.assertIn("UNREADY -> READY -> ACTIVE", result.stdout)
        self.assertIn("CLEANED -> READY", result.stdout)

    def test_create_declares_criteria_without_persisting_values(self) -> None:
        self.create()
        text = self.ledger.read_text(encoding="utf-8")
        self.assertNotIn("development-value", text)
        payload = json.loads(text)
        self.assertEqual(sorted(payload["criteria"]), ["AC01", "AC02"])
        self.assertEqual(
            payload["bindings"]["public_environment"]["keys"],
            ["EXPO_PUBLIC_APP_ENV"],
        )

    def test_partial_evidence_never_reports_complete(self) -> None:
        self.create()
        self.activate()
        self.evidence("AC01", "observed")
        handoff = self.handoff()
        self.assertEqual(handoff["readiness"], "incomplete")
        self.assertEqual(handoff["criteria"]["pending"], ["AC02"])
        self.assertNotIn("decision", handoff)

    def test_later_observation_resolves_not_observed_status(self) -> None:
        self.create()
        self.activate()
        self.evidence("AC01", "not_observed")
        self.evidence("AC01", "observed", observer="reviewer")
        self.evidence("AC02", "observed", observer="reviewer")
        handoff = self.handoff()
        self.assertEqual(handoff["readiness"], "evidence_complete")
        self.assertEqual(handoff["criteria"]["not_observed"], [])
        self.assertEqual(
            handoff["criterion_details"]["AC01"]["latest_observer"],
            "reviewer",
        )
        payload = json.loads(self.ledger.read_text(encoding="utf-8"))
        self.assertEqual(len(payload["criteria"]["AC01"]["history"]), 2)

    def test_cleaned_ledger_can_resume(self) -> None:
        self.create()
        self.phase("READY")
        self.phase("CLEANED")
        self.phase("READY")
        result = self.command("validate", "--ledger", str(self.ledger))
        self.assertEqual(json.loads(result.stdout)["phase"], "READY")

    def test_rebind_invalidates_all_observations_and_updates_full_identity(self) -> None:
        self.create()
        self.activate()
        self.evidence("AC01", "observed")
        self.evidence("AC02", "observed")
        self.phase("READY")
        rebind_evidence = self.root / "rebind.json"
        rebind_evidence.write_text("{}", encoding="utf-8")
        self.command(
            "rebind",
            "--ledger",
            str(self.ledger),
            "--revision",
            "def456",
            "--artifact-identity",
            "Example.app@def456",
            "--app-id",
            "com.example.changed",
            "--metro-project-root",
            str(self.root / "changed-project"),
            "--metro-port",
            "9090",
            "--metro-interface",
            "localhost",
            "--backend-topology",
            "hosted",
            "--backend-probe-status",
            "reachable",
            "--session",
            "story-002",
            "--state-dir",
            str(self.root / "changed-state"),
            "--evidence-ref",
            str(rebind_evidence),
        )
        handoff = self.handoff()
        self.assertEqual(handoff["readiness"], "incomplete")
        self.assertEqual(handoff["criteria"]["pending"], ["AC01", "AC02"])
        self.assertEqual(handoff["criteria"]["observed"], [])
        self.assertEqual(handoff["bindings"]["app_id"], "com.example.changed")
        self.assertEqual(handoff["bindings"]["metro_port"], 9090)
        self.assertEqual(handoff["bindings"]["backend_topology"], "hosted")
        self.assertEqual(handoff["bindings"]["session"], "story-002")

    def test_successful_reviewer_observation_does_not_consume_retry_budget(self) -> None:
        self.create()
        self.activate()
        self.evidence("AC01", "observed", observer="implementer")
        self.evidence("AC01", "observed", observer="reviewer")
        payload = json.loads(self.ledger.read_text(encoding="utf-8"))
        self.assertEqual(payload["attempts"], [])
        self.assertEqual(
            payload["criteria"]["AC01"]["history"][-1]["observer_id"],
            "reviewer",
        )

    def test_strategy_budget_is_locked_across_concurrent_writers(self) -> None:
        self.create()
        self.activate()
        base = [
            sys.executable,
            str(SCRIPT),
            "attempt",
            "--ledger",
            str(self.ledger),
            "--criterion",
            "AC01",
            "--kind",
            "primary",
            "--classification",
            "tool",
            "--result",
            "failed",
        ]
        first = subprocess.Popen(
            [*base, "--strategy-id", "selector-submit"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=self.environment,
        )
        second = subprocess.Popen(
            [*base, "--strategy-id", "coordinate-submit"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=self.environment,
        )
        first.communicate()
        second.communicate()
        statuses = [first.returncode, second.returncode]
        self.assertEqual(sorted(statuses), [0, 3])
        payload = json.loads(self.ledger.read_text(encoding="utf-8"))
        self.assertEqual(len(payload["attempts"]), 1)

    def test_evidence_requires_active_phase(self) -> None:
        self.create()
        evidence = self.root / "evidence.json"
        evidence.write_text("{}", encoding="utf-8")
        result = self.command(
            "evidence",
            "--ledger",
            str(self.ledger),
            "--criterion",
            "AC01",
            "--observer-id",
            "implementer",
            "--status",
            "observed",
            "--assertion-ref",
            str(evidence),
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("only while runtime is ACTIVE", result.stderr)

    def test_empty_local_assertion_artifact_is_rejected(self) -> None:
        self.create()
        self.activate()
        evidence = self.root / "empty.json"
        evidence.touch()
        result = self.command(
            "evidence",
            "--ledger",
            str(self.ledger),
            "--criterion",
            "AC01",
            "--observer-id",
            "implementer",
            "--status",
            "observed",
            "--assertion-ref",
            str(evidence),
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("non-empty file", result.stderr)

    def test_successful_strategy_is_evidence_not_retry_attempt(self) -> None:
        self.create()
        self.activate()
        result = self.command(
            "attempt",
            "--ledger",
            str(self.ledger),
            "--criterion",
            "AC01",
            "--strategy-id",
            "semantic-check",
            "--kind",
            "primary",
            "--classification",
            "product",
            "--result",
            "succeeded",
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("invalid choice", result.stderr)

    def test_final_handoff_reports_cleanup_and_durable_evidence(self) -> None:
        self.create()
        self.activate()
        self.evidence("AC01", "observed")
        self.evidence("AC02", "observed")
        self.phase("CLEANED")
        handoff = self.handoff()
        self.assertTrue(handoff["cleanup_complete"])
        self.assertEqual(handoff["readiness"], "evidence_complete")

    def test_handoff_rejects_an_assertion_artifact_removed_after_capture(self) -> None:
        self.create()
        self.activate()
        self.evidence("AC01", "observed")
        payload = json.loads(self.ledger.read_text(encoding="utf-8"))
        Path(payload["criteria"]["AC01"]["evidence_refs"][0]).unlink()
        result = self.command(
            "handoff",
            "--ledger",
            str(self.ledger),
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("does not exist", result.stderr)

    def test_sensitive_evidence_reference_is_rejected(self) -> None:
        self.create()
        self.activate()
        result = self.command(
            "evidence",
            "--ledger",
            str(self.ledger),
            "--criterion",
            "AC01",
            "--observer-id",
            "implementer",
            "--status",
            "observed",
            "--assertion-ref",
            "https://example.test/evidence?token=secret",
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("sensitive data", result.stderr)

    def test_missing_local_assertion_reference_is_rejected(self) -> None:
        self.create()
        self.activate()
        result = self.command(
            "evidence",
            "--ledger",
            str(self.ledger),
            "--criterion",
            "AC01",
            "--observer-id",
            "implementer",
            "--status",
            "observed",
            "--assertion-ref",
            str(self.root / "missing.json"),
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("does not exist", result.stderr)

    def test_non_public_environment_key_is_rejected(self) -> None:
        result = self.create(public_environment_key="API_KEY", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not explicitly public", result.stderr)

    def test_publicly_named_secret_environment_key_is_rejected(self) -> None:
        result = self.create(
            public_environment_key="EXPO_PUBLIC_AUTH_TOKEN",
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("appears sensitive", result.stderr)

    def test_malformed_ledger_fails_validation(self) -> None:
        self.create()
        payload = json.loads(self.ledger.read_text(encoding="utf-8"))
        payload["attempts"].append({"criterion": "MISSING"})
        self.ledger.write_text(json.dumps(payload), encoding="utf-8")
        result = self.command(
            "validate", "--ledger", str(self.ledger), check=False
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("undeclared criterion", result.stderr)

    def test_current_status_must_match_immutable_history(self) -> None:
        self.create()
        self.activate()
        self.evidence("AC01", "not_observed")
        payload = json.loads(self.ledger.read_text(encoding="utf-8"))
        payload["criteria"]["AC01"]["status"] = "observed"
        self.ledger.write_text(json.dumps(payload), encoding="utf-8")
        result = self.command(
            "validate", "--ledger", str(self.ledger), check=False
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("does not match its history", result.stderr)


if __name__ == "__main__":
    unittest.main()
