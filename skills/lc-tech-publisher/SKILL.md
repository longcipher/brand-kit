---
name: lc-tech-publisher
description: Turn an article into a complete LongCipher-branded media package — 4 aspect-ratio cover images (16:9, 9:16, 4:3, 3:4), a two-speaker dialogue podcast MP3, and a LIGHT "fixed-component" narrated explainer video — built with HyperFrames. Use when the user provides an article (technical knowledge content, docs, blog post, paper notes, market/quant brief) and wants cover / podcast / video output in the LongCipher design system. The LLM only writes structured JSON (podcast turns + slide data); all visual styling is hand-built into four fixed component templates (cover card / keypoint / 3-point summary / outro) so visual quality is 100% controlled and reproducible. Narration uses Microsoft Edge Neural TTS by default (two voices — zh-CN-YunxiNeural male + zh-CN-XiaoxiaoNeural female, no API key, no reference voice — needs internet + `pip install edge-tts`); an optional local Fun-CosyVoice3-0.5B backend provides brand-voice cloning. Video + cover render deterministically with npx hyperframes. Outputs land in output/ as cover_*.png, podcast_full.mp3, and explainer_video.mp4. The skill is domain-agnostic: same visual quality for knowledge share or daily digest content.
---

# LongCipher Tech Publisher

You are the LongCipher media production line. Given one article, you produce a branded media package with strict visual fidelity to the LongCipher **light, restrained, technical** design system (see `references/brand-design.md` and the project's `DESIGN.md`).

## Core principle — fixed templates, JSON-only authoring

The LLM **never writes CSS, HTML, or animations**. All visual styling lives in **four hand-built component templates**:

| Template | Role | File |
|---|---|---|
| Cover card | Hero / cover slide 0 + 4-ratio static cover | `assets/templates/cover.html` |
| Keypoint | Single statement / "this is the point" slide | inline in `dashboard.html` (`<section class="slide">` keypoint branch) |
| 3-point summary | Three-up grid card slide | inline in `dashboard.html` (three_points branch) |
| Outro card | Wrap-up / signoff closing slide | inline in `dashboard.html` (outro branch) |
| Video master | Timeline orchestrator embedding all 5 slide types + captions + audio | `assets/templates/dashboard.html` |
| Shorts | Vertical 9:16 reel from cover + slide feed | `assets/templates/shorts.html` |

The LLM only outputs structured JSON (title, key points, TTS text, color theme name). Every video looks like every other video in the LongCipher system — visual fidelity is **100% controlled**, debugging cost is **near-zero**, and a brand designer can re-skin everything by editing CSS variables (`--accent`, `--ink`, `--canvas`) in one place.

The package is **domain-agnostic**: visual quality is identical whether the source is a knowledge-share deep dive or a daily multi-item digest. Content-specific flavor lives only in the LLM-authored JSON copy.

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

2. **You** (the agent) now write `dist/script.json` — this is the creative core. Use the outline, the article, and `references/brand-design.md` (voice, tone) to produce a **two-speaker dialogue** plus an ordered list of **slide components**. Each slide is exactly one of the four fixed component types:

```jsonc
{
  "meta": {
    "title": "Article headline",
    "subtitle": "One-line thesis",
    "kicker": "STRUCTURE BRIEF",          // mono eyebrow, uppercase
    "lang": "zh",                          // primary language of the script
    "target_seconds": 100,
    "mode": "knowledge",                   // "knowledge" (single-topic deep dive) or "digest" (multi-item daily brief)
    "roles": {                             // zh speaker display names + voices
      "male": "主讲",  "female": "主持",
      "maleVoice": "zh-CN-YunxiNeural",
      "femaleVoice": "zh-CN-XiaoxiaoNeural"
    },
    "enVoice": "en-US-AndrewNeural",       // single EN voice for BOTH speakers
    "enRoles": { "male": "Host", "female": "Co-host" }
  },

  "cover": {
    "kicker": "STRUCTURE BRIEF",
    "title": "Cover headline (\\n for line breaks)",
    "subtitle": "Cover one-liner",
    "cornerTag": "BRIEF",
    "metaLeft": "LongCipher Research · Daily Brief",
    "metaRight": "{{DATE}}",             // e.g. 2026-08-13; the builder drops any issue number
    "headlines": [                          // 4–10 today's focus items (data-driven, topic-agnostic)
      "First key point of today's brief",
      "Second structural signal",
      "Third capital/macro theme",
      "Fourth regulatory or product angle"
    ]
  },

  "podcast": [                              // THE SPINE: two-speaker dialogue
    { "id": "01", "speaker": "male",   "emotion": "calm",     "text": "今天我们来聊…" },
    { "id": "02", "speaker": "female", "emotion": "curious",  "text": "那这个到底是什么意思？" },
    { "id": "03", "speaker": "male",   "emotion": "emphatic", "text": "简单来说…" }
  ],

  "slides": [                               // ordered visual components (see types below)
    { "type": "keypoint",
      "eyebrow": "核心逻辑",
      "icon": "cube",                        // cute flat illustration key (see catalog)
      "statement": "价格只是横盘,真正收紧的是三条逻辑链。",
      "support": "算力去周期化 · 机构化 · 利率锚定",
      "analysis": "真正的问题不在价格,而在现金流:谁能把算力卖成稳定收入,谁就拿到下一轮定价权。",
      "callback": ["呼应开头:宏观利率压力正是矿企抛币的推手"] },

    { "type": "three_points",
      "title": "今日三条主线",
      "icon": "net",
      "points": [
        { "no": "01", "title": "算力去周期化", "body": "矿工费占比创十年新低,收益结构转向算力 + AI 租赁。" },
        { "no": "02", "title": "机构化",        "body": "ETF 与储备模型把算力资产纳入受审计的资产负债表。" },
        { "no": "03", "title": "利率锚定",      "body": "代币化美债把链上收益锚定为无风险利率。" }
      ] },

    { "type": "keypoint",
      "eyebrow": "一句话结论",
      "statement": "价格牛熊只是表层,现金流才是资产。",
      "support": "" },

    { "type": "outro",
      "recap": "今天我们拆了算力去周期化、机构化与利率锚定三条链,以及它们如何在 GPU 期货处汇合。",
      "signoff": "LongCipher · 每日研究简报" }
  ]
}
```

**Dialogue rules:**

- `podcast[]` is the spine. Each turn is `{ id, speaker: "male"|"female", text }`. The `speaker` drives which TTS voice (male = `roles.maleVoice`, female = `roles.femaleVoice`) and the caption color (left-border tint).
- Male = confident explainer (老高式); female = curious questioner (小茉式). Write natural back-and-forth, not monologue split in half.
- **Length gate (hard rule — do not under-fill).** Edge TTS speaks zh at **~5.3–5.7 chars/sec** (measured), NOT the old 3.2–3.6 estimate. Author to the real rate so the video actually reaches `target_seconds`:
  - zh: `total_chars ≈ target_seconds × 5.5`. For an **11 min (660s)** video write **≥ 3600 zh chars**; for 12 min (720s) write **≥ 3900 zh chars**. A 2000–2400-char script only yields ~6–7 min — that is a failed gate.
  - en: `total_words ≈ target_seconds × 2.2`. For 11 min write **≥ 1450 words**.
  - After `generate_audio.py`, confirm `speaker_timestamps[_en].json.total` ≥ `target_seconds × 0.9`; if short, **expand facts inside existing turns** (never filler) and re-run until the gate passes.

**Anti-"AI flavor" dialogue rules (top user complaint — read before writing ANY turn):**

1. **Vary sentence rhythm.** No two adjacent turns may be the same length. Alternate a short punchy reaction (1–2 clauses) with a longer explanation. Uniform paragraph-blocks read as TTS.
2. **Emotional beats.** Tag every turn with an optional `emotion` from the catalog (`neutral/calm/serious/curious/excited/surprised/warm/doubtful/relieved/emphatic`). Map it to the *content*, not decoration: a surprising number → `surprised`, a regulator setback → `serious`, a conclusion → `emphatic`. The TTS engine shifts pacing per turn — uniform pacing is the #1 "AI voice" tell.
3. **Spoken, not written.** Use short sentences, dashes, rhetorical questions, and light fillers ("说白了", "注意这里", "有意思的是"). Ban essay-language: no "综上所述", "值得注意的是", no balanced-clause formality. If it looks like it could be a press release, rewrite it.
4. **Female co-host reacts, doesn't just ask.** Every 2–3 male turns, she must react emotionally (surprise, doubt, a "wait, really?" beat) or *link back* ("这和我们开头说的零售数据是一条逻辑"). Not every female turn is a question.
5. **One fact, then the story.** Each chapter: lead with the concrete fact/number, then the *so-what* — what it means, who it affects, why it's worth caring about. Facts alone are a newswire; the so-what is the podcast.

**Slide fields (anti-AI-flavor visual layer):**

- `icon`: pick a cute flat illustration key from the catalog (`shield/rocket/chart/coins/cube/atom/bolt/net/lock/spark/pick/scale/bot/bank/handshake/trend/gauge/layers/flow`). The template owns the SVG; you only pick. Matches the chapter's topic (e.g. miner chapter → `pick`, macro → `chart`, post-quantum → `atom`, growth → `trend`/`gauge`, matrix → `layers`, process → `flow`).
- `analysis`: a 1–2 sentence so-what line rendered as a distinct "分析 / SO-WHAT" chip under the bullets. Must be a *specific* inference tied to the numbers above — never a generic slogan.
- `callback`: one or more short strings that connect this chapter to another (e.g. `"呼应开头:零售 -0.6% 的宏观压力"`). Rendered as small `↳` tags — this is the visible "information linking" layer.

**Slide rules:**

- `slides[]` is an ordered list of full-frame visual slices. The builder auto-distributes them across `[HERO_DURATION, total_audio]` evenly when `_start`/`_end` are absent. If the last slide is not `outro`, one is auto-appended.
- Slide types (matching the hand-built templates). **Pick by the copy's semantics, not the name** — a metric should be a `chart`/`counter`, a feature matrix a `cards`, a process a `steps`, never plain text (see `references/script-schema.md` §"Semantic-to-visual mapping"):
  - `keypoint` — single statement with eyebrow + optional mono `support`. Use for thesis, definitions, "one-line conclusions". Wrap the key word in `**…**` for a kinetic-typography highlight (L3). Optionally set `visual` to one of the five visualizer keys to render a right-column dynamic card (40/60 two-column layout).
  - `three_points` — exactly 3 points, each with `no`, `title`, `body`. Use for "今日三条主线" / "three takeaways".
  - `chart` — animated dither bar chart: `bars[]` each `{ label, value, suffix? }`, optional `max`. Use for growth/comparison/ranking ("效率提升 10 倍", "A 是 B 的 3 倍"). Bars grow + value counters roll (L2).
  - `counter` — big animated metric: `value`, `label`, optional `prefix`/`suffix`/`delta`/`eyebrow`/`note`. Use for a single headline metric ("收入达 $5M"). The number rolls up (L2).
  - `cards` — 3D card spread: `cards[]` each `{ no?, title, body }`. Use for feature/capability matrices ("支持三大平台"). Cards fan out (L2).
  - `steps` — process/flow: `steps[]` each `{ no?, title, body }`. Use for "输入 → 分析 → 输出" pipelines. Connecting line draws in, nodes pulse (L2).
  - `metric_chart` — animated SVG line chart: `chart` `{ points[], labels[], unit?, max? }`. Use for price / TVL / on-chain balance trends. Polyline draws in, latest point breathes a halo (L2).
  - `pipeline` — node/data-flow diagram: `pipeline` `{ nodes[], links[]? }`. Use for infra / MEV / protocol pipelines (Sequencer → Builder → Proposer). Nodes light up, data packets pulse (L2).
  - `benchmark` — horizontal comparison bars: `benchmark` `{ bars[] {label,value,suffix?}, unit? }`. Use for AI speed (tok/s) or TPS (1M+ TPS). Bars fill with count-up values (L2).
  - `security` — CVSS gauge + port warning: `security` `{ cvss, ports[]?, pulse?, note? }`. Use for vulnerabilities / security events. Arc draws, needle rotates, pulse ring (L2).
  - `terminal` — dark code block: `terminal` `{ lines[], title? }`. Use for Rust / smart-contract releases. Lines type in with a caret (L2).
  - `outro` — closing card with `recap` + `signoff`. Use for wrap-up. **Required as last slide** (auto-appended if missing).

**The `visual` field** (content-aware right-column visualizer): any `keypoint`
may set `visual` to `metric_chart` / `pipeline` / `benchmark` / `security` /
`terminal`, with the data in a sibling field of the same name. This turns the
slide into a 40/60 two-column layout (text left, dynamic visual card right) —
the recommended way to pair a takeaway with its supporting data. The same five
visualizers are also standalone slide types when the visual is the chapter hero.
- `cover.headlines[]` (4 items) raises cover information density so daily covers look different.

**Content direction (two modes, see `references/brand-design.md` §9):**

- `"mode": "knowledge"` — single-topic deep dive. Cover title is a thesis. Slides build the argument: thesis → three pillars → one-line conclusion → outro.
- `"mode": "digest"` — daily multi-item brief. Cover title is a date/issue. Slides are per-item keypoints and 3-point summaries.

**Bilingual output (zh + en videos):** the skill emits **two** videos — the primary language plus an English version. Author English variants alongside the zh ones:

```jsonc
"coverEn":   { "kicker": "EN BRIEF", "title": "Cover headline (EN)", "subtitle": "…", "headlines": […] },
"podcastEn":[ { "id": "01", "speaker": "male", "text": "Let's talk about…" }, … ],
"slidesEn":  [ /* same shape as slides[], English copy */ ]
```

- The EN video uses **one** English voice for both speakers: `meta.enVoice` (default `en-US-AndrewNeural`).
- Every build script accepts `--lang zh|en` and writes to a language-specific tree so the two passes never collide:
  - audio → `dist/audio/` vs `dist/audio_en/`; timings → `dist/speaker_timestamps.json` vs `dist/speaker_timestamps_en.json`; covers → `dist/cover/` vs `dist/cover_en/`; video → `dist/video_zh/` vs `dist/video_en/`.
- If an `En` variant is omitted, the builder falls back to the zh content (with a warning) so the pipeline still runs.

3. Validate the schema:

```bash
uv run python scripts/parse_article.py --validate dist/script.json
```

**Gate**: validation passes with no errors; `podcast[]` non-empty; every turn has `speaker` ∈ {male, female} and non-empty `text`; `slides[]` contains valid types only.

## Step 3 — Generate Dialogue Audio & Timings

Dialogue is synthesized with the **Edge Neural TTS backend by default** (two built-in voices: `zh-CN-YunxiNeural` male + `zh-CN-XiaoxiaoNeural` female, free, no API key, no reference voice — needs `pip install edge-tts` + internet). Pass `--tts cosyvoice` to switch to the local **Fun-CosyVoice3-0.5B** brand-voice clone. See `references/tts.md` for setup.

Default (Edge) — run **twice**, once per language:

```bash
uv run python scripts/generate_audio.py --script dist/script.json --lang zh --out dist
uv run python scripts/generate_audio.py --script dist/script.json --lang en --out dist
```

Optional (CosyVoice3, single cloned voice for both speakers):

```bash
uv run python scripts/generate_audio.py --script dist/script.json --tts cosyvoice \
    --prompt-wav "$COSYVOICE_PROMPT_WAV" --prompt-text "$COSYVOICE_PROMPT_TEXT" \
    --speed 1.0 --lang zh --out dist
```

This produces `dist/audio[_en]/turn-NN.wav`, copies to `dist/video[_en]/audio/turn-NN.wav`, `dist/speaker_timestamps[_en].json` (per-turn `start`/`end`/`duration` + speaker + voice — the absolute timeline), and `dist/podcast_full[_en].wav`.

**Gate**: `dist/speaker_timestamps.json` and `dist/speaker_timestamps_en.json` exist; every turn has `duration > 0`; **`total` ≥ `meta.target_seconds × 0.9`** for both languages (e.g. ≥ 594s for an 11-min target). If a language is short, expand facts inside existing turns and re-run — do not ship a sub-11-minute long video.

## Step 4 — Build the Covers (4 aspect ratios × 2 languages)

```bash
uv run python scripts/build_cover.py --script dist/script.json --lang zh --out dist/cover
uv run python scripts/build_cover.py --script dist/script.json --lang en --out dist/cover_en
```

Each run emits **four** ratio-aware cover HTML files + `logos/lc.svg` + a `manifest.json` map (rendered from the same `cover.html` template, with `--scale` adjusted per ratio).

**Gate**: `dist/cover/cover_*.html` and `dist/cover_en/cover_*.html` (4 files each) exist, `logos/lc.svg` present in both, `manifest.json` present in both.

## Step 5 — Build the Video Compositions

```bash
uv run python scripts/build_composition.py --script dist/script.json --lang zh --out dist/video
uv run python scripts/build_composition.py --script dist/script.json --lang en --out dist/video_en
```

Each run generates a **light LongCipher** HyperFrames composition (`index.html`) from `speaker_timestamps[_en].json` and the matching slides[]:

- Persistent background: calm hairline grid + faint watermark.
- Hero intro clip (0 → `HERO_DURATION`, default 4s) using the cover template.
- Slides 1..n are auto-injected from `script.json slides[]` (zh `slides[]` / en `slidesEn[]`) — each is a HyperFrames `clip` with its own `data-start`/`data-duration` window, evenly distributed across the remaining timeline.
- One bottom caption `.cap.clip` per dialogue turn, identical to the spoken line, multi-line allowed (no clipping).
- One `<audio class="clip">` per turn pointed at `audio/turn-NN.wav`.
- `window.LC_DATA` carries turns / slides / cover; `{{DURATION}}` = total audio + 0.5s tail.

**Gate**: `dist/video_zh/index.html` + `dist/video_zh/hyperframes.json` and `dist/video_en/index.html` + `dist/video_en/hyperframes.json` exist.

## Step 6 — Validate the Compositions

```bash
cd dist/video_zh && npx --yes hyperframes lint && npx --yes hyperframes check
cd dist/video_en && npx --yes hyperframes lint && npx --yes hyperframes check
```

**Gate**: both commands exit 0 with no errors. If `check` reports layout or contrast issues, fix the generated markup in `assets/templates/dashboard.html` / `cover.html` (or the slide data) and rebuild.

## Step 7 — Render & Deliver

1. **Cover images** — both language sets, four ratios each:

```bash
for lang in "" _en; do
  for r in 16x9 9x16 4x3 3x4; do
    uv run python scripts/render_cover.py --project "dist/cover$lang" \
      --name "cover_$r" --output "output/cover$lang_$r.png"
  done
done
```

2. **Podcast audio** (zh + en):

```bash
uv run python scripts/render_video.py --audio-only --lang zh --project dist --output output/podcast_full.mp3
uv run python scripts/render_video.py --audio-only --lang en --project dist --output output/podcast_full_en.mp3
```

3. **Explainer videos** (renders each composition, muxes its dialogue track):

```bash
uv run python scripts/render_video.py --project dist/video_zh --audio dist/podcast_full.wav     --output output/explainer_video_zh.mp4
uv run python scripts/render_video.py --project dist/video_en --audio dist/podcast_full_en.wav --output output/explainer_video_en.mp4 --lang en
```

4. **Verify all the pieces**:

```bash
uv run python scripts/verify_media.py output/explainer_video_zh.mp4
uv run python scripts/verify_media.py output/explainer_video_en.mp4
uv run python scripts/verify_media.py output/podcast_full.mp3
uv run python scripts/verify_media.py output/podcast_full_en.mp3
```

**Gate**: all deliverables exist in `output/`; `verify_media.py` confirms each MP4 has one `h264` video stream + one audio stream, duration matches `meta.target_seconds` ±10%, and the MP3s are non-empty.

## Step 7b — Render Vertical Shorts (9:16, ≤10s, scrolling feed)

A second visual for short-form platforms (TikTok / Reels / Shorts). Same brand, vertical canvas, no narration, curated scrolling feed of the top-N headlines over a fixed background music track.

```bash
# Build the composition (zh + en)
uv run python scripts/build_shorts.py --script dist/script.json --lang zh --out dist/shorts_zh
uv run python scripts/build_shorts.py --script dist/script.json --lang en --out dist/shorts_en

# Lint + check (88/88 contrast pass WCAG AA, 0 errors)
cd dist/shorts_zh && npx --yes hyperframes check && cd ../..
cd dist/shorts_en && npx --yes hyperframes check && cd ../..

# Render — reuses render_video.py; the per-scene audio (the BGM clip baked
# into the index.html) is muxed automatically, no --audio needed.
uv run python scripts/render_video.py --project dist/shorts_zh --output output/shorts_zh.mp4
uv run python scripts/render_video.py --project dist/shorts_en --output output/shorts_en.mp4
```

**Gate**: `output/shorts_zh.mp4` and `output/shorts_en.mp4` exist, 1080×1920, 30fps, duration exactly 10.0s, ≤2MB each, with one AAC audio stream carrying the BGM.

**Design notes**:
- The fixed BGM (`assets/audio/shorts_bgm.mp3`, 10s, 161KB, layered 220+277+329Hz sine pad with limiter + fade) is shipped with the skill and reused across every article — no per-article audio work.
- The feed is **curated**, not exhaustive: 6 top-priority headlines (sorted by `cover.headlines` order). For longer articles, adjust with `--feed-count N`.
- The feed scrolls at a steady velocity (linear `ease: "none"`), start 1.0s, end ~9.0s — the last card holds visibly until the end-of-video fade.
- A mask gradient on the feed-viewport fades cards in/out at the top and bottom edges so cards enter/exit cleanly.

## Delivery

Report the deliverables to the user:

```text
output/cover_16x9.png        # zh landscape cover
output/cover_9x16.png        # zh portrait/story cover
output/cover_4x3.png         # zh standard cover
output/cover_3x4.png         # zh portrait cover
output/cover_en_16x9.png     # en landscape cover
output/cover_en_9x16.png     # en portrait/story cover
output/cover_en_4x3.png      # en standard cover
output/cover_en_3x4.png      # en portrait cover
output/podcast_full.mp3      # zh two-speaker dialogue, podcast-ready
output/podcast_full_en.mp3   # en dialogue (en-US-AndrewNeural), podcast-ready
output/explainer_video_zh.mp4    # zh 1920×1080 narrated light video
output/explainer_video_en.mp4    # en 1920×1080 narrated light video
output/shorts_zh.mp4         # zh 1080×1920 vertical scrolling feed (10s, BGM)
output/shorts_en.mp4         # en 1080×1920 vertical scrolling feed (10s, BGM)
```

## Implementation Rules

- **Brand fidelity is non-negotiable.** Follow `references/brand-design.md` tokens exactly: light canvas `#fafbfc`, surface `#ffffff`, ink `#171718`, single brand blue `#0a72ef`, 2px ceiling on corner radius (no pills), shadow-as-border (layered `box-shadow`), DM Sans + JetBrains Mono. Never introduce a second hue. Keep the `lc.svg` mark as a low-opacity brand watermark.
- **LLM writes JSON only.** Never author CSS, HTML, or animations. Add new visual variants by extending `cover.html` / `dashboard.html` (and its inline slide branches), not by generating ad-hoc styles from the LLM.
- **Domain-agnostic.** Same visual quality for any content. The LLM's job is the copy; the templates' job is the look.
- **Sync is exact.** Caption/audio element `data-duration` equals the turn audio duration from `speaker_timestamps.json`. Slide `data-start`/`data-duration` align to the same absolute timeline. Animation is compositor-only (transform/opacity), never layout-thrashing props.
- **Caption = spoken text.** The `.cap` text and the spoken audio must be identical strings.
- **Local-first TTS, no API keys.** Dialogue defaults to Microsoft Edge Neural TTS (two built-in voices, no reference voice, needs internet + `uv sync` to install `edge-tts`); the optional local Fun-CosyVoice3-0.5B brand-voice clone runs via `scripts/cosyvoice_tts.py`. Select with `--tts edge|cosyvoice`.
- **Fonts are local-ish but CDN-loaded for render.** The light template loads DM Sans + JetBrains Mono from Google Fonts CDN. For production, bundle `.woff2` files into `assets/fonts/` and switch the `<link>` to a `@font-face` declaration.
- **Reuse over rewrite.** Re-run `build_cover.py` / `build_composition.py` after data edits instead of hand-editing generated HTML.