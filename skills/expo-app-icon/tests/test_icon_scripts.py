#!/usr/bin/env python3

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw


SKILL_DIR = Path(__file__).resolve().parents[1]
PREPARE = SKILL_DIR / "scripts" / "prepare_expo_icon_assets.py"
VALIDATE = SKILL_DIR / "scripts" / "validate_expo_icon_assets.py"


class IconScriptsTest(unittest.TestCase):
    def test_generates_assets_and_preserves_unrelated_config(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            master = root / "master.png"
            mark = root / "mark.png"
            monochrome_mark = root / "monochrome.png"
            app_json = root / "app.json"
            output = root / "assets" / "images"

            Image.new("RGB", (1200, 1200), "#203040").save(master)
            mark_image = Image.new("RGBA", (800, 600), (0, 0, 0, 0))
            ImageDraw.Draw(mark_image).ellipse((100, 50, 700, 550), fill="#F4C95D")
            mark_image.save(mark)
            monochrome_image = Image.new("RGBA", (800, 600), (0, 0, 0, 0))
            ImageDraw.Draw(monochrome_image).rectangle(
                (200, 100, 600, 500), fill="white"
            )
            monochrome_image.save(monochrome_mark)
            app_json.write_text(
                json.dumps(
                    {
                        "expo": {
                            "name": "Test",
                            "plugins": [
                                "expo-router",
                                ["other-plugin", {"keep": True}],
                                [
                                    "expo-splash-screen",
                                    {
                                        "resizeMode": "cover",
                                        "dark": {"image": "./dark-splash.png"},
                                    },
                                ],
                            ],
                            "android": {"package": "com.example.test"},
                        }
                    }
                )
            )

            subprocess.run(
                [
                    "python3",
                    str(PREPARE),
                    "--icon-master",
                    str(master),
                    "--mark",
                    str(mark),
                    "--monochrome-mark",
                    str(monochrome_mark),
                    "--output-dir",
                    str(output),
                    "--background-color",
                    "#203040",
                    "--app-json",
                    str(app_json),
                    "--include-splash",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                [
                    "python3",
                    str(VALIDATE),
                    "--assets-dir",
                    str(output),
                    "--app-json",
                    str(app_json),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            config = json.loads(app_json.read_text())["expo"]
            self.assertEqual(config["name"], "Test")
            self.assertEqual(config["android"]["package"], "com.example.test")
            self.assertIn("expo-router", config["plugins"])
            self.assertIn(["other-plugin", {"keep": True}], config["plugins"])
            with Image.open(master) as source:
                self.assertEqual(source.size, (1200, 1200))
            splash = next(
                plugin
                for plugin in config["plugins"]
                if isinstance(plugin, list) and plugin[0] == "expo-splash-screen"
            )
            self.assertEqual(splash[1]["resizeMode"], "cover")
            self.assertEqual(splash[1]["dark"]["image"], "./dark-splash.png")
            self.assertNotEqual(
                Image.open(output / "android-icon-foreground.png")
                .convert("RGBA")
                .getchannel("A")
                .getbbox(),
                Image.open(output / "android-icon-monochrome.png")
                .convert("RGBA")
                .getchannel("A")
                .getbbox(),
            )

    def test_dry_run_writes_nothing_and_prints_requested_prefix(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            master = root / "master.png"
            mark = root / "mark.png"
            output = root / "generated"
            Image.new("RGB", (1024, 1024), "navy").save(master)
            Image.new("RGBA", (1024, 1024), (255, 255, 255, 128)).save(mark)

            result = subprocess.run(
                [
                    "python3",
                    str(PREPARE),
                    "--icon-master",
                    str(master),
                    "--mark",
                    str(mark),
                    "--output-dir",
                    str(output),
                    "--background-color",
                    "#000080",
                    "--config-prefix",
                    "./branding",
                    "--dry-run",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            report = json.loads(result.stdout)
            self.assertEqual(report["expo"]["icon"], "./branding/icon.png")
            self.assertNotIn("plugins", report["expo"])
            self.assertNotIn("web", report["expo"])
            self.assertFalse(output.exists())

    def test_refuses_asset_collisions_without_force(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            master = root / "master.png"
            mark = root / "mark.png"
            output = root / "assets"
            output.mkdir()
            Image.new("RGB", (1024, 1024), "navy").save(master)
            Image.new("RGBA", (1024, 1024), (255, 255, 255, 128)).save(mark)
            Image.new("RGB", (1024, 1024), "red").save(output / "icon.png")

            result = subprocess.run(
                [
                    "python3",
                    str(PREPARE),
                    "--icon-master",
                    str(master),
                    "--mark",
                    str(mark),
                    "--output-dir",
                    str(output),
                    "--background-color",
                    "#000080",
                ],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("refusing to overwrite", result.stderr)

    def test_rejects_ambiguous_existing_adaptive_background(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            master = root / "master.png"
            mark = root / "mark.png"
            app_json = root / "app.json"
            Image.new("RGB", (1024, 1024), "navy").save(master)
            Image.new("RGBA", (1024, 1024), (255, 255, 255, 128)).save(mark)
            app_json.write_text(
                json.dumps(
                    {
                        "expo": {
                            "android": {
                                "adaptiveIcon": {
                                    "backgroundImage": "./existing-background.png"
                                }
                            }
                        }
                    }
                )
            )

            result = subprocess.run(
                [
                    "python3",
                    str(PREPARE),
                    "--icon-master",
                    str(master),
                    "--mark",
                    str(mark),
                    "--output-dir",
                    str(root / "assets"),
                    "--background-color",
                    "#000080",
                    "--app-json",
                    str(app_json),
                ],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("needs a design decision", result.stderr)


if __name__ == "__main__":
    unittest.main()
