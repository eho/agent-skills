#!/usr/bin/env python3
"""Render a canonical managed GitHub issue body from a story manifest."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def render(
    manifest: dict[str, Any],
    story_id: str,
    issue_map: dict[str, Any],
    design_url: str,
    allow_unresolved: bool = False,
) -> str:
    stories = {story["id"]: story for story in manifest.get("stories", [])}
    if story_id not in stories:
        raise ValueError(f"story not found in manifest: {story_id}")
    story = stories[story_id]
    source = story.get("source")
    if not isinstance(source, str) or not source.endswith("\n"):
        raise ValueError("manifest must be generated with --include-source")
    if "<!-- feature-delivery:" in source:
        raise ValueError("story source contains a reserved feature-delivery marker")

    dependency_lines: list[str] = []
    for dependency in story.get("dependencies", []):
        number = issue_map.get(dependency)
        if not isinstance(number, int) or number <= 0:
            if not allow_unresolved:
                raise ValueError(f"missing canonical issue number for dependency {dependency}")
            dependency_lines.append(f"- Depends on: pending (`{dependency}`)")
        else:
            dependency_lines.append(f"- Depends on: #{number} (`{dependency}`)")
    if not dependency_lines:
        dependency_lines.append("- None")

    values = [
        manifest.get("design_identity"),
        manifest.get("design_revision"),
        story.get("story_revision"),
        design_url,
    ]
    if not all(isinstance(value, str) and value and "\n" not in value for value in values):
        raise ValueError("manifest identity and design URL values must be non-empty single lines")
    if "<!--" in manifest["design_identity"] or "-->" in manifest["design_identity"]:
        raise ValueError("design identity contains unsafe marker delimiters")

    return (
        f"<!-- feature-delivery:design={manifest['design_identity']} -->\n"
        f"<!-- feature-delivery:story={story_id} -->\n"
        f"<!-- feature-delivery:design-revision={manifest['design_revision']} -->\n"
        f"<!-- feature-delivery:story-revision={story['story_revision']} -->\n\n"
        "## Managed Story Contract\n\n"
        f"{source}\n"
        "## Canonical Dependencies\n\n"
        f"{chr(10).join(dependency_lines)}\n\n"
        "## Design Doc\n\n"
        f"[View the complete design contract]({design_url})\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--story-id", required=True)
    parser.add_argument("--issue-map", required=True, type=Path)
    parser.add_argument("--design-url", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--allow-unresolved-dependencies", action="store_true")
    args = parser.parse_args()

    try:
        body = render(
            load_json(args.manifest),
            args.story_id,
            load_json(args.issue_map),
            args.design_url,
            args.allow_unresolved_dependencies,
        )
        with args.output.open("w", encoding="utf-8", newline="\n") as output:
            output.write(body)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
