#!/usr/bin/env python3
"""build_cover.py — inject cover data + brand assets into the dark cover
template and emit FOUR aspect ratios (16:9, 9:16, 4:3, 3:4).

Usage:
  uv run python scripts/build_cover.py --script dist/script.json --out dist/cover

Produces (per ratio, <W>x<H>):
  dist/cover/cover_16x9.html  (+ PNG later via render_cover.py)
  dist/cover/cover_9x16.html
  dist/cover/cover_4x3.html
  dist/cover/cover_3x4.html
  dist/cover/logos/lc.svg     bundled brand mark
  dist/cover/manifest.json    ratio -> dimensions map for the renderer
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent

RATIOS = {
    "16x9": (1920, 1080),
    "9x16": (1080, 1920),
    "4x3": (1440, 1080),
    "3x4": (1080, 1440),
}

# Accent gradient stops (default quant theme); overridable via meta.theme.
DEFAULT_ACCENT = ["#6366F1", "#8B5CF6", "#06B6D4"]


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
    p = argparse.ArgumentParser(description="Build branded cover HTML (4 ratios)")
    p.add_argument("--script", default="dist/script.json")
    p.add_argument("--lang", default="zh", choices=["zh", "en"])
    p.add_argument("--out", default="dist/cover")
    args = p.parse_args()

    script_path = Path(args.script)
    out_dir = Path(args.out)
    if not script_path.exists():
        die(f"missing script: {script_path}")

    script = json.loads(script_path.read_text(encoding="utf-8"))
    meta = script.get("meta", {})
    lang = args.lang

    # Pick the cover block for the requested language.
    if lang == "en":
        cover = script.get("coverEn") or {}
        if not cover.get("title"):
            sys.stderr.write("! coverEn[] missing — falling back to cover[] for EN covers\n")
            cover = script.get("cover", {})
    else:
        cover = script.get("cover", {})
    if not cover.get("title"):
        die("script.json missing cover.title (or coverEn.title)")

    # Bundle logo
    logo_src = SKILL_ROOT / "assets" / "logos" / "lc.svg"
    if not logo_src.exists():
        die(f"missing bundled logo: {logo_src}")
    (out_dir / "logos").mkdir(parents=True, exist_ok=True)
    shutil.copyfile(logo_src, out_dir / "logos" / "lc.svg")

    template_path = SKILL_ROOT / "assets" / "templates" / "tpl_cover.html"
    if not template_path.exists():
        die(f"missing template: {template_path}")
    template = template_path.read_text(encoding="utf-8")

    kicker = esc(cover.get("kicker") or meta.get("kicker") or "TECH BRIEF")
    # title may carry explicit \n line breaks — preserve as <br> in HTML
    title_raw = cover.get("title") or ""
    title = esc(title_raw).replace("\\n", "<br>")
    subtitle_raw = cover.get("subtitle") or meta.get("subtitle") or ""
    subtitle = esc(subtitle_raw).replace("\\n", "<br>")
    brand = esc(meta.get("brand") or "LongCipher")
    html_lang = esc(lang)
    date_str = meta.get("date") or ""
    # The issue number (e.g. "NO.028") was shown in the corner tag and meta row
    # but the user found it meaningless — drop it and surface the date instead.
    raw_corner = meta.get("cornerTag") or cover.get("cornerTag") or ""
    corner_tag = esc(date_str or "DAILY INTEL") if (not raw_corner or raw_corner.strip().upper().startswith("NO.")) else esc(raw_corner)
    # headlines label is data-driven (never hard-coded in the template); the
    # skill ships a neutral default so any article/topic renders without edits.
    headlines_label = esc(meta.get("headlinesLabel") or cover.get("headlinesLabel") or ("今日重点" if lang == "zh" else "TODAY'S FOCUS"))
    meta_left = esc(meta.get("metaLeft") or cover.get("metaLeft") or f"{brand} · {kicker}")
    raw_meta_right = meta.get("metaRight") or cover.get("metaRight") or ""
    meta_right = esc(date_str or kicker) if (not raw_meta_right or raw_meta_right.strip().lower().startswith("no.")) else esc(raw_meta_right)

    # 今日重点事件清单(增加封面信息量)——从 cover.headlines 读取,渲染为 <li> 列表。
    headlines = cover.get("headlines") or []
    if isinstance(headlines, list) and headlines:
        headlines_html = "\n".join(
            f'            <li><span class="hl-idx">›</span><span class="hl-txt">{esc(h)}</span></li>'
            for h in headlines
        )
    else:
        headlines_html = ""

    manifest: dict = {"ratios": {}}
    for name, (w, h) in RATIOS.items():
        scale = min(w, h) / 1080.0
        html = (
            template.replace("{{LANG}}", html_lang)
            .replace("{{WIDTH}}", str(w))
            .replace("{{HEIGHT}}", str(h))
            .replace("{{KICKER}}", kicker)
            .replace("{{TITLE}}", title)
            .replace("{{SUBTITLE}}", subtitle)
            .replace("{{HEADLINES}}", headlines_html)
            .replace("{{META_LEFT}}", meta_left)
            .replace("{{META_RIGHT}}", meta_right)
            .replace("{{CORNER_TAG}}", corner_tag)
            .replace("{{HEADLINES_LABEL}}", headlines_label)
            .replace("{{LOGO}}", "logos/lc.svg")
            .replace("--scale: 1;", f"--scale: {scale:.4f};")
        )
        # inject the scale var on :root
        html = html.replace(":root {", f":root {{ --scale: {scale:.4f};", 1)
        # make sure any un-substituted label placeholder falls back gracefully
        html = html.replace("{{HEADLINES_LABEL}}", headlines_label)
        out_file = out_dir / f"cover_{name}.html"
        out_file.write_text(html, encoding="utf-8")
        manifest["ratios"][name] = {"width": w, "height": h, "html": out_file.name}

    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    # HyperFrames project config so render_cover.py can resolve the composition.
    hyperframes_json = (
        '{\n'
        '  "$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",\n'
        '  "paths": { "assets": "assets" }\n'
        '}\n'
    )
    (out_dir / "hyperframes.json").write_text(hyperframes_json, encoding="utf-8")

    sys.stdout.write(
        f"✓ covers written ({len(RATIOS)} ratios) to {out_dir}\n"
        f"  cover_16x9 / 9x16 / 4x3 / 3x4 .html + manifest.json + logos/lc.svg\n"
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
