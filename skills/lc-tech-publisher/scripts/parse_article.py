#!/usr/bin/env python3
"""parse_article.py — extract a raw outline from an article, and validate the
agent-authored dist/script.json against the skill schema.

Two modes:
  1. Outline extraction (Step 2):
       uv run python scripts/parse_article.py --input <article.md> --output dist/article.json
  2. Schema validation (Step 2 Gate):
       uv run python scripts/parse_article.py --validate dist/script.json

The outline is a *raw* skeleton — headings, code blocks, paragraphs. The agent
(LLM) uses it to author the final script.json: a two-speaker dialogue
(`podcast[]`) plus ordered visual slides (`slides[]` of type keypoint /
three_points / outro). The script is domain-agnostic — knowledge share or daily
digest. Visual styling lives entirely in the fixed component templates; the LLM
only emits structured JSON (no CSS).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path


def die(msg: str) -> None:
    sys.stderr.write(f"✗ {msg}\n")
    sys.exit(1)


def read(path: str) -> str:
    try:
        return Path(path).read_text(encoding="utf-8")
    except OSError as e:
        die(f"Cannot read {path}: {e}")


def warn(msg: str) -> None:
    sys.stderr.write(f"! {msg}\n")


def _validate_dialogue(podcast, key: str, errors: list[str]) -> None:
    if not isinstance(podcast, list) or not podcast:
        errors.append(f"{key}[] must be a non-empty array of dialogue turns")
        return
    valid_speakers = {"male", "female"}
    for i, t in enumerate(podcast):
        if not isinstance(t, dict):
            errors.append(f"{key}[{i}] must be an object")
            continue
        sp = t.get("speaker")
        if sp not in valid_speakers:
            errors.append(f"{key}[{i}].speaker must be 'male' or 'female' (got {sp!r})")
        if not t.get("text"):
            errors.append(f"{key}[{i}].text is required (the spoken line)")
        if t.get("voice") is not None and not isinstance(t.get("voice"), str):
            errors.append(f"{key}[{i}].voice must be a string if present")
        emo = t.get("emotion")
        if emo is not None and emo not in VALID_EMOTIONS:
            errors.append(
                f"{key}[{i}].emotion must be one of {sorted(VALID_EMOTIONS)} (got {emo!r})"
            )
        rate = t.get("rate")
        if rate is not None and not isinstance(rate, str):
            errors.append(f"{key}[{i}].rate must be an Edge-TTS rate string like '-4%'")


def _validate_ticker(ticker, key: str, errors: list[str]) -> None:
    # ticker is now optional (knowledge mode may omit it); kept for digest compatibility.
    if ticker is None:
        return
    if not isinstance(ticker, list):
        errors.append(f"{key} must be an array")
        return
    for i, it in enumerate(ticker):
        if not isinstance(it, dict) or not it.get("label"):
            errors.append(f"{key}[{i}] must be {{label, value?, change?, dir?}}")


VALID_SLIDE_TYPES = {"keypoint", "three_points", "outro", "table", "chart", "counter", "cards", "steps"}

# Fixed cute-illustration catalog (must match `ICONS` in dashboard.html /
# shorts.html). The LLM picks a key; unknown keys fall back to "spark".
VALID_ICONS = {
    "shield", "rocket", "chart", "coins", "cube", "atom", "bolt",
    "net", "lock", "spark", "pick", "scale", "bot", "bank", "handshake",
    "trend", "gauge", "layers", "flow",
}

# Emotional pacing catalog (must match `EMOTION_RATE` in generate_audio.py).
VALID_EMOTIONS = {
    "neutral", "calm", "serious", "curious", "excited", "surprised",
    "warm", "doubtful", "relieved", "emphatic",
}


def _validate_panels(slides, key: str, errors: list[str], warns: list[str]) -> None:
    """Validate the slides[] array (keypoint / three_points / outro / table)."""
    if not isinstance(slides, list) or not slides:
        errors.append(f"{key}[] must be a non-empty array of slide objects")
        return
    for i, s in enumerate(slides):
        if not isinstance(s, dict):
            errors.append(f"{key}[{i}] must be an object")
            continue
        stype = s.get("type")
        if stype not in VALID_SLIDE_TYPES:
            errors.append(f"{key}[{i}].type must be one of {sorted(VALID_SLIDE_TYPES)} (got {stype!r})")
            continue
        icon = s.get("icon")
        if icon is not None and icon not in VALID_ICONS:
            warns.append(f"{key}[{i}].icon '{icon}' unknown — falls back to 'spark'")
        if s.get("analysis") is not None and not isinstance(s.get("analysis"), str):
            errors.append(f"{key}[{i}].analysis must be a string (the so-what line)")
        cbs = s.get("callback")
        if cbs is not None:
            if isinstance(cbs, str):
                cbs = [cbs]
            elif not isinstance(cbs, list):
                errors.append(f"{key}[{i}].callback must be a string or array of strings")
                cbs = None
            if cbs is not None:
                for j, cb in enumerate(cbs):
                    if not isinstance(cb, str) or not cb:
                        errors.append(f"{key}[{i}].callback[{j}] must be a non-empty string")
        if stype == "keypoint":
            if not s.get("statement"):
                errors.append(f"{key}[{i}].statement is required for keypoint slides")
        elif stype == "three_points":
            pts = s.get("points")
            if not isinstance(pts, list) or len(pts) != 3:
                errors.append(f"{key}[{i}].points must be an array of exactly 3 for three_points")
            else:
                for j, p in enumerate(pts):
                    if not p.get("title") or not p.get("body"):
                        errors.append(f"{key}[{i}].points[{j}] needs title + body")
        elif stype == "table":
            if not isinstance(s.get("head"), list) or not s.get("head"):
                errors.append(f"{key}[{i}].head must be a non-empty array (column headers) for table slides")
            rows = s.get("rows")
            if not isinstance(rows, list) or not rows:
                errors.append(f"{key}[{i}].rows must be a non-empty array for table slides")
            else:
                ncols = len(s.get("head", []))
                for j, r in enumerate(rows):
                    if not isinstance(r, list) or (ncols and len(r) != ncols):
                        errors.append(f"{key}[{i}].rows[{j}] must have {ncols} cells matching head")
        elif stype == "chart":
            bars = s.get("bars")
            if not isinstance(bars, list) or not bars:
                errors.append(f"{key}[{i}].bars must be a non-empty array for chart slides")
            else:
                for j, b in enumerate(bars):
                    if not isinstance(b, dict) or not b.get("label") or b.get("value") is None:
                        errors.append(f"{key}[{i}].bars[{j}] needs label + value")
        elif stype == "counter":
            if s.get("value") is None:
                errors.append(f"{key}[{i}].value is required for counter slides")
            if not s.get("label"):
                errors.append(f"{key}[{i}].label is required for counter slides")
        elif stype == "cards":
            cards = s.get("cards")
            if not isinstance(cards, list) or not cards:
                errors.append(f"{key}[{i}].cards must be a non-empty array for cards slides")
            else:
                for j, cd in enumerate(cards):
                    if not isinstance(cd, dict) or not cd.get("title") or not cd.get("body"):
                        errors.append(f"{key}[{i}].cards[{j}] needs title + body")
        elif stype == "steps":
            steps = s.get("steps")
            if not isinstance(steps, list) or not steps:
                errors.append(f"{key}[{i}].steps must be a non-empty array for steps slides")
            else:
                for j, st in enumerate(steps):
                    if not isinstance(st, dict) or not st.get("title") or not st.get("body"):
                        errors.append(f"{key}[{i}].steps[{j}] needs title + body")
        elif stype == "outro":
            if not s.get("recap"):
                errors.append(f"{key}[{i}].recap is required for outro slides")
    if not any(s.get("type") == "outro" for s in slides):
        warns.append(f"{key}[] has no outro slide — one will be auto-appended")


def validate_mode(path: str) -> None:
    try:
        data = json.loads(read(path))
    except json.JSONDecodeError:
        die(f"{path} is not valid JSON")

    errors: list[str] = []
    warns: list[str] = []

    if not isinstance(data, dict):
        die(f"{path} must be a JSON object")

    meta = data.get("meta") or {}
    if not isinstance(meta, dict):
        errors.append("meta must be an object")
        meta = {}
    if not meta.get("title"):
        errors.append("meta.title is required")
    if not meta.get("lang"):
        warns.append("meta.lang missing — defaulting to zh")

    cover = data.get("cover") or {}
    if not isinstance(cover, dict):
        errors.append("cover must be an object")
    if not cover.get("title"):
        errors.append("cover.title is required")

    # ── Primary (zh) dialogue + slides ──
    podcast = data.get("podcast")
    slides = data.get("slides")
    _validate_dialogue(podcast, "podcast", errors)
    _validate_ticker(data.get("ticker"), "ticker", errors)
    _validate_panels(slides, "slides", errors, warns)

    # ── Optional English variants (en video). Validate shape if present. ──
    if data.get("podcastEn") is not None:
        _validate_dialogue(data.get("podcastEn"), "podcastEn", errors)
    if data.get("tickerEn") is not None:
        _validate_ticker(data.get("tickerEn"), "tickerEn", errors)
    if data.get("slidesEn") is not None:
        _validate_panels(data.get("slidesEn"), "slidesEn", errors, warns)
    if data.get("coverEn") is not None:
        ce = data.get("coverEn")
        if not isinstance(ce, dict) or not ce.get("title"):
            errors.append("coverEn.title is required when coverEn is present")

    if errors:
        sys.stderr.write("✗ script.json validation failed:\n")
        for e in errors:
            sys.stderr.write(f"  - {e}\n")
        if warns:
            sys.stderr.write("Warnings:\n")
            for w in warns:
                sys.stderr.write(f"  - {w}\n")
        sys.exit(1)

    # Fill defaults
    data["meta"] = meta
    meta["lang"] = meta.get("lang") or "zh"
    if not meta.get("kicker"):
        meta["kicker"] = "TECH BRIEF"
    if not meta.get("roles"):
        meta["roles"] = {"male": "主讲", "female": "主持"}
    # rough target length estimate from dialogue text
    if not meta.get("target_seconds"):
        total_chars = sum(len(t.get("text", "")) for t in podcast)
        meta["target_seconds"] = round(total_chars / 3.4)
    data["cover"] = cover
    if not cover.get("kicker"):
        cover["kicker"] = meta["kicker"]

    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    sys.stdout.write(
        f"✓ script.json valid: {len(podcast)} dialogue turns, "
        f"{len(slides or [])} slides, target ~{meta['target_seconds']}s, lang={meta['lang']}\n"
    )
    sys.exit(0)


def extract_outline(input_path: str, output_path: str) -> None:
    ext = os.path.splitext(input_path)[1].lstrip(".").lower()
    if ext not in ("md", "markdown", "txt"):
        warn(f'unusual extension ".{ext}" — parsing as markdown')

    text = read(input_path)
    lines = text.splitlines()
    outline: dict = {
        "source": str(Path(input_path).resolve()),
        "title": None,
        "headings": [],
        "paragraphs": [],
        "codeBlocks": [],
        "wordCount": 0,
    }

    in_code = False
    code_buf: list[str] = []
    para_buf: list[str] = []

    def flush_para() -> None:
        p = " ".join(para_buf).split()
        p = " ".join(p).strip()
        if p:
            outline["paragraphs"].append(p)
        para_buf.clear()

    for line in lines:
        if re.match(r"^\s*```", line):
            if in_code:
                outline["codeBlocks"].append("\n".join(code_buf))
                code_buf.clear()
                in_code = False
            else:
                flush_para()
                in_code = True
            continue
        if in_code:
            code_buf.append(line)
            continue
        if re.match(r"^#{1,6}\s", line):
            flush_para()
            heading = re.sub(r"^#{1,6}\s+", "", line).strip()
            heading = re.sub(r"[#\s]+$", "", heading).strip()
            outline["headings"].append(heading)
            if not outline["title"]:
                outline["title"] = heading
            continue
        if re.match(r"^\s*$", line):
            flush_para()
            continue
        if outline["title"] is None and not re.match(r"^\s*[-*+\d.)]\s", line):
            outline["title"] = line.strip()[:120]
        para_buf.append(re.sub(r"^[-*+]\s+", "", line).strip())

    flush_para()

    outline["wordCount"] = len([w for w in re.split(r"\s+", text) if w])
    outline["summary"] = (
        f"Title: {outline['title'] or '(none detected)'}\n"
        f"Headings ({len(outline['headings'])}): {' → '.join(outline['headings']) or '—'}\n"
        f"Paragraphs: {len(outline['paragraphs'])}, Code blocks: {len(outline['codeBlocks'])}, Words: {outline['wordCount']}"
    )

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(outline, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    sys.stdout.write(
        f"✓ outline written to {output_path}\n{outline['summary']}\n"
        f"\nNow author dist/script.json (podcast[] dialogue + slides[]) from this outline, then:\n"
        f"  uv run python scripts/parse_article.py --validate dist/script.json\n"
    )
    sys.exit(0)


def main() -> None:
    p = argparse.ArgumentParser(description="Extract article outline / validate script.json")
    p.add_argument("--input", help="article path (markdown/txt) for outline extraction")
    p.add_argument("--output", default="dist/article.json", help="outline output JSON")
    p.add_argument("--validate", help="validate an existing dist/script.json")
    args = p.parse_args()

    if args.validate:
        validate_mode(args.validate)
    elif args.input:
        extract_outline(args.input, args.output)
    else:
        die("missing --input <article> (or use --validate <script.json>)")


if __name__ == "__main__":
    main()
