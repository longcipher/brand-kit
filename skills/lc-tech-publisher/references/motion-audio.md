# LongCipher Motion & Audio Language (Light System)

Defines how motion and audio behave in the **light, fixed-component** explainers
(`assets/templates/dashboard.html` + `tpl_cover.html`). The goal is *restrained,
engineered motion* — restrained enough to read as a serious brief, animated
enough to never feel like a deck. All visuals live in fixed templates; this doc
describes the GSAP vocabulary the templates use so any future template edit
stays consistent.

## 1. Motion Principles

- **Restrained, never noisy.** No neon, no glow blobs, no chart bloom. The
  light system relies on **2px ink rules, shadow-as-border cards, and gentle
  stagger** to give life without theatrics.
- **Compositor-only.** Animate **only** `transform`, `opacity`, and `filter`.
  Never animate `width/height/top/left`. This keeps Puppeteer/Playwright
  frame capture at 60fps with no jank.
- **One slide at a time.** Slides 0..n are absolute-positioned, full-frame,
  overlapping `position:absolute; inset:0`. Only the active slide carries
  `.on` (CSS `opacity:1; visibility:visible`); others are hidden via the base
  `.slide { opacity:0; visibility:hidden }`. Every slide is also a
  HyperFrames `clip` with `data-start`/`data-duration`/`data-track-index` so
  the renderer/scanner only treats one as live at a time.
- **Sync is absolute.** Every slide and every caption has `data-start` aligned
  to the absolute dialogue timeline from `speaker_timestamps.json`.

## 2. Motion Vocabulary (GSAP) — used by `dashboard.html`

| Context | Easing | Duration |
|---------|--------|----------|
| Slide enter (autoAlpha) | `power3.out` | 0.5s |
| Slide exit (autoAlpha) | `power2.inOut` | 0.4s |
| Cover kicker / eyebrow (slide-in from left) | `power3.out` | 0.5s |
| Cover title (rise + fade) | `power3.out` | 0.8s |
| Cover sub (gentle rise) | `power2.out` | 0.6s |
| Headlines list items stagger | `power2.out` | 0.5s, `stagger: 0.1` |
| Keypoint accent rule (scaleY 0→1) | `power3.out` | 0.6s, `transformOrigin: top` |
| Keypoint statement (rise + fade) | `power3.out` | 0.7s |
| Three-points card stagger (rise + fade) | `power3.out` | 0.6s, `stagger: 0.12` |
| Outro card (rise + fade) | `power3.out` | 0.7s |
| Caption pop-in | `power3.out` | 0.2s |
| Caption fade-out | (linear) | 0.18s |
| Master fade-out tail | `power2.inOut` | 0.5s |

### Per-slide entrance pattern (executed in `dashboard.html` JS)

```js
tl.add(function(){ el.classList.add("on"); }, start - 0.02); // CSS visibility
tl.set(el, { autoAlpha: 0 }, start - 0.01);                   // GSAP hold
tl.to(el,  { autoAlpha: 1, duration: 0.5, ease: "power3.out" }, start);
tl.fromTo(el.querySelectorAll(".eyebrow, .head, .kicker"),
  { x: -16, autoAlpha: 0 },
  { x: 0, autoAlpha: 1, duration: 0.5, ease: "power3.out" },
  start + 0.2);
tl.fromTo(el.querySelectorAll(".statement, .recap, .card"),
  { y: 26, autoAlpha: 0 },
  { y: 0, autoAlpha: 1, duration: 0.7, ease: "power3.out" },
  start + 0.35);
tl.fromTo(el.querySelectorAll(".point"),
  { y: 28, autoAlpha: 0 },
  { y: 0, autoAlpha: 1, duration: 0.6, ease: "power3.out", stagger: 0.12 },
  start + 0.4);
tl.to(el, { autoAlpha: 0, duration: 0.4, ease: "power2.inOut" }, end - 0.35);
tl.add(function(){ el.classList.remove("on"); }, end);
```

### Cover hero pattern (`tpl_cover.html` and slide-0)

```js
tl.fromTo(".lockup",     { x: -16, autoAlpha: 0 }, { x: 0, autoAlpha: 1, duration: 0.5 }, 0.10);
tl.fromTo(".corner-tag", { x:  16, autoAlpha: 0 }, { x: 0, autoAlpha: 1, duration: 0.5 }, 0.10);
tl.fromTo(".kicker",     { x: -16, autoAlpha: 0 }, { x: 0, autoAlpha: 1, duration: 0.5, ease: "power3.out" }, 0.20);
tl.fromTo(".title",      { y:  26, autoAlpha: 0 }, { y: 0, autoAlpha: 1, duration: 0.8, ease: "power3.out" }, 0.35);
tl.fromTo(".sub",        { y:  18, autoAlpha: 0 }, { y: 0, autoAlpha: 1, duration: 0.6, ease: "power2.out" }, 0.65);
tl.fromTo(".headlines",  { autoAlpha: 0 },         { autoAlpha: 1, duration: 0.5 }, 0.90);
tl.fromTo(".headlines li",
  { x: -16, autoAlpha: 0 },
  { x: 0, autoAlpha: 1, duration: 0.5, stagger: 0.10, ease: "power2.out" },
  1.00);
tl.fromTo(".meta-row",   { y:  14, autoAlpha: 0 }, { y: 0, autoAlpha: 1, duration: 0.5 }, 0.85);
```

The cover composition uses `data-duration="2.4"` so `render_cover.py` extracts
its frame at `-ss 1.9` (caught after the headlines stagger fully reveals).

## 3. Audio Language (Two-Speaker Dialogue)

The podcast is a **dual-voice dialogue** (老高/小茉 style): a knowledgeable
male host + a curious female co-host. Output is a merged MP3/WAV **and** a
speaker timeline for video caption + slide sync.

### Voices (Edge Neural TTS, default)

| Role | Voice ID | Persona |
|------|----------|---------|
| Male host (老高) | `zh-CN-YunxiNeural` | Confident, witty, explains complex ideas simply, storyteller. |
| Female co-host (小茉) | `zh-CN-XiaoxiaoNeural` (alt `zh-CN-XiaoyiNeural`) | Curious, asks plain-language questions, reacts emotionally, paces the show. |
| English single voice | `en-US-AndrewNeural` | Both English speakers use this voice; speaker labels are kept for caption tint only. |

### Dialogue rules

- `podcast[]` is an ordered array of turns: `{ id, speaker, voice?, text }`.
- Female inserts a real question / reaction every 2–3 male lines (no dead air).
- Caption shows the *current* speaker's line; speaker differentiation is the
  caption's left-border tint (male = `--accent` blue, female = `--ink-300` grey).
- Total pacing ~3.2–3.6 chars/sec (zh) so slide beats land at the turn boundary.

### Speaker timeline (`speaker_timestamps.json`)

`generate_audio.py` measures each turn's WAV with ffprobe and emits:

```json
{
  "total": 100.0,
  "engine": "edge-tts",
  "lang": "zh",
  "turns": [
    { "id": "01", "speaker": "male", "voice": "zh-CN-YunxiNeural",
      "text": "…", "file": "audio/turn-01.wav",
      "start": 0.0, "end": 6.4, "duration": 6.4 }
  ]
}
```

The video builder maps `turns[]` to:
- caption `.cap.clip` per turn (text identical to spoken line);
- `<audio class="clip">` per turn pointed at `audio/turn-NN.wav`;
- slide `data-start`/`data-duration` aligned to the dialogue window the slide illustrates.

## 4. Timing Contract

| Field | Meaning |
|-------|---------|
| `turns[i].start` | Timeline second this speaker turn begins |
| `turns[i].duration` | ffprobe-measured WAV length |
| Slide `data-start`/`data-duration` | Aligned to the dialogue window it illustrates; slides are auto-distributed evenly across `[HERO_DURATION=4.0, total]` when `_start`/`_end` are absent |
| Master `data-duration` | Sum of turn durations + 0.5s tail |

Rules:
1. Caption `data-duration` == its turn audio duration.
2. Caption rendering uses `display:block; opacity:0; visibility:hidden` so GSAP
   `autoAlpha` can switch it to visible. (Never `display:none` — that defeats
   GSAP's visibility transition and the caption silently fails to show.)
3. Final 0.5s fade-out tail for a clean end (`tl.to("#master", { autoAlpha: 0 }, total + 0.5 - 0.5)`).

## 5. Duration Budget

For `meta.target_seconds` of T (auto-estimated by `parse_article.py` from total
dialogue chars):
- Aim 8–14 dialogue turns, ~6–10s each, totaling ~T ± 15%.
- Slide count auto-derived from `script.json slides[]`. `build_composition.py`
  auto-appends an `outro` slide if missing.
- Hero duration is fixed at 4.0s for the cover slide; the remaining
  `(T - 4.0) / n` is divided evenly across the n slides.
- English video single-voice mode runs the same pipeline; turn timing and slide
  distribution are recomputed from the EN timings file.

## 6. Accessibility

- All text/background pairs in the templates pass WCAG AA 4.5:1.
- Brand blue used as **text** is `--accent-text: #0a63d0` (slightly darker
  variant of `--accent: #0a72ef`); the original `--accent` is reserved for
  lines, borders, dots.
- Greys `--ink-300 #565a63` / `--ink-400 #6b6e75` are tuned to clear 4.5:1 on
  both `#fafbfc` (canvas) and `#ffffff` (surface cards).
- Captions are allowed to wrap multi-line; no `white-space: nowrap`, so long
  CJK sentences render fully without ellipsis.

## 7. Embedding rules

- Captions are embedded directly in the composition (one `.cap.clip` per turn)
  so the rendered MP4 already shows subtitles — no player-side burn-in.
- A same-named `.srt` is also emitted next to the MP4 for podcast-style
  playback (40–62 cues for ~100–140s of dialogue).