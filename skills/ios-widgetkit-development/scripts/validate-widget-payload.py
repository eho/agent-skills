#!/usr/bin/env python3
"""Validate JSON intended to cross into WidgetKit property-list storage."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any, Union


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Reject values that cannot safely bridge from JSON into a property list."
    )
    parser.add_argument("payload", type=Path, help="JSON payload to validate")
    parser.add_argument(
        "--max-bytes",
        type=int,
        default=None,
        help="Fail when compact UTF-8 JSON exceeds this size",
    )
    return parser.parse_args()


def child_path(path: str, key: Union[str, int]) -> str:
    if isinstance(key, int):
        return f"{path}[{key}]"
    return f"{path}.{key}" if path else key


def validate(value: Any, path: str = "$") -> list[str]:
    errors: list[str] = []
    if value is None:
        errors.append(f"{path}: null is not property-list safe")
    elif isinstance(value, (bool, str)):
        pass
    elif isinstance(value, int):
        if value < -(2**63) or value > 2**63 - 1:
            errors.append(f"{path}: integer exceeds the signed 64-bit property-list range")
    elif isinstance(value, float):
        if not math.isfinite(value):
            errors.append(f"{path}: non-finite number is not property-list safe")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            errors.extend(validate(item, child_path(path, index)))
    elif isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                errors.append(f"{path}: dictionary key {key!r} is not a string")
                continue
            errors.extend(validate(item, child_path(path, key)))
    else:
        errors.append(f"{path}: unsupported value type {type(value).__name__}")
    return errors


def main() -> int:
    args = parse_args()
    try:
        raw = args.payload.read_bytes()
        payload = json.loads(raw, parse_constant=lambda value: float(value))
    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(json.dumps({"valid": False, "error": str(error)}, indent=2))
        return 2

    errors = validate(payload)
    compact = json.dumps(
        payload, ensure_ascii=False, allow_nan=True, separators=(",", ":")
    ).encode("utf-8")
    if args.max_bytes is not None and len(compact) > args.max_bytes:
        errors.append(
            f"$: compact payload is {len(compact)} bytes; limit is {args.max_bytes}"
        )

    print(
        json.dumps(
            {
                "valid": not errors,
                "compactBytes": len(compact),
                "maxBytes": args.max_bytes,
                "errors": errors,
            },
            indent=2,
        )
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
