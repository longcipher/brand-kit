#!/usr/bin/env python3
"""parse_article.py — extract a raw outline from an article, and validate the
agent-authored dist/script.json against the skill schema.

Two modes:
  1. Outline extraction (Step 2):
       uv run python scripts/parse_article.py --input <article.md> --output dist/article.json
  2. Schema validation (Step 2 Gate):
       uv run python scripts/parse_article.py --validate dist/script.json

The outline is a *raw* skeleton — headings, code blocks, paragraphs. The agent
(LLM) uses it to author the final script.json with scenes + narration.
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


def validate_mode(path: str) -> None:
    try:
        data = json.loads(read(path))
    except json.JSONDecodeError:
        die(f"{path} is not valid JSON")

    errors: list[str] = []
    warns: list[str] = []

    if not data.get("meta", {}).get("title"):
        errors.append("meta.title is required")
    if not data.get("meta", {}).get("lang"):
        warns.append("meta.lang missing — defaulting to zh")
    if not data.get("cover", {}).get("title"):
        errors.append("cover.title is required")
    if not isinstance(data.get("scenes"), list):
        errors.append("scenes must be an array")

    scenes = data.get("scenes", [])
    if isinstance(scenes, list):
        if len(scenes) < 5:
            errors.append(f"scenes must have 5–8 entries (got {len(scenes)})")
        if len(scenes) > 8:
            errors.append(f"scenes must have 5–8 entries (got {len(scenes)})")
        for i, s in enumerate(scenes):
            if not s.get("id"):
                errors.append(f"scenes[{i}].id is required")
            if not s.get("title"):
                errors.append(f"scenes[{i}].title is required")
            if not s.get("narration"):
                errors.append(f"scenes[{i}].narration is required (spoken + captioned text)")
            pts = s.get("points")
            if pts is not None and (not isinstance(pts, list) or len(pts) > 4):
                errors.append(
                    f"scenes[{i}].points must be 2–4 bullets (got {len(pts) if isinstance(pts, list) else 'n/a'})"
                )

    podcast = data.get("podcast")
    if podcast is not None and not isinstance(podcast, list):
        errors.append("podcast (if present) must be an array of {role, text}")

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
    meta = data.setdefault("meta", {})
    meta["lang"] = meta.get("lang") or "zh"
    if not meta.get("kicker"):
        meta["kicker"] = "TECH EXPLAINER"
    if not meta.get("target_seconds"):
        total_chars = sum(len(s.get("narration", "")) for s in scenes)
        meta["target_seconds"] = round(total_chars / 3.4)
    cover = data.setdefault("cover", {})
    if not cover.get("kicker"):
        cover["kicker"] = meta["kicker"]

    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    sys.stdout.write(
        f"✓ script.json valid: {len(scenes)} scenes, target ~{meta['target_seconds']}s, lang={meta['lang']}\n"
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
        f"\nNow author dist/script.json (scenes + narration) from this outline, then:\n"
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
