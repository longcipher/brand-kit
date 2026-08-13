#!/usr/bin/env python3
"""build_cover.py — inject cover data + brand assets into the cover template.

Usage:
  uv run python scripts/build_cover.py --script dist/script.json --out dist/cover

Produces:
  dist/cover/cover.html        renderable cover composition (1s still)
  dist/cover/logos/lc.svg      bundled brand mark
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
HYPERFRAMES_JSON = '{\n  "$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",\n  "paths": { "assets": "assets" }\n}\n'


def die(msg: str) -> None:
    sys.stderr.write(f"✗ {msg}\n")
    sys.exit(1)


def esc(s) -> str:
    return (
        str(s if s is not None else "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def main() -> None:
    p = argparse.ArgumentParser(description="Build the branded cover HTML")
    p.add_argument("--script", default="dist/script.json")
    p.add_argument("--out", default="dist/cover")
    args = p.parse_args()

    script_path = Path(args.script)
    out_dir = Path(args.out)
    if not script_path.exists():
        die(f"missing script: {script_path}")

    script = json.loads(script_path.read_text(encoding="utf-8"))
    cover = script.get("cover", {})
    meta = script.get("meta", {})
    if not cover.get("title"):
        die("script.json missing cover.title")

    # Bundle logo
    logo_src = SKILL_ROOT / "assets" / "logos" / "lc.svg"
    if not logo_src.exists():
        die(f"missing bundled logo: {logo_src}")
    (out_dir / "logos").mkdir(parents=True, exist_ok=True)
    import shutil

    shutil.copyfile(logo_src, out_dir / "logos" / "lc.svg")

    # Read + inject template
    template_path = SKILL_ROOT / "assets" / "templates" / "cover.html"
    if not template_path.exists():
        die(f"missing template: {template_path}")
    html = template_path.read_text(encoding="utf-8")

    tokens = {
        "{{KICKER}}": esc(cover.get("kicker") or meta.get("kicker") or "TECH EXPLAINER"),
        "{{TITLE}}": esc(cover.get("title")),
        "{{SUBTITLE}}": esc(cover.get("subtitle") or meta.get("subtitle") or ""),
        "{{BRAND}}": esc(meta.get("brand") or "LongCipher"),
        "{{LOGO}}": "logos/lc.svg",
    }
    for k, v in tokens.items():
        html = html.replace(k, v)

    (out_dir / "cover.html").write_text(html, encoding="utf-8")
    (out_dir / "hyperframes.json").write_text(HYPERFRAMES_JSON, encoding="utf-8")

    sys.stdout.write(f"✓ cover written: {out_dir / 'cover.html'} (logos/lc.svg bundled)\n")
    sys.exit(0)


if __name__ == "__main__":
    main()
