#!/usr/bin/env python3
"""Generate selected Expo launcher assets from a master and transparent mark."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError as exc:
    raise SystemExit("Pillow is required: python3 -m pip install Pillow") from exc


CANVAS = 1024
ANDROID_SAFE_RATIO = 66 / 108


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--icon-master", required=True, type=Path)
    parser.add_argument("--mark", required=True, type=Path)
    parser.add_argument("--monochrome-mark", type=Path)
    parser.add_argument("--splash-mark", type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--background-color", required=True)
    parser.add_argument("--splash-background-color")
    parser.add_argument("--app-json", type=Path)
    parser.add_argument(
        "--config-prefix",
        default="./assets/images",
        help="app-root-relative asset directory used when --app-json is omitted",
    )
    parser.add_argument("--safe-ratio", type=float, default=ANDROID_SAFE_RATIO)
    parser.add_argument("--splash-image-width", type=int, default=180)
    parser.add_argument("--include-splash", action="store_true")
    parser.add_argument("--include-web", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--force",
        action="store_true",
        help="replace existing generated asset files",
    )
    return parser.parse_args()


def normalize_hex(value: str) -> str:
    value = value.strip().upper()
    if not value.startswith("#"):
        value = f"#{value}"
    if len(value) != 7:
        raise ValueError("color must be a six-character #RRGGBB value")
    int(value[1:], 16)
    return value


def load_image(path: Path) -> Image.Image:
    if not path.is_file():
        raise ValueError(f"missing input: {path}")
    image = Image.open(path)
    image.load()
    return image


def contain_mark(mark: Image.Image, safe_ratio: float) -> Image.Image:
    rgba = mark.convert("RGBA")
    bbox = rgba.getchannel("A").getbbox()
    if bbox is None:
        raise ValueError("transparent mark has no visible pixels")
    cropped = rgba.crop(bbox)
    max_side = round(CANVAS * safe_ratio)
    scale = min(max_side / cropped.width, max_side / cropped.height)
    size = (
        max(1, round(cropped.width * scale)),
        max(1, round(cropped.height * scale)),
    )
    resized = cropped.resize(size, Image.Resampling.LANCZOS)
    output = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    output.alpha_composite(
        resized,
        ((CANVAS - resized.width) // 2, (CANVAS - resized.height) // 2),
    )
    return output


def monochrome_layer(mark: Image.Image, safe_ratio: float) -> Image.Image:
    contained = contain_mark(mark, safe_ratio)
    output = Image.new("RGBA", contained.size, (255, 255, 255, 0))
    output.putalpha(contained.getchannel("A"))
    return output


def config_fragment(
    prefix: str,
    color: str,
    splash_color: str,
    splash_width: int,
    include_splash: bool,
    include_web: bool,
) -> dict:
    def asset(name: str) -> str:
        return f"{prefix}/{name}" if prefix != "." else f"./{name}"

    fragment: dict = {
        "icon": asset("icon.png"),
        "ios": {"icon": asset("icon.png")},
        "android": {
            "icon": asset("icon.png"),
            "adaptiveIcon": {
                "backgroundColor": color,
                "foregroundImage": asset("android-icon-foreground.png"),
                "monochromeImage": asset("android-icon-monochrome.png"),
            },
        },
    }
    if include_web:
        fragment["web"] = {"favicon": asset("favicon.png")}
    if include_splash:
        fragment["plugins"] = [
            [
                "expo-splash-screen",
                {
                    "backgroundColor": splash_color,
                    "image": asset("splash-icon.png"),
                    "imageWidth": splash_width,
                },
            ]
        ]
    return fragment


def load_config(app_json: Path | None) -> dict | None:
    if app_json is None:
        return None
    if not app_json.is_file():
        raise ValueError(f"missing app config: {app_json}")
    data = json.loads(app_json.read_text())
    expo = data.get("expo")
    if not isinstance(expo, dict):
        raise ValueError("app.json must contain an expo object")
    adaptive = expo.get("android", {}).get("adaptiveIcon", {})
    if "backgroundImage" in adaptive:
        raise ValueError(
            "existing adaptiveIcon.backgroundImage needs a design decision; "
            "remove or update it manually before applying backgroundColor"
        )
    return data


def merge_config(data: dict, fragment: dict) -> dict:
    expo = data["expo"]
    expo["icon"] = fragment["icon"]
    expo.setdefault("ios", {})["icon"] = fragment["ios"]["icon"]

    android = expo.setdefault("android", {})
    android["icon"] = fragment["android"]["icon"]
    android.setdefault("adaptiveIcon", {}).update(fragment["android"]["adaptiveIcon"])

    if "web" in fragment:
        expo.setdefault("web", {})["favicon"] = fragment["web"]["favicon"]

    if "plugins" in fragment:
        replacement = fragment["plugins"][0]
        plugins = expo.setdefault("plugins", [])
        for plugin in plugins:
            name = plugin if isinstance(plugin, str) else plugin[0] if plugin else None
            if name != "expo-splash-screen":
                continue
            if isinstance(plugin, str):
                plugins[plugins.index(plugin)] = replacement
            else:
                settings = plugin[1] if len(plugin) > 1 and isinstance(plugin[1], dict) else {}
                settings.update(replacement[1])
                plugin[:] = ["expo-splash-screen", settings]
            break
        else:
            plugins.append(replacement)
    return data


def main() -> int:
    args = parse_args()
    color = normalize_hex(args.background_color)
    splash_color = normalize_hex(args.splash_background_color or color)
    if not (0.1 <= args.safe_ratio <= 1.0):
        raise ValueError("--safe-ratio must be between 0.1 and 1.0")
    if args.splash_mark and not args.include_splash:
        raise ValueError("--splash-mark requires --include-splash")

    master = load_image(args.icon_master)
    mark = load_image(args.mark)
    monochrome_mark = load_image(args.monochrome_mark) if args.monochrome_mark else mark
    splash_mark = load_image(args.splash_mark) if args.splash_mark else mark
    if master.width != master.height or master.width < CANVAS:
        raise ValueError("icon master must be square and at least 1024x1024")
    if master.convert("RGBA").getchannel("A").getextrema()[0] != 255:
        raise ValueError("icon master must be fully opaque")

    prefix = args.config_prefix.rstrip("/")
    if args.app_json:
        try:
            relative = args.output_dir.resolve().relative_to(args.app_json.resolve().parent)
        except ValueError as exc:
            raise ValueError("--output-dir must be inside the app.json directory") from exc
        prefix = f"./{relative.as_posix()}" if relative.parts else "."

    config = load_config(args.app_json)
    fragment = config_fragment(
        prefix,
        color,
        splash_color,
        args.splash_image_width,
        args.include_splash,
        args.include_web,
    )

    outputs = [
        "icon.png",
        "android-icon-foreground.png",
        "android-icon-monochrome.png",
    ]
    if args.include_splash:
        outputs.append("splash-icon.png")
    if args.include_web:
        outputs.append("favicon.png")

    collisions = [
        name
        for name in outputs
        if (args.output_dir / name).exists()
    ]
    report = {"assets": outputs, "collisions": collisions, "expo": fragment}
    print(json.dumps(report, indent=2))
    if args.dry_run:
        return 0
    if collisions and not args.force:
        raise ValueError(
            "refusing to overwrite existing assets without --force: "
            + ", ".join(collisions)
        )

    args.output_dir.mkdir(parents=True, exist_ok=True)

    master_rgba = master.convert("RGBA")
    master_rgba.thumbnail((CANVAS, CANVAS), Image.Resampling.LANCZOS)
    icon = master_rgba.convert("RGB")
    icon.save(args.output_dir / "icon.png", optimize=True)

    foreground = contain_mark(mark, args.safe_ratio)
    foreground.save(args.output_dir / "android-icon-foreground.png", optimize=True)
    monochrome_layer(monochrome_mark, args.safe_ratio).save(
        args.output_dir / "android-icon-monochrome.png", optimize=True
    )

    if args.include_splash:
        contain_mark(splash_mark, 1.0).save(
            args.output_dir / "splash-icon.png", optimize=True
        )
    if args.include_web:
        icon.resize((48, 48), Image.Resampling.LANCZOS).save(
            args.output_dir / "favicon.png", optimize=True
        )

    if args.app_json and config is not None:
        merged = merge_config(config, fragment)
        args.app_json.write_text(json.dumps(merged, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
