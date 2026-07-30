#!/usr/bin/env python3
"""Validate Expo launcher assets and any optional splash or web outputs."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError as exc:
    raise SystemExit("Pillow is required: python3 -m pip install Pillow") from exc


ANDROID_SAFE_RATIO = 66 / 108
CORE = {
    "icon.png": (1024, 1024),
    "android-icon-foreground.png": (1024, 1024),
    "android-icon-monochrome.png": (1024, 1024),
}
OPTIONAL = {
    "splash-icon.png": (1024, 1024),
    "favicon.png": (48, 48),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assets-dir", required=True, type=Path)
    parser.add_argument("--app-json", type=Path)
    parser.add_argument("--safe-ratio", type=float, default=ANDROID_SAFE_RATIO)
    return parser.parse_args()


def alpha(image: Image.Image) -> Image.Image:
    return image.convert("RGBA").getchannel("A")


def resolved_asset(app_json: Path, value: str) -> Path:
    return (app_json.parent / value).resolve()


def load_assets(directory: Path, errors: list[str]) -> dict[str, Image.Image]:
    images: dict[str, Image.Image] = {}
    for name, size in {**CORE, **OPTIONAL}.items():
        path = directory / name
        if not path.is_file():
            if name in CORE:
                errors.append(f"missing {path}")
            continue
        image = Image.open(path)
        image.load()
        images[name] = image
        if image.format != "PNG":
            errors.append(f"{name}: expected PNG data, found {image.format}")
        if image.size != size:
            errors.append(f"{name}: expected {size}, found {image.size}")
    return images


def check_mark_bounds(
    name: str, image: Image.Image, safe_ratio: float, errors: list[str]
) -> None:
    bbox = alpha(image).getbbox()
    if bbox is None:
        errors.append(f"{name} has no visible pixels")
        return
    width, height = bbox[2] - bbox[0], bbox[3] - bbox[1]
    limit = round(1024 * safe_ratio)
    if width > limit or height > limit:
        errors.append(f"{name} bounds {width}x{height} exceed {limit}px safe limit")
    print(f"{name} bounds: {width}x{height}px")


def check_config(app_json: Path, errors: list[str]) -> None:
    try:
        expo = json.loads(app_json.read_text())["expo"]
        adaptive = expo["android"]["adaptiveIcon"]
        values = {
            "icon": expo["icon"],
            "ios.icon": expo["ios"]["icon"],
            "android.icon": expo["android"]["icon"],
            "android.foregroundImage": adaptive["foregroundImage"],
            "android.monochromeImage": adaptive["monochromeImage"],
        }
        if "backgroundImage" in adaptive and "backgroundColor" in adaptive:
            errors.append(
                "adaptiveIcon.backgroundImage overrides backgroundColor; choose one"
            )
        color = adaptive.get("backgroundColor")
        if color is not None and not re.fullmatch(r"#[0-9A-Fa-f]{6}", color):
            errors.append("adaptiveIcon.backgroundColor must be #RRGGBB")

        web = expo.get("web", {})
        if "favicon" in web:
            values["web.favicon"] = web["favicon"]

        for plugin in expo.get("plugins", []):
            if isinstance(plugin, list) and plugin and plugin[0] == "expo-splash-screen":
                settings = plugin[1] if len(plugin) > 1 else {}
                if "image" in settings:
                    values["splash.image"] = settings["image"]
                break

        for field, value in values.items():
            if not resolved_asset(app_json, value).is_file():
                errors.append(f"{field} does not resolve: {value}")
    except (KeyError, TypeError, json.JSONDecodeError) as exc:
        errors.append(f"invalid Expo icon configuration: {exc}")


def main() -> int:
    args = parse_args()
    errors: list[str] = []
    images = load_assets(args.assets_dir, errors)

    icon = images.get("icon.png")
    if icon and alpha(icon).getextrema() != (255, 255):
        errors.append("icon.png must be fully opaque")

    foreground = images.get("android-icon-foreground.png")
    if foreground:
        if alpha(foreground).getextrema()[0] == 255:
            errors.append("android-icon-foreground.png must retain transparency")
        check_mark_bounds(
            "android-icon-foreground.png", foreground, args.safe_ratio, errors
        )

    monochrome = images.get("android-icon-monochrome.png")
    if monochrome:
        check_mark_bounds(
            "android-icon-monochrome.png", monochrome, args.safe_ratio, errors
        )
        visible_colors = {
            pixel[:3]
            for pixel in monochrome.convert("RGBA").getdata()
            if pixel[3] > 0
        }
        if len(visible_colors) != 1:
            errors.append("monochrome layer must use exactly one visible RGB color")

    splash = images.get("splash-icon.png")
    if splash and alpha(splash).getextrema()[0] == 255:
        errors.append("splash-icon.png must retain transparency")

    if args.app_json:
        check_config(args.app_json, errors)

    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("PASS: Expo icon assets and configuration are structurally valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
