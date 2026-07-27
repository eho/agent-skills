#!/usr/bin/env python3
"""Validate and compute deterministic design-document and user-story identities."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


HEADING_RE = re.compile(r"^(#{1,6})[ \t]+(.+?)[ \t]*$")
STORY_ID_RE = re.compile(r"\b([A-Z][A-Z0-9]{1,9}-[0-9]{3,})\b")
STATUS_RE = re.compile(
    r"(?i)^\s*(?:\*\*)?Status(?::(?:\*\*)?|\*\*:)\s*(?:\*\*)?([A-Za-z]+)(?:\*\*)?\s*$"
)
DEPENDENCY_RE = re.compile(
    r"(?i)^\s*(?:[-*]\s*)?(?:\*\*)?Depends on(?::(?:\*\*)?|\*\*:)\s*(.+?)\s*$"
)
OUTCOME_RE = re.compile(
    r"(?i)^\s*(?:[-*]\s*)?(?:\*\*)?Outcome(?::(?:\*\*)?|\*\*:)\s*(.+?)\s*$"
)
OUT_OF_SCOPE_RE = re.compile(
    r"(?i)^\s*(?:[-*]\s*)?(?:\*\*)?Out of scope(?::(?:\*\*)?|\*\*:)\s*(.+?)\s*$"
)
ACCEPTANCE_RE = re.compile(
    r"(?i)^\s*(?:\*\*)?Acceptance Criteria(?::(?:\*\*)?|\*\*:)\s*$"
)
VERIFICATION_RE = re.compile(
    r"(?i)^\s*(?:\*\*)?Verification(?::(?:\*\*)?|\*\*:)\s*$"
)
FIELD_HEADER_RE = re.compile(
    r"^\s*(?:[-*]\s+)?\*\*[^*]+(?::\*\*|\*\*:)(?:\s+.*)?$"
)
CHECKBOX_RE = re.compile(r"^\s*[-*]\s+\[[ xX]\]\s+\S")
LIST_ITEM_RE = re.compile(r"^\s*[-*]\s+\S")
FENCE_RE = re.compile(r"^[ \t]{0,3}(`{3,}|~{3,})")


def normalize_markdown(text: str) -> str:
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    lines = [line.rstrip(" \t") for line in lines]
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines) + "\n"


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def clean_heading(value: str) -> str:
    return value.rstrip().rstrip("#").rstrip()


def structural_lines(lines: list[str]) -> list[bool]:
    """Return a mask that excludes fenced-code content from Markdown structure."""
    visible: list[bool] = []
    fence_character = ""
    fence_length = 0
    for line in lines:
        match = FENCE_RE.match(line)
        if not fence_character:
            if match:
                fence = match.group(1)
                fence_character = fence[0]
                fence_length = len(fence)
                visible.append(False)
            else:
                visible.append(True)
            continue

        visible.append(False)
        stripped = line.lstrip(" \t")
        if (
            stripped.startswith(fence_character * fence_length)
            and set(stripped.rstrip()) <= {fence_character}
        ):
            fence_character = ""
            fence_length = 0
    return visible


def dependency_ids(source: str, story_id: str) -> list[str]:
    lines = source.splitlines()
    visible = structural_lines(lines)
    matches: list[str] = []
    for line, is_visible in zip(lines, visible):
        if not is_visible:
            continue
        match = DEPENDENCY_RE.fullmatch(line)
        if match:
            matches.append(match.group(1))
    if len(matches) != 1:
        raise ValueError(
            f"{story_id} must contain exactly one 'Depends on:' declaration; found {len(matches)}"
        )
    value = matches[0].strip()
    if value.lower() == "none":
        return []
    identifier = r"[A-Z][A-Z0-9]{1,9}-[0-9]{3,}"
    if not re.fullmatch(rf"{identifier}(?:\s*,\s*{identifier})*", value):
        raise ValueError(f"{story_id} has malformed dependency metadata: {value}")
    identifiers = STORY_ID_RE.findall(value)
    if len(identifiers) != len(set(identifiers)):
        raise ValueError(f"{story_id} repeats a dependency")
    return identifiers


def single_field(
    lines: list[str],
    visible: list[bool],
    pattern: re.Pattern[str],
    story_id: str,
    field_name: str,
) -> tuple[int, str]:
    matches = [
        (index, match.group(1).strip())
        for index, (line, is_visible) in enumerate(zip(lines, visible))
        if is_visible and (match := pattern.fullmatch(line))
    ]
    if len(matches) != 1 or not matches[0][1]:
        raise ValueError(f"{story_id} must contain exactly one non-empty '{field_name}:' field")
    return matches[0]


def field_body_end(lines: list[str], visible: list[bool], start: int) -> int:
    for index in range(start + 1, len(lines)):
        if not visible[index]:
            continue
        if (
            HEADING_RE.fullmatch(lines[index])
            or FIELD_HEADER_RE.fullmatch(lines[index])
            or ACCEPTANCE_RE.fullmatch(lines[index])
            or VERIFICATION_RE.fullmatch(lines[index])
            or OUTCOME_RE.fullmatch(lines[index])
            or OUT_OF_SCOPE_RE.fullmatch(lines[index])
        ):
            return index
    return len(lines)


def story_structure(source: str, story_id: str) -> None:
    if "<!-- feature-delivery:" in source:
        raise ValueError(f"{story_id} contains a reserved feature-delivery marker")

    lines = source.splitlines()
    visible = structural_lines(lines)
    outcome, _ = single_field(lines, visible, OUTCOME_RE, story_id, "Outcome")
    out_of_scope, _ = single_field(
        lines, visible, OUT_OF_SCOPE_RE, story_id, "Out of scope"
    )

    acceptance = [
        index
        for index, (line, is_visible) in enumerate(zip(lines, visible))
        if is_visible and ACCEPTANCE_RE.fullmatch(line)
    ]
    verification = [
        index
        for index, (line, is_visible) in enumerate(zip(lines, visible))
        if is_visible and VERIFICATION_RE.fullmatch(line)
    ]
    if len(acceptance) != 1:
        raise ValueError(
            f"{story_id} must contain exactly one 'Acceptance Criteria:' section"
        )
    if len(verification) != 1:
        raise ValueError(f"{story_id} must contain exactly one 'Verification:' section")
    if not outcome < acceptance[0]:
        raise ValueError(f"{story_id} must place 'Outcome:' before 'Acceptance Criteria:'")
    if not out_of_scope < acceptance[0]:
        raise ValueError(
            f"{story_id} must place 'Out of scope:' before 'Acceptance Criteria:'"
        )
    if not acceptance[0] < verification[0]:
        raise ValueError(
            f"{story_id} must place 'Acceptance Criteria:' before 'Verification:'"
        )

    acceptance_end = field_body_end(lines, visible, acceptance[0])
    criteria = [
        line
        for line, is_visible in zip(
            lines[acceptance[0] + 1 : acceptance_end],
            visible[acceptance[0] + 1 : acceptance_end],
        )
        if is_visible and CHECKBOX_RE.match(line)
    ]
    if not criteria:
        raise ValueError(
            f"{story_id} must contain at least one acceptance-criteria checkbox"
        )

    verification_end = field_body_end(lines, visible, verification[0])
    verification_body = [
        line
        for line, is_visible in zip(
            lines[verification[0] + 1 : verification_end],
            visible[verification[0] + 1 : verification_end],
        )
        if is_visible and LIST_ITEM_RE.match(line)
    ]
    if not verification_body:
        raise ValueError(
            f"{story_id} must contain at least one verification instruction"
        )


def document_status(lines: list[str], visible: list[bool], mode: str) -> str:
    statuses = [
        match.group(1).casefold()
        for line, is_visible in zip(lines, visible)
        if is_visible and (match := STATUS_RE.fullmatch(line))
    ]
    if len(statuses) != 1:
        raise ValueError("design document must contain exactly one Status: Draft or Status: Revised")
    if statuses[0] not in {"draft", "revised"}:
        raise ValueError(
            f"unsupported actionable design status: {statuses[0].title()}; "
            "expected Draft or Revised"
        )
    status = statuses[0].title()
    if mode == "delivery" and status != "Revised":
        raise ValueError("delivery mode requires Status: Revised")
    return status


def build_manifest(
    design_path: Path,
    repo_root: Path,
    include_source: bool,
    mode: str = "delivery",
) -> dict[str, object]:
    resolved_design = design_path.resolve()
    resolved_root = repo_root.resolve()
    try:
        identity = resolved_design.relative_to(resolved_root).as_posix()
    except ValueError as error:
        raise ValueError(f"design document is outside repository root: {resolved_design}") from error
    if "<!--" in identity or "-->" in identity or "\n" in identity:
        raise ValueError("design identity contains unsafe marker delimiters")

    normalized_document = normalize_markdown(resolved_design.read_text(encoding="utf-8"))
    lines = normalized_document.splitlines()
    visible = structural_lines(lines)
    status = document_status(lines, visible, mode)
    headings: list[tuple[int, int, str]] = []
    for index, line in enumerate(lines):
        if not visible[index]:
            continue
        match = HEADING_RE.match(line)
        if match:
            headings.append((index, len(match.group(1)), clean_heading(match.group(2))))

    user_sections = [heading for heading in headings if heading[2].casefold() == "user stories"]
    if len(user_sections) != 1:
        raise ValueError(f"expected exactly one 'User Stories' section, found {len(user_sections)}")

    user_line, user_level, _ = user_sections[0]
    section_end = len(lines)
    for line_number, level, _ in headings:
        if line_number > user_line and level <= user_level:
            section_end = line_number
            break

    story_headings: list[tuple[int, str, str]] = []
    for line_number, level, heading in headings:
        if not (user_line < line_number < section_end and level == user_level + 1):
            continue
        identifiers = STORY_ID_RE.findall(heading)
        if len(identifiers) != 1:
            raise ValueError(
                f"story heading on line {line_number + 1} must contain exactly one stable story ID"
            )
        story_headings.append((line_number, identifiers[0], heading))

    if not story_headings:
        raise ValueError("no stable story headings found beneath 'User Stories'")

    seen: set[str] = set()
    stories: list[dict[str, object]] = []
    for index, (start, story_id, heading) in enumerate(story_headings):
        if story_id in seen:
            raise ValueError(f"duplicate story ID: {story_id}")
        seen.add(story_id)
        end = story_headings[index + 1][0] if index + 1 < len(story_headings) else section_end
        source = normalize_markdown("\n".join(lines[start:end]))
        story_structure(source, story_id)
        story: dict[str, object] = {
            "id": story_id,
            "heading": heading,
            "start_line": start + 1,
            "end_line": end,
            "story_revision": digest(source),
            "dependencies": dependency_ids(source, story_id),
        }
        if include_source:
            story["source"] = source
        stories.append(story)

    graph = {
        str(story["id"]): [str(dependency) for dependency in story["dependencies"]]
        for story in stories
    }
    for story in stories:
        story_id = str(story["id"])
        for dependency in story["dependencies"]:
            if dependency not in graph:
                raise ValueError(f"{story_id} depends on unknown story {dependency}")
            if dependency == story_id:
                raise ValueError(f"{story_id} cannot depend on itself")

    state: dict[str, int] = {}
    path: list[str] = []

    def visit(story_id: str) -> None:
        status = state.get(story_id, 0)
        if status == 2:
            return
        if status == 1:
            cycle_start = path.index(story_id)
            cycle = path[cycle_start:] + [story_id]
            raise ValueError(f"cyclic story dependencies: {' -> '.join(cycle)}")
        state[story_id] = 1
        path.append(story_id)
        for dependency in graph[story_id]:
            visit(dependency)
        path.pop()
        state[story_id] = 2

    for story_id in graph:
        visit(story_id)

    return {
        "design_identity": identity,
        "design_revision": digest(normalized_document),
        "status": status,
        "stories": stories,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("design_doc", type=Path)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--include-source", action="store_true")
    parser.add_argument(
        "--mode",
        choices=("author", "delivery"),
        default="delivery",
        help="author accepts Draft or Revised; delivery requires Revised",
    )
    args = parser.parse_args()

    try:
        manifest = build_manifest(
            args.design_doc,
            args.repo_root,
            args.include_source,
            args.mode,
        )
    except (OSError, UnicodeError, ValueError) as error:
        parser.error(str(error))
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
