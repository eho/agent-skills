#!/usr/bin/env python3
"""Assign stable per-finding IDs from a structured blocking-findings ledger."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


REQUIRED_FIELDS = {
    "stable_key",
    "severity",
    "location",
    "behavior",
    "impact",
    "required_change",
}


def normalized(value: str) -> str:
    return "\n".join(
        line.rstrip(" \t")
        for line in value.replace("\r\n", "\n").replace("\r", "\n").strip().split("\n")
    )


def fingerprint(findings: object) -> list[dict[str, str]]:
    if not isinstance(findings, list):
        raise ValueError("findings file must be a JSON array")
    result: list[dict[str, str]] = []
    seen: set[str] = set()
    for index, finding in enumerate(findings):
        if not isinstance(finding, dict) or set(finding) != REQUIRED_FIELDS:
            raise ValueError(
                f"finding {index} must contain exactly: {', '.join(sorted(REQUIRED_FIELDS))}"
            )
        if not all(isinstance(value, str) and normalized(value) for value in finding.values()):
            raise ValueError(f"finding {index} fields must be non-empty strings")
        stable_key = normalized(finding["stable_key"])
        if stable_key in seen:
            raise ValueError(f"duplicate stable_key: {stable_key}")
        seen.add(stable_key)
        record = {key: normalized(finding[key]) for key in sorted(REQUIRED_FIELDS)}
        record["id"] = hashlib.sha256(stable_key.encode("utf-8")).hexdigest()
        result.append(record)
    return sorted(result, key=lambda item: item["id"])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("findings_file", type=Path)
    args = parser.parse_args()
    try:
        content = json.loads(args.findings_file.read_text(encoding="utf-8"))
        result = fingerprint(content)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        parser.error(str(error))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
