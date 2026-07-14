#!/usr/bin/env python3
"""Inventory an iOS .app and its embedded WidgetKit extensions."""

from __future__ import annotations

import argparse
import json
import plistlib
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Inspect a built iOS app, embedded extensions, entitlements, and AppIntent metadata."
    )
    parser.add_argument("--app", required=True, type=Path, help="Path to the .app")
    parser.add_argument(
        "--widget-bundle-id",
        help="Optional bundle identifier used to select one embedded extension",
    )
    return parser.parse_args()


def read_plist(path: Path) -> Dict[str, Any]:
    with path.open("rb") as handle:
        value = plistlib.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path} is not a dictionary plist")
    return value


def read_entitlements(bundle: Path) -> Tuple[Dict[str, Any], Optional[str]]:
    codesign = shutil.which("codesign")
    if codesign is None:
        return {}, "codesign is unavailable"
    result = subprocess.run(
        [codesign, "-d", "--entitlements", ":-", str(bundle)],
        capture_output=True,
        check=False,
    )
    candidates = [result.stdout, result.stderr]
    for candidate in candidates:
        start = candidate.find(b"<?xml")
        if start < 0:
            start = candidate.find(b"bplist")
        if start < 0:
            continue
        try:
            value = plistlib.loads(candidate[start:])
        except Exception:
            continue
        if isinstance(value, dict):
            return value, None
    message = result.stderr.decode("utf-8", errors="replace").strip()
    return {}, message or f"codesign exited with status {result.returncode}"


def metadata_paths(bundle: Path) -> list[str]:
    matches: set[str] = set()
    for root in bundle.iterdir():
        lowered = root.name.lower()
        if "appintent" not in lowered and not lowered.endswith("actionsdata"):
            continue
        matches.add(str(root.relative_to(bundle)))
        if root.is_dir():
            for path in root.rglob("*"):
                matches.add(str(path.relative_to(bundle)))
    return sorted(matches)


def bundle_record(bundle: Path) -> Dict[str, Any]:
    info_path = bundle / "Info.plist"
    info = read_plist(info_path)
    entitlements, entitlement_error = read_entitlements(bundle)
    extension = info.get("NSExtension", {})
    if not isinstance(extension, dict):
        extension = {}
    record: Dict[str, Any] = {
        "path": str(bundle.resolve()),
        "bundleIdentifier": info.get("CFBundleIdentifier"),
        "bundleName": info.get("CFBundleDisplayName") or info.get("CFBundleName"),
        "executable": info.get("CFBundleExecutable"),
        "extensionPointIdentifier": extension.get("NSExtensionPointIdentifier"),
        "entitlementsPresent": bool(entitlements),
        "appGroups": entitlements.get("com.apple.security.application-groups", []),
        "appIntentMetadata": metadata_paths(bundle),
    }
    if entitlement_error:
        record["entitlementsWarning"] = entitlement_error
    return record


def main() -> int:
    args = parse_args()
    app = args.app.resolve()
    if app.suffix != ".app" or not app.is_dir():
        print(json.dumps({"valid": False, "error": f"not an .app directory: {app}"}, indent=2))
        return 2
    try:
        host = bundle_record(app)
        plugin_dir = app / "PlugIns"
        extensions = [bundle_record(path) for path in sorted(plugin_dir.glob("*.appex"))]
    except (OSError, ValueError, plistlib.InvalidFileException) as error:
        print(json.dumps({"valid": False, "error": str(error)}, indent=2))
        return 2

    if args.widget_bundle_id:
        extensions = [
            item for item in extensions if item["bundleIdentifier"] == args.widget_bundle_id
        ]
    widget_extensions = [
        item
        for item in extensions
        if item["extensionPointIdentifier"] == "com.apple.widgetkit-extension"
    ]
    result = {
        "valid": bool(widget_extensions),
        "host": host,
        "extensions": extensions,
        "widgetExtensionCount": len(widget_extensions),
    }
    if args.widget_bundle_id and not extensions:
        result["error"] = f"extension not found: {args.widget_bundle_id}"
    elif not widget_extensions:
        result["error"] = "no WidgetKit extension found"
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
