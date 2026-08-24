#!/usr/bin/env python3
"""build_composition.py — assemble the LIGHT HyperFrames composition from
script.json + speaker_timestamps.json.

Strategy (fixed-template, JSON-only authoring):
  - The LLM writes structured JSON only (cover + slides[] + podcast[]).
  - This script injects that data into the hand-built light templates
    (assets/templates/dashboard.html). NO CSS is authored by the LLM.
  - Slides are laid out as full-frame components, evenly distributed across the
    narration timeline, each a HyperFrames clip aligned to speaker turns.

Usage:
  uv run python scripts/build_composition.py --script dist/script.json \
      --timings dist/speaker_timestamps.json --out dist/video
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

import subtitle_util as sub

HYPERFRAMES_JSON = '{\n  "$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",\n  "paths": { "assets": "assets" }\n}\n'

TEMPLATE = "assets/templates/dashboard.html"
HERO_DURATION = 4.0  # cover/hero hook before first content slide
SKILL_ROOT = Path(__file__).resolve().parent.parent


def die(msg: str) -> None:
    sys.stderr.write(f"✗ {msg}\n")
    sys.exit(1)


def _pick(script: dict, key: str, lang: str):
    if lang == "en":
        val = script.get(key + "En")
        if val is None:
            sys.stderr.write(f"! {key}En missing — falling back to {key}[] for EN video\n")
            val = script.get(key)
        return val
    return script.get(key)


def _split_turn_cues(turn: dict, lang: str) -> list[dict]:
    """Split a spoken turn into per-cue caption windows that exactly mirror the
    .srt sidecar. Each cue owns its own [start, end] slice of the turn's audio,
    so the on-screen caption refreshes line-by-line in step with the voice
    (instead of one long caption that gets truncated by `text-overflow`)."""
    text = (turn.get("text") or "").strip()
    if not text:
        return []
    start = float(turn.get("start", 0))
    end = float(turn.get("end", 0))
    span = max(end - start, 0.001)
    cues_text = sub.split_subtitles(text, lang)
    if not cues_text:
        return []
    weights = [len(c) for c in cues_text]
    total_w = sum(weights) or 1
    out: list[dict] = []
    cursor = start
    speaker = turn.get("speaker")
    for c, w in zip(cues_text, weights):
        dur = span * (w / total_w)
        seg_end = cursor + dur
        out.append({
            "text": c,
            "speaker": speaker,
            "start": round(cursor, 3),
            "end": round(seg_end, 3),
        })
        cursor = seg_end
    return out


def main() -> None:
    p = argparse.ArgumentParser(description="Build the light composition")
    p.add_argument("--script", default="dist/script.json")
    p.add_argument("--timings", default="dist/speaker_timestamps.json")
    p.add_argument("--lang", default="zh", choices=["zh", "en"])
    p.add_argument("--out", default="dist/video")
    args = p.parse_args()

    lang = args.lang
    script_path = Path(args.script)
    default_timings = (
        f"dist/speaker_timestamps_{lang}.json" if lang == "en" else "dist/speaker_timestamps.json"
    )
    timings_path = Path(
        args.timings if args.timings != "dist/speaker_timestamps.json" else default_timings
    )
    out_dir = Path(args.out if args.out != "dist/video" else f"dist/video_{lang}")

    if not script_path.exists():
        die(f"missing script: {script_path}")
    if not timings_path.exists():
        die(f"missing timings: {timings_path} (run generate-audio --lang {lang} first)")

    script = json.loads(script_path.read_text(encoding="utf-8"))
    timestamps = json.loads(timings_path.read_text(encoding="utf-8"))
    turns = timestamps.get("turns")
    if not isinstance(turns, list) or not turns:
        die("speaker_timestamps.json has no turns")

    total = float(timestamps.get("total", 0))
    if total <= 0:
        die("timings.total must be > 0")

    meta = script.get("meta", {})
    cover = _pick(script, "cover", lang) or {}
    slides = _pick(script, "slides", lang) or []

    # Auto-append an outro if the last slide isn't one.
    if not slides or slides[-1].get("type") != "outro":
        slides = list(slides) + [{"type": "outro", "recap": cover.get("subtitle") or meta.get("subtitle") or "",
                                  "signoff": "LongCipher", "audioFrom": turns[-1].get("id") if turns else None,
                                  "audioTo": turns[-1].get("id") if turns else None}]

    # Map each slide to the audio window it illustrates. A slide may declare
    # `audioFrom`/`audioTo` turn ids so the on-screen text stays in lock-step
    # with the spoken narration (the user reads the center zone, not the
    # caption). Without those hints we fall back to even distribution.
    id_to_turn = {t.get("id"): t for t in turns}
    n = len(slides)

    def _turn_time(tid, which):
        t = id_to_turn.get(tid)
        if not t:
            return None
        return float(t.get(which, 0))

    # First pass: resolve explicit audioFrom/audioTo windows.
    windows = []
    for s in slides:
        a0, a1 = s.get("audioFrom"), s.get("audioTo")
        t0 = _turn_time(a0, "start") if a0 else None
        t1 = _turn_time(a1, "end") if a1 else None
        if t0 is None or t1 is None:
            windows.append(None)
        else:
            windows.append((round(t0, 3), round(t1, 3)))

    # Second pass: fill gaps so every slide has a contiguous, non-overlapping
    # window across [HERO_DURATION, total]. Slides with explicit windows keep
    # them; the rest are distributed PROPORTIONALLY BY TURN COUNT so each
    # slide's on-screen window matches the dialogue it illustrates. This
    # prevents cumulative drift (voice pulling ahead of slides) that the old
    # even-time-split caused.
    if any(w is None for w in windows):
        unbound_indices = [i for i, w in enumerate(windows) if w is None]
        n_unbound = len(unbound_indices)
        n_turns = len(turns)
        # Assign each unbound slide a proportional range of dialogue turns.
        # The slide's time window = [start of its first turn, end of its last].
        turn_step = n_turns / n_unbound if n_unbound > 0 else 1
        for rank, slide_idx in enumerate(unbound_indices):
            ti_start = int(round(rank * turn_step))
            ti_end = int(round((rank + 1) * turn_step))
            ti_start = min(ti_start, n_turns - 1)
            ti_end = max(ti_end, ti_start + 1)
            ti_end = min(ti_end, n_turns)
            t_start = float(turns[ti_start]["start"])
            t_end = float(turns[ti_end - 1]["end"])
            windows[slide_idx] = (round(t_start, 3), round(t_end, 3))
    # Ensure monotonic, gap-free coverage. Each slide starts at its resolved
    # audio-binding window, and its end is pushed to the NEXT slide's start so
    # unbound "bridge" turns are visually absorbed by the previous slide (no
    # blank gaps in the video). The last slide runs to the end of the audio.
    windows.sort(key=lambda x: x[0])
    for i in range(n):
        s_start, s_end = windows[i]
        s_start = round(max(s_start, HERO_DURATION if i == 0 else windows[i - 1][1]), 3)
        if i < n - 1:
            s_end = max(s_end, windows[i + 1][0])
        else:
            s_end = max(s_end, total)
        # never let a slide be shorter than a minimum so content is readable
        s_end = max(s_end, s_start + 1.0)
        windows[i] = (s_start, round(s_end, 3))

    for i, s in enumerate(slides):
        s["_start"] = windows[i][0]
        s["_end"] = windows[i][1]

    # Cover/hero stays on screen through the intro narration (until the first
    # slide begins) so there is never a blank gap between the hero hook and the
    # first content slide. Fall back to HERO_DURATION if no slide exists.
    cover_end = round(windows[0][0], 3) if windows else HERO_DURATION

    data = {
        "lang": lang,
        "logo": "logos/lc.svg",
        "coverEnd": cover_end,
        "cover": {
            "kicker": cover.get("kicker") or meta.get("kicker", "BRIEF"),
            "title": cover.get("title") or meta.get("title", ""),
            "subtitle": cover.get("subtitle") or meta.get("subtitle", ""),
            "cornerTag": cover.get("cornerTag") or cover.get("kicker") or meta.get("kicker", "BRIEF"),
            "metaLeft": cover.get("metaLeft") or f"{meta.get('brand','LongCipher')} · {meta.get('kicker','BRIEF')}",
            "metaRight": cover.get("metaRight") or meta.get("date") or "",
            "headlinesLabel": cover.get("headlinesLabel") or meta.get("headlinesLabel") or ("今日重点" if lang == "zh" else "TODAY'S FOCUS"),
            "headlines": cover.get("headlines") or [],
        },
        "slides": slides,
        "turns": [
            {
                "id": t.get("id"),
                "speaker": t.get("speaker"),
                "voice": t.get("voice", ""),
                "emotion": t.get("emotion", ""),
                "rate": t.get("rate", ""),
                "text": t.get("text", ""),
                "start": round(float(t.get("start", 0)), 3),
                "end": round(float(t.get("end", 0)), 3),
                "duration": round(float(t.get("duration", 0)), 3),
                "file": t.get("file", ""),
                "cues": _split_turn_cues(t, lang),
            }
            for t in turns
        ],
    }

    template_path = SKILL_ROOT / TEMPLATE
    if not template_path.exists():
        die(f"missing template: {template_path}")
    html = template_path.read_text(encoding="utf-8")

    icons_path = SKILL_ROOT / "assets" / "templates" / "_icons.js"
    icons_js = icons_path.read_text(encoding="utf-8") if icons_path.exists() else "var ICONS = {};"
    html = html.replace("{{ICONS_JS}}", icons_js)

    data_json = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    html = html.replace("window.LC_DATA = {};", f"window.LC_DATA = {data_json};")
    html = html.replace("{{DURATION}}", f"{round(total + 0.5, 3)}")
    html = html.replace("{{LANG}}", lang)
    html = html.replace("{{TITLE}}", (cover.get("title") or meta.get("title") or "").replace("\n", " "))
    html = html.replace("{{LOGO}}", "logos/lc.svg")

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "index.html").write_text(html, encoding="utf-8")
    (out_dir / "hyperframes.json").write_text(HYPERFRAMES_JSON, encoding="utf-8")

    logo_src = SKILL_ROOT / "assets" / "logos" / "lc.svg"
    if logo_src.exists():
        dst = out_dir / "logos"
        dst.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(logo_src, dst / "lc.svg")
    else:
        sys.stderr.write(f"! brand logo missing: {logo_src}\n")

    # Vendor GSAP locally so composition load never depends on CDN reachability.
    vendor_src = SKILL_ROOT / "assets" / "vendor" / "gsap.min.js"
    if vendor_src.exists():
        vdst = out_dir / "assets" / "vendor"
        vdst.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(vendor_src, vdst / "gsap.min.js")
    else:
        sys.stderr.write(f"! vendored gsap missing: {vendor_src} (CDN fallback will be used)\n")

    # Self-hosted brand fonts — no Google Fonts CDN dependency at render time.
    fonts_src = SKILL_ROOT / "assets" / "fonts"
    if fonts_src.is_dir():
        fdst = out_dir / "assets" / "fonts"
        fdst.mkdir(parents=True, exist_ok=True)
        for woff in sorted(fonts_src.glob("*.woff2")):
            shutil.copyfile(woff, fdst / woff.name)

    sys.stdout.write(
        f"✓ composition written (lang={lang}): {out_dir / 'index.html'} "
        f"({len(turns)} turns, {len(slides)} slides, {round(total + 0.5, 3)}s)\n"
        f"  Next: cd {out_dir} && npx --yes hyperframes lint && npx --yes hyperframes check\n"
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
