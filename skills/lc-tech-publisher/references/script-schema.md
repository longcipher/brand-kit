# script.json Schema (fixed-template, JSON-only authoring)

The LLM's **only** creative artifact is `script.json`. It must contain **no
CSS, no class names, no inline styles** — only structured data that the 4 fixed
component templates consume. Visual fidelity is guaranteed by the templates
(`references/brand-design.md`).

## Top level

```jsonc
{
  "meta": {
    "title": "Article / episode headline",
    "subtitle": "One-line thesis",
    "kicker": "DAILY BRIEF",             // mono eyebrow, uppercase
    "lang": "zh",                        // primary language
    "mode": "knowledge",                 // "knowledge" | "digest"
    "brand": "LongCipher",
    "date": "{{DATE}}",                  // any YYYY-MM-DD; surfaced on the cover, replaces any issue_no
    "issue_no": "No.028",                // OPTIONAL & IGNORED — the builder discards it; do not rely on it
    "roles": { "male": "主讲", "female": "主持" },
    "enRoles": { "male": "Host", "female": "Co-host" },
    "maleVoice": "zh-CN-YunxiNeural",
    "femaleVoice": "zh-CN-XiaoxiaoNeural",
    "enVoice": "en-US-AndrewNeural"
  },

  // Cover (component 1). Headlines raise cover information density.
  // All strings are placeholders — replace with the actual article's content.
  "cover": {
    "kicker": "STRUCTURE BRIEF",
    "title": "{{TITLE}}",                  // \n = line break
    "subtitle": "{{ONE_LINE_THESIS}}",
    "cornerTag": "{{DATE}}",               // builder falls back to date if value looks like an issue no.
    "metaLeft": "LongCipher Research · Daily Brief",
    "metaRight": "{{DATE}}",               // issue numbers are dropped automatically
    "headlinesLabel": "TODAY'S FOCUS",     // optional; neutral default if omitted
    "headlines": [                         // 4–10 concise bullets (analysis, not price)
      "{{focus item 1}}",
      "{{focus item 2}}"
    ]
  },

  // Optional English variants (the builder falls back to zh if omitted).
  "coverEn":  { "kicker": "EN BRIEF", "title": "...", "subtitle": "...", "headlines": [...] },

  // THE SPINE: two-speaker dialogue (老高/小茉 style). One turn per beat.
  "podcast": [
    { "id": "01", "speaker": "male",   "text": "..." },
    { "id": "02", "speaker": "female", "text": "..." }
  ],
  "podcastEn": [ { "id": "01", "speaker": "male", "text": "..." } ],

  // Ordered visual slides — each maps to ONE fixed component.
  "slides": [
    { "type": "keypoint",  "eyebrow": "核心逻辑",
      "statement": "价格只是横盘,真正收紧的是三条逻辑链。",
      "support": "算力去周期化 · 机构化 · 利率锚定" },
    { "type": "three_points", "title": "今日三条主线",
      "points": [
        { "no": "01", "title": "算力去周期化", "body": "..." },
        { "no": "02", "title": "机构化",       "body": "..." },
        { "no": "03", "title": "利率锚定",     "body": "..." }
      ] },
    { "type": "keypoint",  "eyebrow": "一句话结论",
      "statement": "价格牛熊只是表层,现金流才是资产。",
      "support": "" },
    { "type": "table", "title": "{{TABLE_TITLE}}",
      "head": ["项目", "轮次/类型", "金额", "要点"],
      "numCols": [2],
      "rows": [
        ["{{item}}", "{{round}}", "{{amount}}", "{{note}}"],
        ["{{item}}", "{{round}}", "{{amount}}", "{{note}}"]
      ] },
    { "type": "outro", "recap": "今天我们拆了算力、机构与代币化的三条链。",
      "signoff": "LongCipher · 每日研究简报" }
  ]
}
```

## Slide component types (must be one of these)

Every slide may also carry these **anti-AI-flavor** fields:
- `icon` — a key from the fixed cute-illustration catalog (`shield/rocket/chart/coins/cube/atom/bolt/net/lock/spark/pick/scale/bot/bank/handshake/trend/gauge/layers/flow`). The template owns the SVG art; you only pick a topic-matching key. Unknown keys fall back to `spark`.
- `analysis` — 1–2 sentence so-what line, rendered as a distinct "分析 / SO-WHAT" chip under the bullets. Must be a *specific* inference tied to that chapter's numbers, never a generic slogan.
- `callback` — string or array of short strings linking this chapter to another, rendered as small `↳` tags (the visible information-connection layer). Example: `"呼应开头:零售 -0.6% 的宏观压力"`.

| `type` | Required fields | Renders via |
|--------|----------------|-------------|
| `keypoint` | `statement` (string, ≤ ~40 chars), optional `eyebrow`, optional `support`, optional `bullets[]` (3–5 short fact lines shown as a structured list under the statement), optional `icon`/`analysis`/`callback`, optional `visual` (see below — renders a right-column dynamic visualizer, turning the slide into a 40/60 two-column layout), optional `audioFrom`/`audioTo` (turn ids binding the slide to a narration chapter) | inline in `dashboard.html` (keypoint branch) |
| `three_points` | `points[3]` each `{ no, title, body }`, optional `title`, optional `icon`, optional `audioFrom`/`audioTo` | inline in `dashboard.html` (three_points branch) |
| `table` | `head[≥2]` (string column headers), `rows[]` (each row must have the same cell count as `head`), optional `numCols` (array of 0-based column indices rendered right-aligned in mono blue), optional `title`, optional `icon`, optional `audioFrom`/`audioTo` | inline in `dashboard.html` (table branch) |
| `chart` | `bars[]` each `{ label, value, suffix? }` (2–6 bars), optional `max` (y-axis ceiling; auto-computed if omitted), optional `title`, optional `icon`/`analysis`, optional `audioFrom`/`audioTo` | inline in `dashboard.html` (chart branch) |
| `counter` | `value` (number), `label` (string), optional `prefix`/`suffix`, optional `delta` (e.g. `"+300%"`), optional `eyebrow`, optional `note`, optional `icon`/`analysis`, optional `audioFrom`/`audioTo` | inline in `dashboard.html` (counter branch) |
| `cards` | `cards[]` each `{ no?, title, body }` (2–4 cards), optional `title`, optional `icon`, optional `audioFrom`/`audioTo` | inline in `dashboard.html` (cards branch) |
| `steps` | `steps[]` each `{ no?, title, body }` (2–5 steps), optional `title`, optional `icon`, optional `audioFrom`/`audioTo` | inline in `dashboard.html` (steps branch) |
| `metric_chart` | `chart` = `{ title?, unit?, points[] (numbers), labels[] (x-axis), max? }`, optional `title`, optional `icon`/`analysis`, optional `audioFrom`/`audioTo` | inline in `dashboard.html` (metric_chart branch) |
| `pipeline` | `pipeline` = `{ title?, nodes[] (strings), links[]? (edge labels) }`, optional `title`, optional `icon`/`analysis`, optional `audioFrom`/`audioTo` | inline in `dashboard.html` (pipeline branch) |
| `benchmark` | `benchmark` = `{ title?, unit?, bars[] each { label, value, suffix? } }`, optional `title`, optional `icon`/`analysis`, optional `audioFrom`/`audioTo` | inline in `dashboard.html` (benchmark branch) |
| `security` | `security` = `{ title?, cvss (0–10), ports[]?, pulse?, note? }`, optional `title`, optional `icon`/`analysis`, optional `audioFrom`/`audioTo` | inline in `dashboard.html` (security branch) |
| `terminal` | `terminal` = `{ title?, lines[] (strings; `$`-prefixed = command, `>`-prefixed = output) }`, optional `title`, optional `icon`/`analysis`, optional `audioFrom`/`audioTo` | inline in `dashboard.html` (terminal branch) |
| `outro` | `recap` (string), optional `signoff`, optional `icon`, optional `audioFrom`/`audioTo` | inline in `dashboard.html` (outro branch) |

### The `visual` field (content-aware right-column visualizer)

Any `keypoint` slide may set `visual` to one of the five visualizer keys. When set,
the slide becomes a **two-column layout**: left 40% = the text (statement, bullets,
analysis, callbacks), right 60% = the dynamic visual card. The visualizer data lives
in a sibling field named after the key:

| `visual` | Data field | Visual treatment |
|----------|-----------|------------------|
| `metric_chart` | `chart` | SVG line chart — polyline draws in left→right, area fades, data dots pop, value labels count up, latest point breathes a halo |
| `pipeline` | `pipeline` | Node/data-flow diagram — nodes light up in sequence, a data packet pulses along each link |
| `benchmark` | `benchmark` | Horizontal comparison bars — fill left→right with count-up values (AI tok/s, TPS) |
| `security` | `security` | CVSS semicircular gauge — arc draws, needle rotates, score counts up, pulse ring + port chips |
| `terminal` | `terminal` | Dark terminal window — lines type in with a blinking caret (Rust / smart-contract releases) |

Example — a keypoint with a right-column line chart:

```jsonc
{ "type": "keypoint", "eyebrow": "行情", "icon": "trend",
  "statement": "链上余额持续累积。",
  "visual": "metric_chart",
  "chart": { "title": "BTC 链上余额", "unit": "万 BTC",
             "points": [62, 64, 61, 66, 68, 70], "labels": ["M1","M2","M3","M4","M5","M6"] },
  "analysis": "余额累积反映长期持有者惜售。",
  "bullets": ["矿工持仓 119.19 万 BTC", "交易所净流出持续"] }
```

The same five visualizers are also available as **standalone slide types**
(`metric_chart` / `pipeline` / `benchmark` / `security` / `terminal`) that fill the
whole content area — use those when the visual is the hero of the chapter rather
than a supporting card.

### Semantic-to-visual mapping (the 4-layer visual stack)

Pick the slide type that matches the *semantic* of the copy, not the template name.
This is the core anti-"PPT" rule — a metric should render as a **chart/counter**, a
feature matrix as **cards**, a process as **steps**, never as plain text:

| Copy semantics | Preferred slide type | Visual treatment |
|----------------|---------------------|------------------|
| Growth / metric ("效率提升 10 倍", "收入达 $5M") | `counter` or `chart` | number rolls up + bars grow (L2) over the breathing atmosphere (L0) |
| Comparison / ranking ("A 是 B 的 3 倍") | `chart` | animated dither bars + value counters |
| Feature / capability matrix ("支持三大平台") | `cards` | 3D card spread fans out |
| Process / architecture ("输入 → 分析 → 输出") | `steps` | connecting line draws in, nodes pulse |
| Price / TVL / on-chain balance trend | `metric_chart` (or `keypoint` + `visual:"metric_chart"`) | SVG line chart draws in, latest point breathes a halo |
| Infra / MEV / protocol pipeline (Sequencer → Builder → Proposer) | `pipeline` (or `keypoint` + `visual:"pipeline"`) | nodes light up, data packets pulse along links |
| AI speed / TPS benchmark ("140 tok/s", "1M+ TPS") | `benchmark` (or `keypoint` + `visual:"benchmark"`) | horizontal bars fill with count-up values |
| Vulnerability / security event (CVSS 9.8, exposed ports) | `security` (or `keypoint` + `visual:"security"`) | CVSS gauge draws, needle rotates, pulse ring + port chips |
| Code / release / smart-contract deploy | `terminal` (or `keypoint` + `visual:"terminal"`) | dark terminal types lines in with a caret |
| Breakthrough / pain-point flip ("毫秒级响应") | `keypoint` + `**keyword**` | kinetic typography highlight (L3) |
| Thesis / one-line conclusion | `keypoint` | statement + bullets + analysis chip |

**Kinetic typography (L3):** wrap the word that carries the semantic weight in
`**double asterisks**` inside any `statement` / `bullets` / `support` / `analysis`
string. The template renders it as a highlighted accent span (brand-blue underline
+ soft chip). Use it sparingly — one or two keywords per slide, never whole lines.

**Icon keys** (extended catalog): `shield/rocket/chart/coins/cube/atom/bolt/net/
lock/spark/pick/scale/bot/bank/handshake/trend/gauge/layers/flow`. Match the topic:
growth → `trend`/`gauge`, matrix → `layers`, process → `flow`, miner → `pick`,
macro → `chart`, post-quantum → `atom`. Unknown keys fall back to `spark`.

### Keeping the center zone in sync with the narration

The center (static) zone is the **primary** information surface — the viewer should
understand the current topic from it alone, without reading the caption. To make a
slide switch exactly when its narration chapter begins/ends, set `audioFrom` and
`audioTo` to the first/last `podcast[].id` of that chapter. `build_composition.py`
then pins the slide's on-screen window to that audio span instead of evenly
splitting total duration. Without the hints, slides are distributed evenly (the
old behavior, which let the center text lag behind the spoken topic).

Each `keypoint` should therefore carry the **concrete numbers and claims** of its
chapter in `bullets[]` (and a `statement` that is a specific takeaway, not a
generic motto). Generic "金句"-only slides force the viewer back to the caption.

The **cover** is component 1 (`cover.html`) and also serves as the video's
hero slide — it is not listed in `slides[]`; the builder always opens the video
with the cover, then plays `slides[]`, then ends on `outro` (auto-appended if the
last slide isn't an `outro`). Use the `table` slide whenever you have comparable
figures (funding rounds, metrics, rankings) — a real data table reads far more
credibly than prose and keeps the screen's static document zone information-dense.

## Dialogue rules

- `podcast[]` is an ordered array `{ id, speaker: "male"|"female", text, emotion? }`.
  `speaker` drives the TTS voice and the caption accent.
- Male = confident explainer (老高式); female = curious questioner (小茉式).
  Natural back-and-forth, not a monologue split in half.
- Female inserts a real question/reaction every 2–3 male lines.
- Keep emotion/price-panic out; favor mechanism, logic chains, deeper causes.
- **Length gate (hard rule — do not under-fill).** Edge TTS speaks zh at
  **~5.3–5.7 chars/sec** (measured), NOT the old 3.0–3.4 estimate. Author the
  dialogue to the **real** rate so the video actually reaches `target_seconds`:
  - zh: `total_chars ≈ target_seconds × 5.5`. For an **11 min (660s)** video
    write **≥ 3600 zh chars**; for 12 min (720s) write **≥ 3900 zh chars**.
    A 2000–2400-char script only yields ~6–7 min — that is a failed gate.
  - en: `total_words ≈ target_seconds × 2.2`. For 11 min write **≥ 1450 words**.
  - After `generate_audio.py`, check `speaker_timestamps[_en].json.total` ≥
    `target_seconds × 0.9`; if short, **expand facts inside existing turns**
    (never add filler) and re-run until the gate passes.

### `emotion` — per-turn emotional pacing (anti-AI-flavor)

Each turn may set `emotion` from a fixed catalog. It drives a **per-turn speech-rate
shift** (Edge TTS), so the narration breathes instead of reading at a constant
machine pace. Map the emotion to the *content*, not decoration:

| emotion | Effect | Use when… |
|---------|--------|-----------|
| `neutral` | baseline | default, bridge turns |
| `calm` | -4% slower | opening, settling a topic |
| `serious` | -5% slower | regulators, hacks, losses |
| `curious` | -1% | co-host asking |
| `excited` | +5% faster | a surprising win, a milestone |
| `surprised` | +4% | a genuinely unexpected number |
| `warm` | -3% | soft framing, human angle |
| `doubtful` | -2% | skepticism, "wait, really?" |
| `relieved` | -2% | a tension resolved |
| `emphatic` | -6% slower | the conclusion / punch line |

Rules:
- **Vary adjacent turns** — never two `neutral` in a row on the same pacing.
- Prefer `serious`/`emphatic` for the last turn of a chapter (weight), and
  `excited`/`surprised` on the beat that deserves it.
- A turn may instead set an explicit `rate` string (e.g. `"-6%"`), which wins
  over the emotion mapping.
- Uniform pacing is the #1 "AI voice" tell — vary it by emotion on every chapter.

### Anti-AI-flavor writing (top user complaint)

1. **Short + long alternation.** No two adjacent turns the same length. Mix a
   punchy 1–2 clause reaction with a longer explainer.
2. **Spoken, not written.** Short sentences, dashes, rhetorical questions, light
   fillers ("说白了", "注意", "有意思的是"). Ban press-release prose
   ("综上所述", balanced clauses).
3. **React, don't just ask.** The female co-host reacts emotionally or links
   back to an earlier chapter; not every turn is a question.
4. **One fact, then the story.** Lead with the concrete number, then the
   so-what (what it means, who it affects). Facts alone are a newswire.

## Bilingual output

Author `coverEn`, `podcastEn` alongside zh. The EN video uses **one** English
voice (`meta.enVoice`) for both speakers; both `podcastEn[].speaker` labels are
kept (caption coloring) but every turn is synthesized with `enVoice`. If an `En`
variant is omitted, the builder falls back to zh with a warning.

## Content direction (platform-safe)

- Avoid leading with coin prices / quotes / fear-greed indices as the hero.
  A single number is fine as an *analytical lead-in*, never the focus.
- Analyze the logic chain behind moves (bull/bear, up/down) — mechanism,
  governance, capital structure, macro — not "BTC went up X% today".
- Cover must surface **today's real events** via `headlines`, so each day's
  cover differs (never a static daily title).
