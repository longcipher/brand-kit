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


def _normalize_text(text: str) -> str:
    """Normalize text for duplicate detection: strip, collapse whitespace,
    strip punctuation, lowercase. Keeps only alphanumerics + CJK chars."""
    t = re.sub(r"\s+", "", text.strip())
    return re.sub(r"[^\w\u4e00-\u9fff]", "", t).lower()


def _validate_dialogue(podcast, key: str, errors: list[str]) -> None:
    if not isinstance(podcast, list) or not podcast:
        errors.append(f"{key}[] must be a non-empty array of dialogue turns")
        return
    valid_speakers = {"male", "female"}
    prev_norm = None
    prev_idx = None
    for i, t in enumerate(podcast):
        if not isinstance(t, dict):
            errors.append(f"{key}[{i}] must be an object")
            continue
        sp = t.get("speaker")
        if sp not in valid_speakers:
            errors.append(f"{key}[{i}].speaker must be 'male' or 'female' (got {sp!r})")
        text = t.get("text", "")
        if not text:
            errors.append(f"{key}[{i}].text is required (the spoken line)")
        # Duplicate detection: flag consecutive turns with high text overlap.
        norm = _normalize_text(text)
        if norm and prev_norm is not None and len(norm) > 5 and len(prev_norm) > 5:
            if norm == prev_norm:
                errors.append(
                    f"{key}[{i}] is a VERBATIM DUPLICATE of {key}[{prev_idx}] "
                    f"(same normalized text). Remove the duplicate turn."
                )
            else:
                # Character-bag Jaccard similarity catches paraphrased duplicates
                set_a, set_b = set(norm), set(prev_norm)
                jaccard = len(set_a & set_b) / len(set_a | set_b) if (set_a | set_b) else 0
                # Also check: shorter fully contained in longer (with gap tolerance)
                shorter, longer = (norm, prev_norm) if len(norm) <= len(prev_norm) else (prev_norm, norm)
                containment = shorter in longer
                if jaccard > 0.70 or (containment and len(shorter) / len(longer) > 0.75):
                    errors.append(
                        f"{key}[{i}] is a NEAR-DUPLICATE of {key}[{prev_idx}] "
                        f"(similarity {jaccard:.0%}). Remove or substantially rephrase."
                    )
        if norm:
            prev_norm = norm
            prev_idx = i
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


VALID_SLIDE_TYPES = {
    "keypoint", "three_points", "outro", "table", "chart", "counter",
    "cards", "steps", "metric_chart", "pipeline", "benchmark", "security", "terminal",
}

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
            body = s.get("body")
            if not body or (isinstance(body, list) and len(body) < 2):
                warns.append(
                    f"{key}[{i}] (keypoint) has no/insufficient `body` — add 2–4 detail paragraphs "
                    f"so the slide has substantive content matching the narration"
                )
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

    # ── Content completeness check: every article section must be covered ──
    # Compare the script's content against the article outline headings and
    # bullet-level text. We extract the raw bullet text from the source article
    # (not just headings) so we can verify that specific topics/items appear
    # in the dialogue. This catches the "LLM skipped the later sections" bug.
    outline_path = Path(path).parent / "article.json"
    if outline_path.exists():
        try:
            outline = json.loads(outline_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            outline = None
        if outline:
            # Build the full script text (podcast + slides) to search for coverage
            script_text = " ".join(t.get("text", "") for t in podcast)
            script_text += " " + " ".join(
                s.get("statement", "") + " " + s.get("title", "") + " " + s.get("eyebrow", "")
                + " " + " ".join(p.get("title", "") + " " + p.get("body", "") for p in (s.get("points") or []))
                + " " + " ".join(p.get("title", "") + " " + p.get("body", "") for p in (s.get("cards") or []))
                + " " + " ".join(p.get("title", "") + " " + p.get("body", "") for p in (s.get("steps") or []))
                + " " + " ".join(s.get("body", []) if isinstance(s.get("body"), list) else [s.get("body", "")])
                + " " + s.get("recap", "")
                for s in (slides or [])
            )
            script_text_lower = script_text.lower()
            paragraphs = outline.get("paragraphs", [])

            # Strategy: the article outline's paragraphs[] are the bullet-level
            # content — each one describes a specific topic/item. We check whether
            # the distinctive terms from each bullet appear in the script. If a
            # cluster of bullets (a section) has very few matches, that section
            # was likely skipped by the LLM.
            #
            # We partition paragraphs into sections using H2 headings as boundaries.

            headings = outline.get("headings", [])
            paragraphs = outline.get("paragraphs", [])

            # Extract H2-level section headings (一、二、三、四、五、)
            h2_pattern = re.compile(r"^[一二三四五六七八九十][、.\s]")
            h2_indices = [i for i, h in enumerate(headings) if h2_pattern.match(h.strip())]

            # Map each heading index to its section number (which H2 it belongs to)
            # For each paragraph, determine which section it falls under by finding
            # the nearest preceding H2 heading in the original text order.
            # Since outline doesn't store positions, we use a heuristic:
            # distribute paragraphs evenly across the gaps between H2 headings.

            # Better: use the heading index to section mapping. Each H2 starts a new
            # section. Paragraphs are assigned proportionally.
            if h2_indices and paragraphs:
                n_sections = len(h2_indices)
                # Distribute paragraphs across sections proportionally
                paras_per_section = len(paragraphs) / n_sections
                section_paragraphs: list[list[str]] = [[] for _ in range(n_sections)]
                for pi, para in enumerate(paragraphs):
                    sec_idx = min(int(pi / paras_per_section), n_sections - 1)
                    section_paragraphs[sec_idx].append(para)

                def _clean_md(text: str) -> str:
                    # Strip markdown formatting so we compare clean text
                    # (the dialogue text has no **bold** or *italic* markers)
                    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)  # **bold**
                    text = re.sub(r'\*(.+?)\*', r'\1', text)        # *italic*
                    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)  # [link](url)
                    text = re.sub(r'`([^`]+)`', r'\1', text)        # `code`
                    return text.strip()

                uncovered_sections = []
                for si, sec_paras in enumerate(section_paragraphs):
                    if not sec_paras:
                        continue
                    h2_name = headings[h2_indices[si]].strip() if si < len(h2_indices) else f"Section {si+1}"

                    # Extract DISTINCTIVE terms from each section: proper nouns,
                    # project names, acronyms, and specific technical terms.
                    # Skip generic boilerplate that appears everywhere.
                    stopwords = {"核心更新", "相关链接", "核心逻辑", "核心观点", "核心内容",
                                 "核心实测", "具体介绍", "具体要求", "联系方式", "工作形式",
                                 "岗位需求", "招聘方", "核心能力", "人才背景", "相关链接",
                                 "时报报道", "官方博客", "深度解析", "深度报道", "实战经验"}
                    topic_keywords: list[str] = []
                    for para in sec_paras:
                        para_clean = _clean_md(para)
                        # Extract Chinese character sequences (4+ chars)
                        chinese_runs = re.findall(r'[\u4e00-\u9fff]{4,}', para_clean)
                        for run in chinese_runs:
                            if run not in stopwords and run not in topic_keywords:
                                topic_keywords.append(run)
                        # Also extract English proper nouns / acronyms (2+ chars)
                        english_runs = re.findall(r'\b[A-Za-z][A-Za-z0-9.]{1,}\b', para_clean)
                        for run in english_runs:
                            if len(run) >= 2 and run not in topic_keywords:
                                topic_keywords.append(run)
                    if not topic_keywords:
                        continue
                    # Check: how many of these keywords appear in the script?
                    matched = 0
                    missing_samples = []
                    for kw in topic_keywords:
                        kw_lower = kw.lower()
                        found = kw_lower in script_text_lower
                        if found:
                            matched += 1
                        else:
                            missing_samples.append(kw[:20])
                    # Flag if less than 20% of the section's keywords are covered.
                    # This catches blatant section-skipping (the "LLM skipped the
                    # later sections" bug) while tolerating the LLM's natural
                    # rephrasing of concepts in different words.
                    coverage = matched / len(topic_keywords) if topic_keywords else 1
                    if coverage < 0.20:
                        uncovered_sections.append((h2_name, missing_samples[:3], coverage))

                if uncovered_sections:
                    warns.append(
                        f"Content completeness: {len(uncovered_sections)} article section(s) appear under-covered:"
                    )
                    for sec_name, missing, cov in uncovered_sections:
                        warns.append(f"  - {sec_name} (matched {cov:.0%}): e.g. {', '.join(missing)}")
                    warns.append(
                        "Cover EVERY section — add dialogue turns for missing topics. "
                        "Do NOT skip article content to control duration; the video can be longer."
                    )

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
    # Edge TTS speaks zh at ~5.5 chars/sec (measured), NOT the old 3.2–3.6 estimate
    if not meta.get("target_seconds"):
        total_chars = sum(len(t.get("text", "")) for t in podcast)
        meta["target_seconds"] = round(total_chars / 5.5)
    data["cover"] = cover
    if not cover.get("kicker"):
        cover["kicker"] = meta["kicker"]

    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    sys.stdout.write(
        f"✓ script.json valid: {len(podcast)} dialogue turns, "
        f"{len(slides or [])} slides, target ~{meta['target_seconds']}s, lang={meta['lang']}\n"
    )
    if warns:
        sys.stderr.write("Warnings:\n")
        for w in warns:
            sys.stderr.write(f"  - {w}\n")
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
