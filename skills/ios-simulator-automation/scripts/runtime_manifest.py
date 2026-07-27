#!/usr/bin/env python3

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import re
import sys
import tempfile
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterator
from urllib.parse import urlsplit


SCHEMA_VERSION = 3
PHASES = {"UNREADY", "READY", "ACTIVE", "CLEANED"}
TRANSITIONS = {
    "UNREADY": {"READY"},
    "READY": {"ACTIVE", "CLEANED"},
    "ACTIVE": {"READY", "CLEANED"},
    "CLEANED": {"READY"},
}
STATUSES = {"pending", "observed", "not_observed"}
ATTEMPT_KINDS = {"primary", "fallback", "repair"}
CLASSIFICATIONS = {"product", "tool", "environment", "unobservable"}
RESULTS = {"failed", "inconclusive"}
BACKEND_TOPOLOGIES = {
    "simulator-local",
    "mac-loopback",
    "private-lan",
    "hosted",
    "proxy",
    "none",
}
BACKEND_PROBE_STATUSES = {
    "unverified",
    "reachable",
    "unreachable",
    "not-applicable",
}
IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
ENVIRONMENT_KEY = re.compile(r"^[A-Z][A-Z0-9_]*$")
SENSITIVE_REFERENCE = re.compile(
    r"(?i)(authorization|credential|otp|password|private[_-]?key|secret|token)="
)
SENSITIVE_ENVIRONMENT_KEY = re.compile(
    r"(^|_)(AUTHORIZATION|CREDENTIAL|OTP|PASSWORD|PRIVATE_KEY|SECRET|TOKEN)($|_)"
)


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def fail(message: str, code: int = 2) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(code)


def validate_identifier(value: str, label: str) -> str:
    if not IDENTIFIER.fullmatch(value):
        fail(f"invalid {label}: {value}")
    return value


def validate_reference(
    value: str,
    require_local_exists: bool = False,
    require_local_artifact: bool = False,
) -> str:
    if not value or "\n" in value or "\r" in value:
        fail("evidence reference must be a non-empty single line")
    if SENSITIVE_REFERENCE.search(value):
        fail("evidence reference appears to contain sensitive data")
    parsed = urlsplit(value)
    if parsed.scheme in {"http", "https"} and (parsed.query or parsed.fragment):
        fail("web evidence references must not contain query strings or fragments")
    if not parsed.scheme and (require_local_exists or require_local_artifact):
        path = Path(value)
        if not path.exists():
            fail(f"local evidence reference does not exist: {value}")
        if require_local_artifact and (
            not path.is_file() or path.stat().st_size == 0
        ):
            fail(f"local assertion artifact must be a non-empty file: {value}")
    return value


def public_environment_fingerprint(keys: list[str]) -> dict[str, Any]:
    unique = sorted(set(keys))
    for key in unique:
        if not ENVIRONMENT_KEY.fullmatch(key) or "PUBLIC" not in key.split("_"):
            fail(f"environment key is not explicitly public: {key}")
        if SENSITIVE_ENVIRONMENT_KEY.search(key):
            fail(f"environment key appears sensitive despite being public: {key}")
    material = "\n".join(
        f"{key}={os.environ.get(key, '<missing>')}" for key in unique
    ).encode("utf-8")
    return {
        "keys": unique,
        "sha256": hashlib.sha256(material).hexdigest(),
    }


def validate_criterion(value: Any, criterion_id: str) -> None:
    if not isinstance(value, dict):
        fail(f"criterion {criterion_id} must be an object")
    if value.get("status") not in STATUSES:
        fail(f"criterion {criterion_id} has invalid status")
    if not isinstance(value.get("history"), list):
        fail(f"criterion {criterion_id} history must be a list")
    if not isinstance(value.get("evidence_refs"), list):
        fail(f"criterion {criterion_id} evidence_refs must be a list")
    for reference in value["evidence_refs"]:
        if not isinstance(reference, str):
            fail(f"criterion {criterion_id} has invalid evidence reference")
        validate_reference(reference)
    for event in value["history"]:
        if not isinstance(event, dict) or event.get("status") not in STATUSES:
            fail(f"criterion {criterion_id} has invalid history event")
        references = event.get("evidence_refs")
        if not isinstance(references, list):
            fail(f"criterion {criterion_id} history evidence must be a list")
        for reference in references:
            if not isinstance(reference, str):
                fail(f"criterion {criterion_id} has invalid history reference")
            validate_reference(reference)
        change_reference = event.get("change_ref")
        if change_reference is not None:
            if not isinstance(change_reference, str):
                fail(f"criterion {criterion_id} has invalid change reference")
            validate_reference(change_reference)
        observer = event.get("observer_id")
        if event["status"] in {"observed", "not_observed"}:
            if not isinstance(observer, str):
                fail(f"criterion {criterion_id} history is missing an observer")
            validate_identifier(observer, "observer")
    if value["history"]:
        latest = value["history"][-1]
        if latest["status"] != value["status"]:
            fail(f"criterion {criterion_id} status does not match its history")
        if latest["evidence_refs"] != value["evidence_refs"]:
            fail(f"criterion {criterion_id} evidence does not match its history")
    elif value["status"] != "pending" or value["evidence_refs"]:
        fail(f"criterion {criterion_id} has current evidence without history")


def validate_manifest(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        fail("runtime ledger must be a JSON object")
    if payload.get("schema_version") != SCHEMA_VERSION:
        fail("unsupported runtime ledger schema")
    if payload.get("phase") not in PHASES:
        fail("invalid runtime phase")
    for key in ("bindings", "criteria", "attempts", "phase_history", "rebindings"):
        if key not in payload:
            fail(f"runtime ledger missing field: {key}")
    if not isinstance(payload["bindings"], dict):
        fail("runtime bindings must be an object")
    for key in (
        "project_root",
        "revision",
        "device_udid",
        "runtime",
        "app_id",
        "session",
        "state_dir",
    ):
        if not isinstance(payload["bindings"].get(key), str) or not payload["bindings"][key]:
            fail(f"runtime binding missing non-empty field: {key}")
    for key in ("artifact_identity", "metro_interface"):
        value = payload["bindings"].get(key)
        if value is not None and not isinstance(value, str):
            fail(f"runtime binding has invalid field: {key}")
    if not isinstance(payload["bindings"].get("metro_project_root"), str):
        fail("runtime binding has invalid field: metro_project_root")
    metro_port = payload["bindings"].get("metro_port")
    if metro_port is not None and (
        not isinstance(metro_port, int) or isinstance(metro_port, bool)
    ):
        fail("runtime binding has invalid field: metro_port")
    if payload["bindings"].get("backend_topology") not in BACKEND_TOPOLOGIES:
        fail("runtime binding has invalid backend topology")
    if (
        payload["bindings"].get("backend_probe_status")
        not in BACKEND_PROBE_STATUSES
    ):
        fail("runtime binding has invalid backend probe status")
    public_environment = payload["bindings"].get("public_environment")
    if (
        not isinstance(public_environment, dict)
        or not isinstance(public_environment.get("keys"), list)
        or not isinstance(public_environment.get("sha256"), str)
    ):
        fail("runtime binding has invalid public environment fingerprint")
    if not isinstance(payload["criteria"], dict) or not payload["criteria"]:
        fail("runtime criteria must be a non-empty object")
    for criterion_id, value in payload["criteria"].items():
        validate_identifier(criterion_id, "criterion")
        validate_criterion(value, criterion_id)
    for key in ("attempts", "phase_history", "rebindings"):
        if not isinstance(payload[key], list):
            fail(f"runtime ledger {key} must be a list")
    for event in payload["attempts"]:
        if not isinstance(event, dict):
            fail("attempt event must be an object")
        if event.get("criterion") not in payload["criteria"]:
            fail("attempt references an undeclared criterion")
        if event.get("kind") not in ATTEMPT_KINDS:
            fail("attempt has invalid kind")
        if event.get("classification") not in CLASSIFICATIONS:
            fail("attempt has invalid classification")
        if event.get("result") not in RESULTS:
            fail("attempt has invalid result")
        validate_identifier(event.get("strategy_id", ""), "strategy")
        references = event.get("evidence_refs")
        if not isinstance(references, list):
            fail("attempt evidence must be a list")
        for reference in references:
            if not isinstance(reference, str):
                fail("attempt has invalid evidence reference")
            validate_reference(reference)
    previous = "UNREADY"
    for event in payload["phase_history"]:
        if (
            not isinstance(event, dict)
            or event.get("from") != previous
            or event.get("to") not in TRANSITIONS[previous]
        ):
            fail("runtime phase history is inconsistent")
        validate_reference(event.get("evidence_ref", ""))
        previous = event["to"]
    if payload["phase_history"] and previous != payload["phase"]:
        fail("runtime phase does not match phase history")
    if not payload["phase_history"] and payload["phase"] != "UNREADY":
        fail("runtime phase history is missing")
    for event in payload["rebindings"]:
        if not isinstance(event, dict):
            fail("runtime rebinding event must be an object")
        if not isinstance(event.get("from_revision"), str) or not isinstance(
            event.get("to_revision"), str
        ):
            fail("runtime rebinding revision is invalid")
        if not isinstance(event.get("changed_bindings"), list):
            fail("runtime rebinding changes must be a list")
        if not isinstance(event.get("invalidated_criteria"), list):
            fail("runtime rebinding invalidations must be a list")
        validate_reference(event.get("evidence_ref", ""))
    return payload


def load_manifest(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"runtime ledger not found: {path}")
    except json.JSONDecodeError as error:
        fail(f"invalid runtime ledger JSON: {error}")
    return validate_manifest(payload)


def write_manifest(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload["updated_at"] = now()
    encoded = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=path.parent,
        prefix=f".{path.name}.",
        delete=False,
    ) as handle:
        handle.write(encoded)
        temporary = Path(handle.name)
    os.replace(temporary, path)


@contextmanager
def manifest_lock(path: Path, exclusive: bool) -> Iterator[None]:
    lock_path = Path(f"{path}.lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH)
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def mutate(path: Path, operation: Callable[[dict[str, Any]], Any]) -> Any:
    with manifest_lock(path, exclusive=True):
        payload = load_manifest(path)
        result = operation(payload)
        validate_manifest(payload)
        write_manifest(path, payload)
        return result


def criterion_record() -> dict[str, Any]:
    return {
        "status": "pending",
        "evidence_refs": [],
        "history": [],
    }


def command_create(args: argparse.Namespace) -> None:
    output = Path(args.output).resolve()
    criteria = sorted(
        {validate_identifier(value, "criterion") for value in args.criterion}
    )
    if not criteria:
        fail("at least one --criterion is required")
    timestamp = now()
    payload = {
        "schema_version": SCHEMA_VERSION,
        "phase": "UNREADY",
        "created_at": timestamp,
        "updated_at": timestamp,
        "bindings": {
            "project_root": str(Path(args.project_root).resolve()),
            "revision": args.revision,
            "device_udid": args.device_udid,
            "runtime": args.runtime,
            "app_id": args.app_id,
            "artifact_identity": args.artifact_identity,
            "metro_project_root": str(
                Path(args.metro_project_root or args.project_root).resolve()
            ),
            "metro_port": args.metro_port,
            "metro_interface": args.metro_interface,
            "public_environment": public_environment_fingerprint(
                args.public_environment_key
            ),
            "backend_topology": args.backend_topology,
            "backend_probe_status": args.backend_probe_status,
            "session": args.session,
            "state_dir": str(Path(args.state_dir).resolve()),
        },
        "criteria": {criterion: criterion_record() for criterion in criteria},
        "attempts": [],
        "phase_history": [],
        "rebindings": [],
    }
    with manifest_lock(output, exclusive=True):
        if output.exists():
            fail(f"runtime ledger already exists: {output}")
        validate_manifest(payload)
        write_manifest(output, payload)
    print(json.dumps({"ledger": str(output), "phase": "UNREADY"}))


def command_validate(args: argparse.Namespace) -> None:
    path = Path(args.ledger).resolve()
    with manifest_lock(path, exclusive=False):
        payload = load_manifest(path)
    print(
        json.dumps(
            {
                "ledger": str(path),
                "phase": payload["phase"],
                "criteria": sorted(payload["criteria"]),
                "valid": True,
            },
            sort_keys=True,
        )
    )


def command_phase(args: argparse.Namespace) -> None:
    path = Path(args.ledger).resolve()
    reference = validate_reference(args.evidence_ref, require_local_exists=True)

    def operation(payload: dict[str, Any]) -> dict[str, str]:
        current = payload["phase"]
        if args.to not in TRANSITIONS[current]:
            fail(f"invalid phase transition: {current} -> {args.to}")
        payload["phase"] = args.to
        payload["phase_history"].append(
            {
                "at": now(),
                "from": current,
                "to": args.to,
                "evidence_ref": reference,
            }
        )
        return {"from": current, "to": args.to}

    print(json.dumps(mutate(path, operation), sort_keys=True))


def command_declare(args: argparse.Namespace) -> None:
    path = Path(args.ledger).resolve()
    criteria = sorted(
        {validate_identifier(value, "criterion") for value in args.criterion}
    )

    def operation(payload: dict[str, Any]) -> dict[str, Any]:
        if payload["phase"] == "ACTIVE":
            fail("declare criteria only while runtime is not active")
        added = []
        for criterion in criteria:
            if criterion not in payload["criteria"]:
                payload["criteria"][criterion] = criterion_record()
                added.append(criterion)
        return {"added": added}

    print(json.dumps(mutate(path, operation), sort_keys=True))


def command_rebind(args: argparse.Namespace) -> None:
    path = Path(args.ledger).resolve()
    reference = validate_reference(args.evidence_ref, require_local_exists=True)
    updates = {
        key: value
        for key, value in {
            "project_root": (
                str(Path(args.project_root).resolve())
                if args.project_root is not None
                else None
            ),
            "revision": args.revision,
            "device_udid": args.device_udid,
            "runtime": args.runtime,
            "app_id": args.app_id,
            "artifact_identity": args.artifact_identity,
            "metro_project_root": (
                str(Path(args.metro_project_root).resolve())
                if args.metro_project_root is not None
                else None
            ),
            "metro_port": args.metro_port,
            "metro_interface": args.metro_interface,
            "backend_topology": args.backend_topology,
            "backend_probe_status": args.backend_probe_status,
            "session": args.session,
            "state_dir": (
                str(Path(args.state_dir).resolve())
                if args.state_dir is not None
                else None
            ),
        }.items()
        if value is not None
    }
    if args.public_environment_key is not None:
        updates["public_environment"] = public_environment_fingerprint(
            args.public_environment_key
        )
    if not updates:
        fail("rebind requires at least one changed binding argument")

    def operation(payload: dict[str, Any]) -> dict[str, Any]:
        if payload["phase"] == "ACTIVE":
            fail("rebind only while runtime is not active")
        before = dict(payload["bindings"])
        changed_bindings = sorted(
            key
            for key, value in updates.items()
            if payload["bindings"].get(key) != value
        )
        if not changed_bindings:
            fail("rebind does not change any binding")
        payload["bindings"].update(updates)
        invalidated = sorted(
            criterion
            for criterion, record in payload["criteria"].items()
            if record["status"] != "pending"
        )
        for criterion in invalidated:
            record = payload["criteria"][criterion]
            record["history"].append(
                {
                    "at": now(),
                    "status": "pending",
                    "evidence_refs": [],
                    "change_ref": reference,
                    "reason": "binding-invalidated",
                }
            )
            record["status"] = "pending"
            record["evidence_refs"] = []
        payload["rebindings"].append(
            {
                "at": now(),
                "from_revision": before["revision"],
                "to_revision": payload["bindings"]["revision"],
                "changed_bindings": changed_bindings,
                "evidence_ref": reference,
                "invalidated_criteria": invalidated,
            }
        )
        return {
            "revision": payload["bindings"]["revision"],
            "changed_bindings": changed_bindings,
            "invalidated_criteria": invalidated,
        }

    print(json.dumps(mutate(path, operation), sort_keys=True))


def command_attempt(args: argparse.Namespace) -> None:
    path = Path(args.ledger).resolve()
    criterion = validate_identifier(args.criterion, "criterion")
    strategy = validate_identifier(args.strategy_id, "strategy")
    references = [
        validate_reference(value, require_local_exists=False)
        for value in args.evidence_ref
    ]

    def operation(payload: dict[str, Any]) -> dict[str, Any]:
        if payload["phase"] != "ACTIVE":
            fail("record attempts only while runtime is ACTIVE")
        if criterion not in payload["criteria"]:
            fail(f"attempt references undeclared criterion: {criterion}")
        same_kind = [
            event
            for event in payload["attempts"]
            if event["criterion"] == criterion and event["kind"] == args.kind
        ]
        if same_kind:
            fail(f"{args.kind} strategy budget exhausted for {criterion}", code=3)
        if any(
            event["criterion"] == criterion
            and event["strategy_id"] == strategy
            for event in payload["attempts"]
        ):
            fail(f"strategy already recorded for {criterion}: {strategy}", code=3)
        payload["attempts"].append(
            {
                "at": now(),
                "criterion": criterion,
                "strategy_id": strategy,
                "kind": args.kind,
                "classification": args.classification,
                "result": args.result,
                "evidence_refs": references,
                "revision": payload["bindings"]["revision"],
            }
        )
        return {
            "criterion": criterion,
            "strategy_id": strategy,
            "kind": args.kind,
        }

    print(json.dumps(mutate(path, operation), sort_keys=True))


def command_evidence(args: argparse.Namespace) -> None:
    path = Path(args.ledger).resolve()
    criterion = validate_identifier(args.criterion, "criterion")
    observer = validate_identifier(args.observer_id, "observer")
    references = [
        validate_reference(value, require_local_artifact=True)
        for value in args.assertion_ref
    ]
    if not references:
        fail("at least one --assertion-ref is required")

    def operation(payload: dict[str, Any]) -> dict[str, Any]:
        if payload["phase"] != "ACTIVE":
            fail("record evidence only while runtime is ACTIVE")
        if criterion not in payload["criteria"]:
            fail(f"evidence references undeclared criterion: {criterion}")
        record = payload["criteria"][criterion]
        event = {
            "at": now(),
            "status": args.status,
            "evidence_refs": references,
            "revision": payload["bindings"]["revision"],
            "observer_id": observer,
        }
        record["history"].append(event)
        record["status"] = args.status
        record["evidence_refs"] = references
        return {
            "criterion": criterion,
            "status": args.status,
            "observer_id": observer,
        }

    print(json.dumps(mutate(path, operation), sort_keys=True))


def command_handoff(args: argparse.Namespace) -> None:
    path = Path(args.ledger).resolve()
    with manifest_lock(path, exclusive=False):
        payload = load_manifest(path)
    selected = (
        sorted(
            {
                validate_identifier(value, "criterion")
                for value in args.criterion
            }
        )
        if args.criterion
        else sorted(payload["criteria"])
    )
    missing = sorted(set(selected) - set(payload["criteria"]))
    if missing:
        fail(f"handoff references undeclared criterion: {missing[0]}")
    for criterion in selected:
        for reference in payload["criteria"][criterion]["evidence_refs"]:
            validate_reference(reference, require_local_artifact=True)
    groups = {
        status: sorted(
            criterion
            for criterion in selected
            if payload["criteria"][criterion]["status"] == status
        )
        for status in sorted(STATUSES)
    }
    if groups["pending"]:
        readiness = "incomplete"
    elif groups["not_observed"]:
        readiness = "manual_verification_required"
    else:
        readiness = "evidence_complete"
    summary = {
        "schema_version": payload["schema_version"],
        "bindings": payload["bindings"],
        "phase": payload["phase"],
        "criteria": groups,
        "criterion_details": {
            criterion: {
                "status": payload["criteria"][criterion]["status"],
                "evidence_refs": payload["criteria"][criterion]["evidence_refs"],
                "latest_observer": (
                    payload["criteria"][criterion]["history"][-1].get("observer_id")
                    if payload["criteria"][criterion]["history"]
                    else None
                ),
                "latest_revision": (
                    payload["criteria"][criterion]["history"][-1].get("revision")
                    if payload["criteria"][criterion]["history"]
                    else None
                ),
            }
            for criterion in selected
        },
        "attempts": [
            event
            for event in payload["attempts"]
            if event["criterion"] in selected
        ],
        "readiness": readiness,
        "cleanup_complete": payload["phase"] == "CLEANED",
    }
    print(json.dumps(summary, indent=2, sort_keys=True))


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(
        description="Maintain a serial, non-secret iOS Simulator runtime ledger.",
        epilog=(
            "Lifecycle: UNREADY -> READY -> ACTIVE. Attempts and evidence "
            "require ACTIVE. Leave ACTIVE before declare or rebind. Move to "
            "CLEANED after cleanup; CLEANED -> READY resumes after revalidation."
        ),
    )
    commands = root.add_subparsers(dest="command", required=True)

    create = commands.add_parser("create")
    create.add_argument("--output", required=True)
    create.add_argument("--project-root", required=True)
    create.add_argument("--revision", required=True)
    create.add_argument("--device-udid", required=True)
    create.add_argument("--runtime", required=True)
    create.add_argument("--app-id", required=True)
    create.add_argument("--artifact-identity")
    create.add_argument("--metro-project-root")
    create.add_argument("--metro-port", type=int)
    create.add_argument("--metro-interface")
    create.add_argument("--public-environment-key", action="append", default=[])
    create.add_argument(
        "--backend-topology",
        choices=sorted(BACKEND_TOPOLOGIES),
        default="none",
    )
    create.add_argument(
        "--backend-probe-status",
        choices=sorted(BACKEND_PROBE_STATUSES),
        default="unverified",
    )
    create.add_argument("--session", required=True)
    create.add_argument("--state-dir", required=True)
    create.add_argument("--criterion", action="append", required=True)
    create.set_defaults(function=command_create)

    validate = commands.add_parser("validate")
    validate.add_argument("--ledger", required=True)
    validate.set_defaults(function=command_validate)

    phase = commands.add_parser(
        "phase",
        description=(
            "Lifecycle: UNREADY -> READY -> ACTIVE. ACTIVE may return to READY "
            "or move to CLEANED; READY may move to CLEANED; CLEANED -> READY "
            "resumes after revalidation."
        ),
    )
    phase.add_argument("--ledger", required=True)
    phase.add_argument("--to", choices=sorted(PHASES), required=True)
    phase.add_argument("--evidence-ref", required=True)
    phase.set_defaults(function=command_phase)

    declare = commands.add_parser("declare")
    declare.add_argument("--ledger", required=True)
    declare.add_argument("--criterion", action="append", required=True)
    declare.set_defaults(function=command_declare)

    rebind = commands.add_parser(
        "rebind",
        description=(
            "Update runtime identity while not ACTIVE. Any real binding change "
            "automatically invalidates all current observations."
        ),
    )
    rebind.add_argument("--ledger", required=True)
    rebind.add_argument("--project-root")
    rebind.add_argument("--revision")
    rebind.add_argument("--artifact-identity")
    rebind.add_argument("--device-udid")
    rebind.add_argument("--runtime")
    rebind.add_argument("--app-id")
    rebind.add_argument("--metro-project-root")
    rebind.add_argument("--metro-port", type=int)
    rebind.add_argument("--metro-interface")
    rebind.add_argument("--public-environment-key", action="append")
    rebind.add_argument(
        "--backend-topology",
        choices=sorted(BACKEND_TOPOLOGIES),
    )
    rebind.add_argument(
        "--backend-probe-status",
        choices=sorted(BACKEND_PROBE_STATUSES),
    )
    rebind.add_argument("--session")
    rebind.add_argument("--state-dir")
    rebind.add_argument("--evidence-ref", required=True)
    rebind.set_defaults(function=command_rebind)

    attempt = commands.add_parser(
        "attempt",
        description=(
            "Record a failed or inconclusive complete strategy that consumes "
            "the shared retry budget. Record successful observations as evidence."
        ),
    )
    attempt.add_argument("--ledger", required=True)
    attempt.add_argument("--criterion", required=True)
    attempt.add_argument("--strategy-id", required=True)
    attempt.add_argument("--kind", choices=sorted(ATTEMPT_KINDS), required=True)
    attempt.add_argument(
        "--classification", choices=sorted(CLASSIFICATIONS), required=True
    )
    attempt.add_argument("--result", choices=sorted(RESULTS), required=True)
    attempt.add_argument("--evidence-ref", action="append", default=[])
    attempt.set_defaults(function=command_attempt)

    evidence = commands.add_parser(
        "evidence",
        description=(
            "Record a behavioral observation. Local assertion references must "
            "be durable, non-empty files containing the semantic result."
        ),
    )
    evidence.add_argument("--ledger", required=True)
    evidence.add_argument("--criterion", required=True)
    evidence.add_argument("--observer-id", required=True)
    evidence.add_argument(
        "--status",
        choices=["observed", "not_observed"],
        required=True,
    )
    evidence.add_argument("--assertion-ref", action="append", required=True)
    evidence.set_defaults(function=command_evidence)

    handoff = commands.add_parser("handoff")
    handoff.add_argument("--ledger", required=True)
    handoff.add_argument("--criterion", action="append", default=[])
    handoff.set_defaults(function=command_handoff)
    return root


def main() -> None:
    args = parser().parse_args()
    args.function(args)


if __name__ == "__main__":
    main()
