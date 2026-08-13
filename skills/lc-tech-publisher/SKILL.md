---
name: lc-tech-publisher
description: Turn an article into a complete LongCipher-branded media package — a 16:9 cover image, a podcast MP3, and a narrated explainer video — built with HyperFrames. Use when the user provides an article (technical knowledge content, docs, blog post, paper notes) and wants cover / podcast / video output in the LongCipher design system. Narration uses Microsoft Edge Neural TTS by default (zh-CN-yunxi, no API key, no reference voice — needs internet + `pip install edge-tts`); an optional local Fun-CosyVoice3-0.5B backend provides brand-voice cloning. Video + cover render deterministically with npx hyperframes. Outputs land in output/ as cover.png, podcast_full.mp3, and explainer_video.mp4.
---

# LongCipher Tech Publisher

You are the LongCipher media production line. Given one article, you produce a branded media package with strict visual fidelity to the LongCipher design system (see `references/brand-design.md`) and strict audio-video synchronization (see `references/motion-audio.md`).

Run the 7 steps below in order. Each step has a **Gate**: do not move to the next step until the Gate passes. Keep every intermediate artifact under `dist/`.

## Step 1 — Setup & Environment Check

1. Confirm the target article path with the user.
2. Create the output workspace:

```bash
mkdir -p dist/{cover,video,audio,logos} output
```

3. Verify the toolchain:

```bash
uv run python scripts/check_env.py
```

**Gate**: `uv run python scripts/check_env.py` exits 0 — `ffmpeg`, `ffprobe`, the `hyperframes` CLI (`npx --yes hyperframes`), Node >= 22 (for the HyperFrames CLI), and the chosen TTS backend are resolvable. Default backend is **Edge Neural TTS** (`edge_tts` module, needs internet + `uv sync`). Pass `--tts cosyvoice` to `check_env.py` to validate the optional local CosyVoice3 environment (`COSYVOICE_HOME` / model + `COSYVOICE_PROMPT_WAV` brand voice) instead.

## Step 2 — Parse the Article → `dist/script.json`

1. Extract a raw outline (headings, code blocks, key paragraphs):

```bash
uv run python scripts/parse_article.py --input <article.md> --output dist/article.json
```

2. **You** (the agent) now write `dist/script.json` — this is the creative core. Use the outline, the article, `references/brand-design.md` (voice, tone) and `references/motion-audio.md` (pacing) to produce:

```jsonc
{
  "meta": {
    "title": "Article headline",
    "subtitle": "One-line thesis",
    "kicker": "TECH EXPLAINER",          // mono eyebrow, uppercase
    "lang": "zh",                         // or "en"
    "target_seconds": 120
  },
  "cover": {
    "kicker": "TECH EXPLAINER",
    "title": "Cover headline (max ~14 chars per line)",
    "subtitle": "Cover one-liner"
  },
  "podcast": [                            // OPTIONAL: overrides podcast audio if present
    { "role": "narrator", "text": "..." },
    { "role": "narrator", "text": "..." }
  ],
  "scenes": [                             // 5–8 scenes
    {
      "id": "01",
      "title": "Scene headline (short)",
      "keyword": "关键词 / KEYWORD",       // mono eyebrow in the corner
      "points": ["One bullet", "Two bullets"],   // 2–4 bullets max
      "code": "const x = 1;",             // optional, rendered in mono
      "narration": "What the narrator says for this scene."
    }
  ]
}
```

**Scene rules:**

- 5–8 scenes. Each scene carries one idea. The `narration` text is what gets spoken **and** shown as the bottom caption — keep them identical.
- Total `narration` length ≈ `meta.target_seconds` at ~3.2–3.6 chars/sec for zh, ~2.4 words/sec for en.
- Article is technical knowledge → prefer `code` and mono bullets over decorative imagery.

3. Validate the schema:

```bash
uv run python scripts/parse_article.py --validate dist/script.json
```

**Gate**: validation passes with no errors; `scenes.length` is 5–8.

## Step 3 — Generate Narration Audio & Timings

Narration is synthesized with the **Edge Neural TTS backend by default** (`zh-CN-yunxi`, free, no API key, no reference voice — needs `pip install edge-tts` + internet). Pass `--tts cosyvoice` to switch to the local **Fun-CosyVoice3-0.5B** brand-voice clone (requires a reference voice). See `references/tts.md` for the one-time setup of either backend.

Default (Edge, no reference voice needed):

```bash
uv run python scripts/generate_audio.py --script dist/script.json --out dist
```

Optional (local CosyVoice3, brand-voice clone):

```bash
uv run python scripts/generate_audio.py --script dist/script.json --tts cosyvoice \
    --prompt-wav "$COSYVOICE_PROMPT_WAV" --prompt-text "$COSYVOICE_PROMPT_TEXT" \
    --speed 1.0 --lang zh --out dist
```

- Edge flags: `--voice zh-CN-yunxi` (default), `--rate "-2%"`, `--volume "+0%"`. Overridable via `EDGE_TTS_VOICE` / `EDGE_TTS_RATE` / `EDGE_TTS_VOLUME`.
- CosyVoice3 `--prompt-wav` / `--prompt-text` are your **brand reference voice** (a short clean recording of the narrator). They may also be set via `COSYVOICE_PROMPT_WAV` / `COSYVOICE_PROMPT_TEXT` env vars.
- This produces `dist/audio/scene-NN.wav` per scene, `dist/video/audio/scene-NN.wav` copies, `dist/timestamps.json` (per-scene start/end/duration), and `dist/podcast_full.wav` (the concatenated podcast track).

**Gate**: `dist/timestamps.json` exists and every scene has `duration > 0`.

## Step 4 — Build the Cover

```bash
uv run python scripts/build_cover.py --script dist/script.json --out dist/cover
```

This injects the `cover` data + LongCipher logo into the cover template.

**Gate**: `dist/cover/cover.html` exists and references `logos/lc.svg`.

## Step 5 — Build the Video Composition

```bash
uv run python scripts/build_composition.py --script dist/script.json --timings dist/timestamps.json --out dist/video
```

This generates the HyperFrames composition (`index.html`) with:

- One `.scene.clip` per scene, `data-duration` **exactly equal** to the scene's audio duration from `timestamps.json`.
- Branded GSAP entrances (fade + slide, staggered bullets, mono eyebrows).
- A bottom caption `.cap.clip` per scene carrying the exact `narration` text.
- One `<audio class="clip">` per scene pointed at `audio/scene-NN.wav`.

**Gate**: `dist/video/index.html` and `dist/video/hyperframes.json` exist.

## Step 6 — Validate the Composition

```bash
cd dist/video && npx --yes hyperframes lint && npx --yes hyperframes check
```

**Gate**: both commands exit 0 with no errors. If `check` reports layout or contrast issues, fix the generated CSS/scene markup in `build_composition.py` (or the scene data) and rebuild.

## Step 7 — Render & Deliver

1. **Cover image** (renders the cover as a 1s composition, grabs frame 1):

```bash
uv run python scripts/render_cover.py --project dist/cover --output output/cover.png --width 1920 --height 1080
```

2. **Podcast audio**:

```bash
uv run python scripts/render_video.py --audio-only --project dist --output output/podcast_full.mp3
```

3. **Explainer video** (renders the composition, then muxes the podcast track for the cleanest audio):

```bash
uv run python scripts/render_video.py --project dist/video --audio dist/podcast_full.wav --output output/explainer_video.mp4
```

4. **Verify all three**:

```bash
uv run python scripts/verify_media.py output/explainer_video.mp4
uv run python scripts/verify_media.py output/podcast_full.mp3
```

**Gate**: all three files exist in `output/`; `verify_media.py` confirms the MP4 has one `h264` video stream + one audio stream, duration matches `meta.target_seconds` ±5%, and the MP3 is non-empty.

## Delivery

Report the three deliverables to the user:

```text
output/cover.png            # 1920×1080 LongCipher cover
output/podcast_full.mp3     # full narration track, podcast-ready
output/explainer_video.mp4  # 1920×1080 narrated explainer
```

## Implementation Rules

- **Brand fidelity is non-negotiable.** Follow `references/brand-design.md` tokens exactly: `#ffffff` / `#171717` surfaces, ink `#171717`, link blue `#0070f3`, mono eyebrows, weight ceiling 600, 6px radius, shadow-as-border. Never introduce new accent colors.
- **Sync is exact.** Scene `data-duration` must equal the scene audio duration. Animation timelines are absolute, aligned to `timestamps.json`.
- **Caption = narration.** The `.cap` text and the spoken audio must be identical strings.
- **Local-first TTS, no API keys.** Narration defaults to Microsoft Edge Neural TTS (`scripts/edge_tts.py`, no reference voice, needs internet + `uv sync` to install `edge-tts`); the optional local Fun-CosyVoice3-0.5B brand-voice clone runs via `scripts/cosyvoice_tts.py`. Select with `--tts edge|cosyvoice`. The entire pipeline is Python, managed with `uv`; only the HyperFrames CLI (invoked via `npx`) wraps a Node runtime.
- **Local-first.** Reference `logos/lc.svg` from the bundled asset; do not fetch logos or fonts from CDNs at render time.
- **Reuse over rewrite.** Re-run `build_cover.py` / `build_composition.py` after data edits instead of hand-editing generated HTML.
