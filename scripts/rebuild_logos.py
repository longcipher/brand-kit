#!/usr/bin/env python3
"""Rebuild LongCipher logo variants with:
- unified light fill #FAFAF9 (negative space; reads as gap on light, bright on dark)
- wordmark/slogan as DM Sans path outlines (no system-font dependency)
- lockup blue documented as brand-blue #0a72ef
- explicit width/height + viewBox (no CLS as <img>)
- a11y: role=img + <title>

Run:  uv run --with fonttools --with brotli python scripts/rebuild_logos.py
"""
from __future__ import annotations

import re
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.misc.transform import Transform

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "skills" / "lc-tech-publisher" / "assets" / "fonts"

# Brand tokens (must match DESIGN.md)
LIGHT = "#FAFAF9"
DARK = "#2A2A2A"
RED = "#FF0000"
GREEN = "#08C477"
WORDMARK = "#0a72ef"  # single brand accent — replaces undocumented #165DFF
SLOGAN_OPACITY = "0.72"

# The mark geometry lives in lc.svg as five colored paths + one light base path.
MARK_PATHS = {
    LIGHT: None,  # filled in from source
    RED: [],
    DARK: [],
    GREEN: [],
}

CLIP_POLY = "511.5,184.5 796,364 796,674 512.5,843 228,674.5 228,352.5"


def load_mark_geometry() -> dict[str, list[str]]:
    src = (ROOT / "lc.svg").read_text(encoding="utf-8")
    paths: dict[str, list[str]] = {LIGHT: [], RED: [], DARK: [], GREEN: []}
    for m in re.finditer(r'<path fill="(#[0-9A-Fa-f]{6})" d="([^"]+)"', src):
        color = m.group(1).upper()
        d = m.group(2)
        # Normalize to brand token colors
        if color in ("#FAFAF9", "#E6E6E6"):
            paths[LIGHT].append(d)
        elif color == "#FF0000":
            paths[RED].append(d)
        elif color == "#2A2A2A":
            paths[DARK].append(d)
        elif color == "#08C477":
            paths[GREEN].append(d)
        else:
            raise SystemExit(f"unexpected mark color: {color}")
    assert paths[LIGHT] and paths[RED] and paths[DARK] and paths[GREEN], paths.keys()
    return paths


def load_font(name: str) -> TTFont:
    return TTFont(FONTS / name)


def glyph_paths(
    font: TTFont,
    text: str,
    *,
    size: float,
    tracking: float = 0.0,
    x: float = 0.0,
    y: float = 0.0,
) -> tuple[str, float]:
    """Render `text` to a single SVG path `d`. Returns (d, advance_width).

    `tracking` is extra advance per glyph, in the same units as `size`
    (i.e. em-fraction * size). `y` is the baseline.
    """
    glyph_set = font.getGlyphSet()
    cmap = font.getBestCmap()
    hmtx = font["hmtx"]
    upem = font["head"].unitsPerEm
    scale = size / upem

    d_parts: list[str] = []
    cursor = x
    for ch in text:
        if ch == " ":
            # word space: prefer the font's space advance
            gname = cmap.get(ord(" "))
            adv = hmtx[gname][0] if gname else int(upem * 0.28)
            cursor += adv * scale + tracking
            continue
        gname = cmap.get(ord(ch))
        if gname is None:
            raise SystemExit(f"font has no glyph for {ch!r}")
        pen = SVGPathPen(glyph_set, ntos=lambda v: f"{v:.2f}".rstrip("0").rstrip("."))
        # y-up font coords → SVG y-down
        tp = TransformPen(pen, Transform(scale, 0, 0, -scale, cursor, y))
        glyph_set[gname].draw(tp)
        seg = pen.getCommands()
        if seg:
            d_parts.append(seg)
        adv = hmtx[gname][0]
        cursor += adv * scale + tracking
    # trailing tracking is not part of the advance
    return " ".join(d_parts), cursor - tracking


def svg_open(width: int, height: int, title: str, clip_id: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="{clip_id}-title">\n'
        f'  <title id="{clip_id}-title">{title}</title>\n'
        f"  <defs>\n"
        f'    <clipPath id="{clip_id}">\n'
        f'      <polygon points="{CLIP_POLY}"/>\n'
        f"    </clipPath>\n"
        f"  </defs>\n"
    )


def build_pure(paths: dict[str, list[str]]) -> str:
    """lc.svg — pure mark, 1:1, no text. Primary asset."""
    cid = "lc-clip"
    parts = [svg_open(1024, 1024, "LongCipher mark", cid)]
    parts.append(f'  <g clip-path="url(#{cid})">')
    for color in (LIGHT, RED, DARK, GREEN):
        for d in paths[color]:
            parts.append(f'    <path fill="{color}" d="{d}"/>')
    parts.append("  </g>")
    parts.append("</svg>\n")
    return "\n".join(parts)


def build_lc11(paths: dict[str, list[str]]) -> str:
    """1:1 mark + wordmark below. Wordmark DM Sans 700, tracking -0.02em."""
    cid = "lc11-clip"
    # mark scaled to 0.9, centered upper area (matches prior layout)
    tf = "translate(512, 420) scale(0.9) translate(-512, -513)"
    size = 96.0
    tracking = -0.02 * size
    # baseline y=880, centered on 512
    # recompute path with centered x
    font = load_font("dm-sans-latin-700-normal.woff2")
    # measure first (x=0) to center, then place on baseline
    _d0, adv0 = glyph_paths(font, "LongCipher", size=size, tracking=tracking, x=0, y=0)
    start_x = 512 - (adv0 - tracking) / 2
    d, _adv = glyph_paths(font, "LongCipher", size=size, tracking=tracking, x=start_x, y=880)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1024" '
        f'viewBox="0 0 1024 1024" role="img" aria-labelledby="lc11-title">',
        f'  <title id="lc11-title">LongCipher logo with wordmark</title>',
        f"  <defs>",
        f'    <clipPath id="{cid}">',
        f'      <polygon points="{CLIP_POLY}"/>',
        f"    </clipPath>",
        f"  </defs>",
        f'  <g transform="{tf}">',
        f'    <g clip-path="url(#{cid})">',
    ]
    for color in (LIGHT, RED, DARK, GREEN):
        for p in paths[color]:
            parts.append(f'      <path fill="{color}" d="{p}"/>')
    parts += [
        "    </g>",
        "  </g>",
        f'  <path fill="{WORDMARK}" d="{d}"/>',
        "</svg>",
        "",
    ]
    return "\n".join(parts)


def build_horizontal(
    paths: dict[str, list[str]],
    *,
    width: int,
    height: int,
    cid: str,
    title: str,
    mark_tf: str,
    word_size: float,
    word_x: float,
    word_y: float,
    word_tracking_em: float,
    slogan_size: float | None = None,
    slogan_x: float = 0,
    slogan_y: float = 0,
    slogan_tracking_em: float = 0.28,
    filename_hint: str = "",
) -> str:
    font700 = load_font("dm-sans-latin-700-normal.woff2")
    wt = word_tracking_em * word_size
    word_d, word_adv = glyph_paths(
        font700, "LongCipher", size=word_size, tracking=wt, x=word_x, y=word_y
    )
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="{cid}-title">',
        f'  <title id="{cid}-title">{title}</title>',
        f"  <defs>",
        f'    <clipPath id="{cid}">',
        f'      <polygon points="{CLIP_POLY}"/>',
        f"    </clipPath>",
        f"  </defs>",
        f'  <g transform="{mark_tf}">',
        f'    <g clip-path="url(#{cid})">',
    ]
    for color in (LIGHT, RED, DARK, GREEN):
        for p in paths[color]:
            parts.append(f'      <path fill="{color}" d="{p}"/>')
    parts += ["    </g>", "  </g>", f'  <path fill="{WORDMARK}" d="{word_d}"/>']

    if slogan_size:
        # slogan in DM Sans 500, uppercase tracking (path outlines + manual tracking)
        font500 = load_font("dm-sans-latin-500-normal.woff2")
        st = slogan_tracking_em * slogan_size
        slogan_d, _ = glyph_paths(
            font500,
            "AI NATIVE PAYMENT AND TRADING",
            size=slogan_size,
            tracking=st,
            x=slogan_x,
            y=slogan_y,
        )
        parts.append(
            f'  <path fill="{WORDMARK}" fill-opacity="{SLOGAN_OPACITY}" d="{slogan_d}"/>'
        )
    parts += ["</svg>", ""]
    return "\n".join(parts)


def main() -> None:
    paths = load_mark_geometry()
    print(f"mark paths: light={len(paths[LIGHT])} red={len(paths[RED])} "
          f"dark={len(paths[DARK])} green={len(paths[GREEN])}")

    font700 = load_font("dm-sans-latin-700-normal.woff2")

    # --- lc.svg ---
    (ROOT / "lc.svg").write_text(build_pure(paths), encoding="utf-8")
    print("wrote lc.svg")

    # --- lc11.svg ---
    (ROOT / "lc11.svg").write_text(build_lc11(paths), encoding="utf-8")
    print("wrote lc11.svg")

    # --- lc31.svg  3:1 wordmark + slogan ---
    # Prior: viewBox 1800x600, mark translate(450,300) scale(0.6),
    #        word 150px @ (700, 310), slogan 34px @ (710, 390)
    lc31 = build_horizontal(
        paths,
        width=1800,
        height=600,
        cid="lc31-clip",
        title="LongCipher logo 3:1",
        mark_tf="translate(450, 300) scale(0.6) translate(-512, -513)",
        word_size=150,
        word_x=700,
        word_y=310,
        word_tracking_em=-0.02,
        slogan_size=34,
        slogan_x=710,
        slogan_y=390,
        slogan_tracking_em=0.28,
    )
    (ROOT / "lc31.svg").write_text(lc31, encoding="utf-8")
    print("wrote lc31.svg")

    # --- lc43.svg  4:3 ---
    lc43 = build_horizontal(
        paths,
        width=2400,
        height=1800,
        cid="lc43-clip",
        title="LongCipher logo 4:3",
        mark_tf="translate(550, 900) scale(0.95) translate(-512, -513)",
        word_size=200,
        word_x=920,
        word_y=930,
        word_tracking_em=-0.02,
        slogan_size=44,
        slogan_x=930,
        slogan_y=1050,
        slogan_tracking_em=0.28,
    )
    (ROOT / "lc43.svg").write_text(lc43, encoding="utf-8")
    print("wrote lc43.svg")

    # --- lc169.svg  16:9 ---
    lc169 = build_horizontal(
        paths,
        width=3200,
        height=1800,
        cid="lc169-clip",
        title="LongCipher logo 16:9",
        mark_tf="translate(750, 900) scale(1.1) translate(-512, -513)",
        word_size=240,
        word_x=1200,
        word_y=930,
        word_tracking_em=-0.02,
        slogan_size=52,
        slogan_x=1215,
        slogan_y=1070,
        slogan_tracking_em=0.3,
    )
    (ROOT / "lc169.svg").write_text(lc169, encoding="utf-8")
    print("wrote lc169.svg")

    # Keep the skill's bundled pure mark in sync
    skill_logo = ROOT / "skills" / "lc-tech-publisher" / "assets" / "logos" / "lc.svg"
    skill_logo.write_text((ROOT / "lc.svg").read_text(encoding="utf-8"), encoding="utf-8")
    print(f"synced {skill_logo.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
