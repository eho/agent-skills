#!/usr/bin/env python3
"""Choose the next deterministic delivery-attempt ID for a composite story."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import PurePosixPath


STORY_RE = re.compile(r"^(?:[A-Z][A-Z0-9]{1,9}-[0-9]{3,}|GAP-[0-9A-F]{12})$")


def base_id(design_identity: str, story_id: str) -> str:
    if (
        not design_identity
        or design_identity.startswith("/")
        or "\n" in design_identity
        or any(part == ".." for part in PurePosixPath(design_identity).parts)
    ):
        raise ValueError("design identity must be a safe repository-relative path")
    if not STORY_RE.fullmatch(story_id):
        raise ValueError(f"invalid story ID: {story_id}")
    slug = re.sub(r"[^a-z0-9]+", "-", PurePosixPath(design_identity).stem.lower()).strip("-")
    slug = (slug or "design")[:40]
    identity_hash = hashlib.sha256(design_identity.encode("utf-8")).hexdigest()[:8]
    return f"{slug}-{identity_hash}-{story_id.lower()}"


def next_id(design_identity: str, story_id: str, existing: list[str]) -> str:
    prefix = base_id(design_identity, story_id)
    pattern = re.compile(rf"^{re.escape(prefix)}-a([1-9][0-9]*)$")
    attempts = [int(match.group(1)) for value in existing if (match := pattern.fullmatch(value))]
    return f"{prefix}-a{max(attempts, default=0) + 1}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--design-identity", required=True)
    parser.add_argument("--story-id", required=True)
    parser.add_argument(
        "--existing-ids-json",
        default="[]",
        help="JSON array of delivery IDs discovered across open, closed, and merged PRs",
    )
    args = parser.parse_args()
    try:
        existing = json.loads(args.existing_ids_json)
        if not isinstance(existing, list) or not all(isinstance(item, str) for item in existing):
            raise ValueError("existing IDs must be a JSON array of strings")
        value = next_id(args.design_identity, args.story_id, existing)
    except (json.JSONDecodeError, ValueError) as error:
        parser.error(str(error))
    print(value)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
