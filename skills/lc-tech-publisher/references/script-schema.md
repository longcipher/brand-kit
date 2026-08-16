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
- `icon` — a key from the fixed cute-illustration catalog (`shield/rocket/chart/coins/cube/atom/bolt/net/lock/spark/pick/scale/bot/bank/handshake`). The template owns the SVG art; you only pick a topic-matching key. Unknown keys fall back to `spark`.
- `analysis` — 1–2 sentence so-what line, rendered as a distinct "分析 / SO-WHAT" chip under the bullets. Must be a *specific* inference tied to that chapter's numbers, never a generic slogan.
- `callback` — string or array of short strings linking this chapter to another, rendered as small `↳` tags (the visible information-connection layer). Example: `"呼应开头:零售 -0.6% 的宏观压力"`.

| `type` | Required fields | Renders via |
|--------|----------------|-------------|
| `keypoint` | `statement` (string, ≤ ~40 chars), optional `eyebrow`, optional `support`, optional `bullets[]` (3–5 short fact lines shown as a structured list under the statement), optional `icon`/`analysis`/`callback`, optional `audioFrom`/`audioTo` (turn ids binding the slide to a narration chapter) | inline in `dashboard.html` (keypoint branch) |
| `three_points` | `points[3]` each `{ no, title, body }`, optional `title`, optional `icon`, optional `audioFrom`/`audioTo` | inline in `dashboard.html` (three_points branch) |
| `table` | `head[≥2]` (string column headers), `rows[]` (each row must have the same cell count as `head`), optional `numCols` (array of 0-based column indices rendered right-aligned in mono blue), optional `title`, optional `icon`, optional `audioFrom`/`audioTo` | inline in `dashboard.html` (table branch) |
| `outro` | `recap` (string), optional `signoff`, optional `icon`, optional `audioFrom`/`audioTo` | inline in `dashboard.html` (outro branch) |

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
- Total `text` length ≈ `target_seconds` at ~3.0–3.4 chars/sec (zh),
  ~2.2–2.5 words/sec (en). For an ~11 min video target ≈ 2000–2400 zh chars.

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
