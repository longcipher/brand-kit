#!/usr/bin/env python3
"""subtitle_util.py — shared subtitle/cue splitting used by both the SRT
emitter (render_video.py) and the video composition (build_composition.py).

Keeping the split logic in ONE place guarantees the embedded captions and the
.srt sidecar are byte-for-byte the same sequence of one-line cues, so the
on-screen caption refreshes exactly in step with the spoken audio.
"""

from __future__ import annotations

import re


def _split_sentences(text: str, lang: str) -> list[str]:
    """Split into atomic sentences on STRONG punctuation only (. ! ? 。 ！ ？),
    keeping the delimiter. Each returned piece is a self-contained sentence."""
    if lang == "en":
        parts = re.split(r"(?<=[.!?])\s*", text)
    else:
        parts = re.split(r"(?<=[。！？])", text)
    return [p.strip() for p in parts if p.strip()]


def _hard_split(piece: str, lang: str, hard_max: int) -> list[str]:
    """Hard-split an over-long single sentence at WEAK punctuation (commas etc.)
    or word/char boundaries, targeting ~hard_max-per-chunk so no cue overflows."""
    if lang == "en":
        words = piece.split()
        if len(words) <= hard_max:
            return [piece]
        out: list[str] = []
        cur: list[str] = []
        for w in words:
            cur.append(w)
            if len(cur) >= hard_max:
                out.append(" ".join(cur))
                cur = []
        if cur:
            out.append(" ".join(cur))
        return out
    # CJK: prefer weak-punctuation boundaries, then char budget
    weak = "，,、；;：:—… "
    out: list[str] = []
    i = 0
    L = len(piece)
    while i < L:
        j = min(i + hard_max, L)
        if j < L:
            k = j
            while k > i and piece[k - 1] not in weak:
                k -= 1
            if k > i:
                j = k
        out.append(piece[i:j])
        i = j
    return out


def split_subtitles(text: str, lang: str) -> list[str]:
    """Split a dialogue turn into single-line subtitle cues.

    Strategy (driven by layout, not by audio length):
      • Break ONLY at strong punctuation (。！？.!?) into atomic sentences.
      • Greedily MERGE consecutive short sentences into one cue until the cue
        reaches ~TARGET length (≈ 2/3 of the 1920px frame width), so a cue is
        rarely just two or three words.
      • Only if a single sentence still exceeds HARD_MAX is it force-split at
        weak punctuation (，、；： etc.) / word boundaries.
    Original meaning is preserved verbatim — we never drop or reorder text.
    """
    text = text.replace("\r", " ").replace("\n", " ").strip()
    if not text:
        return []

    if lang == "en":
        target, hard_max = 12, 15   # words per cue (~fits 1500px @28px)
    else:
        target, hard_max = 30, 46   # CJK chars per cue (~2/3 frame width)

    sentences = _split_sentences(text, lang)
    cues: list[str] = []
    buf = ""
    for s in sentences:
        # A lone over-long sentence — split it internally, flush the buffer first.
        if len(s) > hard_max:
            if buf:
                cues.append(buf)
                buf = ""
            cues.extend(_hard_split(s, lang, hard_max))
            continue
        # If adding this sentence would overrun target, emit the buffer and
        # start a fresh cue with this sentence.
        if buf and (len(buf) + 1 + len(s)) > target:
            cues.append(buf)
            buf = s
        else:
            buf = (buf + " " + s) if buf else s
    if buf:
        cues.append(buf)
    return cues
