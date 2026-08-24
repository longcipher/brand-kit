#!/usr/bin/env python3
"""build_shorts.py — assemble the vertical 9:16 "shorts" composition from
script.json.

Strategy (fixed-template, JSON-only authoring):
  - The LLM writes structured JSON only (cover + slides[]).
  - This script builds a STATIC hero cover (visible at t=0, like the landscape
    video's cover slide) from the cover block, then a scrolling feed of ALL
    categories (one section per keypoint slide) with curated key bullets.
  - Shorts are short vertical reels (10s default) over a fixed BGM.

Usage:
  uv run python scripts/build_shorts.py --script dist/script.json \
      --lang zh --out dist/shorts_zh
  uv run python scripts/build_shorts.py --script dist/script.json \
      --lang en --out dist/shorts_en

Produces:
  dist/shorts_<lang>/index.html         (HyperFrames composition)
  dist/shorts_<lang>/hyperframes.json
  dist/shorts_<lang>/logos/lc.svg       (branded logo)
  dist/shorts_<lang>/audio/shorts_bgm.mp3 (fixed BGM)
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

HYPERFRAMES_JSON = '{\n  "$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",\n  "paths": { "assets": "assets" }\n}\n'

TEMPLATE = "assets/templates/shorts.html"
SKILL_ROOT = Path(__file__).resolve().parent.parent

# Fixed cute-illustration catalog — must match `ICONS` in shorts.html /
# dashboard.html. The LLM picks a key; the template owns the actual SVG art.
ICON_KEYS = [
    "shield", "rocket", "chart", "coins", "cube", "atom", "bolt",
    "net", "lock", "spark", "pick", "scale", "bot", "bank", "handshake",
]

DEFAULT_DURATION = 10.0
# Per-category: how many key bullets to surface in the feed.
DEFAULT_BULLETS = 3

# Duration is derived from content volume so the whole feed scrolls fully
# (never truncated). Capped at MAX_DURATION; the user is fine with up to 60s.
HERO_HOLD = 0.8        # time the hero cover stays before the feed starts
TAIL = 2.0             # dwell time after the last category before fade-out
CAT_BASE = 1.0         # seconds per category (structure)
CAT_BULLET = 0.4       # extra seconds per bullet line
MIN_DURATION = 12.0
MAX_DURATION = 60.0


def die(msg: str) -> None:
    sys.stderr.write(f"✗ {msg}\n")
    sys.exit(1)


def _pick(script: dict, key: str, lang: str):
    if lang == "en":
        val = script.get(key + "En")
        if val is None:
            sys.stderr.write(f"! {key}En missing — falling back to {key} for shorts\n")
            val = script.get(key)
        return val
    return script.get(key)


def _esc(s: str) -> str:
    return (
        str(s if s is not None else "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def main() -> None:
    p = argparse.ArgumentParser(description="Build the vertical shorts composition")
    p.add_argument("--script", default="dist/script.json")
    p.add_argument("--lang", default="zh", choices=["zh", "en"])
    p.add_argument("--out", default=None,
                   help="output dir (default: dist/shorts_zh or dist/shorts_en)")
    p.add_argument("--duration", default=DEFAULT_DURATION, type=float,
                   help="shorts duration in seconds (default 10.0)")
    p.add_argument("--bullets", default=DEFAULT_BULLETS, type=int,
                   help="key bullets per category section (default 3)")
    args = p.parse_args()

    lang = args.lang
    script_path = Path(args.script)
    if not script_path.exists():
        die(f"missing script: {script_path}")

    out_dir = Path(args.out) if args.out else Path(f"dist/shorts_{lang}")
    out_dir.mkdir(parents=True, exist_ok=True)

    script = json.loads(script_path.read_text(encoding="utf-8"))
    meta = script.get("meta", {})
    cover = _pick(script, "cover", lang) or {}

    title = (cover.get("title") or meta.get("title") or "").strip()
    subtitle = (cover.get("subtitle") or meta.get("subtitle") or "").strip()
    kicker = (
        cover.get("kicker")
        or meta.get("kicker")
        or ("每日精选" if lang == "zh" else "TODAY'S FOCUS")
    )
    feed_label = (
        cover.get("headlinesLabel")
        or meta.get("headlinesLabel")
        or ("今日重点" if lang == "zh" else "TODAY'S FOCUS")
    )
    sections_label = (
        cover.get("sectionsLabel")
        or meta.get("sectionsLabel")
        or ("要点速览" if lang == "zh" else "KEY TAKEAWAYS")
    )
    date = meta.get("date") or ""

    hero_headlines = [h for h in (cover.get("headlines") or [])[:4] if h]

    # Build one category section per keypoint / three_points slide. Outro is
    # skipped (it's the wrap-up, not a category). Pick top-N bullets.
    slides = _pick(script, "slides", lang) or []
    categories: list[dict] = []
    for s in slides:
        t = s.get("type")
        if t == "outro":
            continue
        if t == "keypoint":
            eyebrow = s.get("eyebrow") or feed_label
            statement = s.get("statement") or ""
            bullets = [b for b in (s.get("bullets") or [])[: args.bullets] if b]
        elif t == "three_points":
            eyebrow = (s.get("title") or feed_label)
            statement = s.get("title") or ""
            bullets = [
                (p.get("title") or "") + ((" — " + p.get("body")) if p.get("body") else "")
                for p in (s.get("points") or [])
            ]
            bullets = [b for b in bullets if b][: args.bullets]
        elif t == "table":
            eyebrow = s.get("title") or feed_label
            statement = s.get("title") or ""
            bullets = []
            for row in (s.get("rows") or [])[: args.bullets]:
                if isinstance(row, list) and row:
                    bullets.append("  ".join(str(c) for c in row))
        else:
            continue
        if not statement and not bullets:
            continue
        categories.append({
            "eyebrow": eyebrow,
            "statement": statement,
            "bullets": bullets,
            "icon": s.get("icon") if s.get("icon") in ICON_KEYS else None,
            "analysis": s.get("analysis"),
        })

    if not categories:
        die("script.json has no category slides to render in the shorts feed")

    # Derive duration from content volume so every category scrolls fully into
    # view (no truncation). Falls back to --duration only when explicitly set.
    per_cat = CAT_BASE + sum(len(c["bullets"]) for c in categories) / max(len(categories), 1) * CAT_BULLET
    computed_duration = HERO_HOLD + len(categories) * per_cat + TAIL
    computed_duration = max(MIN_DURATION, min(MAX_DURATION, computed_duration))
    if abs(args.duration - DEFAULT_DURATION) > 1e-6:
        # user explicitly overrode -> honor it (still capped)
        duration = max(MIN_DURATION, min(MAX_DURATION, args.duration))
    else:
        duration = computed_duration

    data = {
        "lang": lang,
        "heroHeadlines": hero_headlines,
        "categories": categories,
    }
    data_json = json.dumps(data, ensure_ascii=False)

    template_path = SKILL_ROOT / TEMPLATE
    if not template_path.exists():
        die(f"missing template: {template_path}")
    html = template_path.read_text(encoding="utf-8")

    icons_path = SKILL_ROOT / "assets" / "templates" / "_icons.js"
    icons_js = icons_path.read_text(encoding="utf-8") if icons_path.exists() else "var ICONS = {};"
    html = html.replace("{{ICONS_JS}}", icons_js)

    html = html.replace("{{LANG}}", lang)
    html = html.replace("{{DURATION}}", f"{duration:.2f}")
    html = html.replace("{{TITLE}}", _esc(title).replace("\\n", "<br>"))
    html = html.replace("{{SUBTITLE}}", _esc(subtitle).replace("\\n", "<br>"))
    html = html.replace("{{KICKER}}", _esc(kicker))
    html = html.replace("{{HEADLINES_LABEL}}", _esc(feed_label))
    html = html.replace("{{SECTIONS_LABEL}}", _esc(sections_label))
    html = html.replace("{{DATE}}", _esc(date))
    html = html.replace("{{DATA}}", data_json)

    (out_dir / "index.html").write_text(html, encoding="utf-8")
    (out_dir / "hyperframes.json").write_text(HYPERFRAMES_JSON, encoding="utf-8")

    logo_src = SKILL_ROOT / "assets" / "logos" / "lc.svg"
    if logo_src.exists():
        (out_dir / "logos").mkdir(parents=True, exist_ok=True)
        shutil.copyfile(logo_src, out_dir / "logos" / "lc.svg")
    else:
        sys.stderr.write(f"! brand logo missing: {logo_src}\n")

    # Vendor GSAP locally so shorts rendering never depends on CDN reachability.
    vendor_src = SKILL_ROOT / "assets" / "vendor" / "gsap.min.js"
    if vendor_src.exists():
        vdst = out_dir / "assets" / "vendor"
        vdst.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(vendor_src, vdst / "gsap.min.js")

    # Self-hosted brand fonts — no Google Fonts CDN dependency at render time.
    fonts_src = SKILL_ROOT / "assets" / "fonts"
    if fonts_src.is_dir():
        fdst = out_dir / "assets" / "fonts"
        fdst.mkdir(parents=True, exist_ok=True)
        for woff in sorted(fonts_src.glob("*.woff2")):
            shutil.copyfile(woff, fdst / woff.name)

    bgm_src = SKILL_ROOT / "assets" / "audio" / "shorts_bgm.mp3"
    # Regenerate the BGM to match the derived duration so the audio slot
    # (data-duration) and the actual file length line up — otherwise the
    # renderer silently truncates audio to the file length and the tail is
    # silent. The synth loops the 5-bar progression, so any duration <= 60s
    # is a valid loop.
    #
    # IMPORTANT: the synthesized file is written into the PROJECT dir
    # (dist/shorts_<lang>/audio/shorts_bgm.mp3), NEVER back to the skill source
    # assets/audio/shorts_bgm.mp3. The source is the canonical 10s loop and is
    # committed to Git; the per-build duration variant is a build artifact
    # (dist/ is gitignored), so we must not mutate the tracked source each run.
    bgm_out = out_dir / "audio" / "shorts_bgm.mp3"
    (out_dir / "audio").mkdir(parents=True, exist_ok=True)
    try:
        res = subprocess.run(
            [sys.executable, str(SKILL_ROOT / "scripts" / "make_shorts_bgm.py"),
             "--out", str(bgm_out), "--duration", f"{duration:.2f}"],
            capture_output=True, text=True,
        )
        if res.returncode != 0:
            sys.stderr.write(f"! BGM synth failed: {res.stderr}\n")
            # fall back to the canonical source copy
            if bgm_src.exists():
                shutil.copyfile(bgm_src, bgm_out)
    except FileNotFoundError as e:
        sys.stderr.write(f"! cannot invoke make_shorts_bgm.py: {e}\n")
        if bgm_src.exists():
            shutil.copyfile(bgm_src, bgm_out)
    if not bgm_out.exists():
        sys.stderr.write(f"! shorts BGM missing: {bgm_src} (run make_shorts_bgm.py)\n")

    sys.stdout.write(
        f"✓ shorts composition written (lang={lang}): {out_dir / 'index.html'} "
        f"({len(categories)} categories, {len(hero_headlines)} hero headlines, {duration:.2f}s)\n"
        f"  Next: render via `render_video.py --project {out_dir} --output output/shorts_{lang}.mp4`\n"
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
