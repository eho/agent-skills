#!/usr/bin/env python3
"""Normalize one blocking final-audit gap and compute its canonical identity."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path, PurePosixPath


FIELDS = {
    "stable_key",
    "design_identity",
    "design_revision",
    "category",
    "affected_stories",
    "evidence",
    "required_remediation",
    "acceptance_criteria",
    "verification",
    "dependencies",
}
STORY_ID = re.compile(r"^(?:[A-Z][A-Z0-9]{1,9}-[0-9]{3,}|GAP-[0-9A-F]{12})$")


def normalize_string(value: str) -> str:
    lines = value.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    normalized = "\n".join(line.rstrip(" \t") for line in lines).strip()
    if not normalized:
        raise ValueError("string values must not be empty")
    return normalized


def build_contract(raw: object) -> dict[str, object]:
    if not isinstance(raw, dict) or set(raw) != FIELDS:
        raise ValueError(f"payload must contain exactly: {', '.join(sorted(FIELDS))}")

    stable_key = raw["stable_key"]
    if not isinstance(stable_key, str):
        raise ValueError("stable_key must be a string")
    stable_key = normalize_string(stable_key)

    identity = raw["design_identity"]
    if not isinstance(identity, str):
        raise ValueError("design_identity must be a string")
    identity = normalize_string(identity)
    if (
        identity.startswith("/")
        or "\n" in identity
        or any(part == ".." for part in PurePosixPath(identity).parts)
        or "<!--" in identity
        or "-->" in identity
    ):
        raise ValueError("design_identity must be a safe repository-relative path")

    revision = raw["design_revision"]
    if not isinstance(revision, str) or not re.fullmatch(r"[0-9a-f]{64}", revision):
        raise ValueError("design_revision must be a lowercase SHA-256")
    category = raw["category"]
    if category not in {"integration-gap", "documentation-gap"}:
        raise ValueError("category must be integration-gap or documentation-gap")

    payload: dict[str, object] = {
        "stable_key": stable_key,
        "design_identity": identity,
        "design_revision": revision,
        "category": category,
    }
    for field in (
        "affected_stories",
        "evidence",
        "acceptance_criteria",
        "verification",
        "dependencies",
    ):
        value = raw[field]
        if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
            raise ValueError(f"{field} must be an array of strings")
        normalized = [normalize_string(item) for item in value]
        if field in {"affected_stories", "acceptance_criteria", "verification"} and not normalized:
            raise ValueError(f"{field} must not be empty")
        if field in {"affected_stories", "dependencies"}:
            invalid = [item for item in normalized if not STORY_ID.fullmatch(item)]
            if invalid:
                raise ValueError(f"{field} contains invalid IDs: {', '.join(invalid)}")
            if len(normalized) != len(set(normalized)):
                raise ValueError(f"{field} contains duplicate IDs")
        payload[field] = normalized

    remediation = raw["required_remediation"]
    if not isinstance(remediation, str):
        raise ValueError("required_remediation must be a string")
    payload["required_remediation"] = normalize_string(remediation)

    canonical = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    gap_revision = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    identity_digest = hashlib.sha256(stable_key.encode("utf-8")).hexdigest()
    return {
        "gap_id": f"GAP-{identity_digest[:12].upper()}",
        "gap_revision": gap_revision,
        "canonical_payload": canonical,
        "payload": payload,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("payload", type=Path)
    args = parser.parse_args()
    try:
        raw = json.loads(args.payload.read_text(encoding="utf-8"))
        contract = build_contract(raw)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        parser.error(str(error))
    print(json.dumps(contract, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
