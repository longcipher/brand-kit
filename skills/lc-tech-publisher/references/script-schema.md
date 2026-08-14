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

| `type` | Required fields | Renders via |
|--------|----------------|-------------|
| `keypoint` | `statement` (string, ≤ ~40 chars), optional `eyebrow`, optional `support`, optional `bullets[]` (3–5 short fact lines shown as a structured list under the statement), optional `audioFrom`/`audioTo` (turn ids binding the slide to a narration chapter) | `tpl_keypoint.html` |
| `three_points` | `points[3]` each `{ no, title, body }`, optional `title`, optional `audioFrom`/`audioTo` | `tpl_three_points.html` |
| `table` | `head[≥2]` (string column headers), `rows[]` (each row must have the same cell count as `head`), optional `numCols` (array of 0-based column indices rendered right-aligned in mono blue), optional `title`, optional `audioFrom`/`audioTo` | `dashboard.html` inline table |
| `outro` | `recap` (string), optional `signoff`, optional `audioFrom`/`audioTo` | `tpl_outro.html` |

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

The **cover** is component 1 (`tpl_cover.html`) and also serves as the video's
hero slide — it is not listed in `slides[]`; the builder always opens the video
with the cover, then plays `slides[]`, then ends on `outro` (auto-appended if the
last slide isn't an `outro`). Use the `table` slide whenever you have comparable
figures (funding rounds, metrics, rankings) — a real data table reads far more
credibly than prose and keeps the screen's static document zone information-dense.

## Dialogue rules

- `podcast[]` is an ordered array `{ id, speaker: "male"|"female", text }`.
  `speaker` drives the TTS voice and the caption accent.
- Male = confident explainer (老高式); female = curious questioner (小茉式).
  Natural back-and-forth, not a monologue split in half.
- Female inserts a real question/reaction every 2–3 male lines.
- Keep emotion/price-panic out; favor mechanism, logic chains, deeper causes.
- Total `text` length ≈ `target_seconds` at ~3.0–3.4 chars/sec (zh),
  ~2.2–2.5 words/sec (en). For an ~11 min video target ≈ 2000–2400 zh chars.

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
