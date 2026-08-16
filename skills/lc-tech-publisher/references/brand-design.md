# LongCipher Render-Side Visual System (Light)

This is the render-side distillation of the LongCipher **light** design system
(`DESIGN.md` is the source of truth). Every token below is a *hard rule* for the
fixed component templates. The skill is **fixed-template**: the LLM only ever
outputs structured JSON (`script.json`); all visual styling lives in the 4
hand-built component templates. This guarantees 100% visual control — the LLM
never writes CSS.

## 0. Non-negotiable (anti AI-default)

- **No AI-default fonts.** Use **DM Sans** (UI/headings) + **JetBrains Mono**
  (data/eyebrows). Never Inter/Roboto/Geist.
- **No rounded, pillowy corners.** 2px ceiling everywhere (`Radius 2px`).
  No pills, no circular avatars.
- **No second accent hue.** Single brand blue `#0a72ef` only. Direction uses
  neutral ink, not red/green traffic-light colors (we are a knowledge brand, not
  a trading terminal — see §6 for the one allowed semantic exception).
- **No mesh gradients, no glow auras, no blob logos, no shimmer.**
- **Depth via shadow-as-border**, not CSS borders on primary surfaces.

## 1. Color (Light)

| Token | Hex | Use |
|-------|-----|-----|
| `--canvas` | `#fafbfc` | Page / video background (subtle blue tint) |
| `--surface` | `#ffffff` | Cards / elevated panels |
| `--ink` | `#171718` | Primary text, headings (near-black, slight blue tint) |
| `--ink-200` | `#4e5159` | Secondary text on light |
| `--ink-300` | `#565a63` | Muted captions, metadata, eyebrows (passes WCAG AA on light) |
| `--ink-400` | `#6b6e75` | Faint labels, dividers text (passes WCAG AA on light) |
| `--line` | `#e0e2e8` | Hairline borders / dividers (neutral-300) |
| `--line-strong` | `#b4b8c2` | Slightly stronger dividers |
| `--accent` | `#0a72ef` | The single brand blue — lines, borders, dots |
| `--accent-text` | `#0a63d0` | Slightly darker brand blue for text usage — passes WCAG AA on light |
| `--accent-soft` | `rgba(10,114,239,0.10)` | Faint accent wash (chart fill, hover) |
| `--accent-hair` | `rgba(10,114,239,0.40)` | Accent hairline border |

Shadow-as-border stack (rest):
```css
box-shadow:
  rgba(23,23,23,0.06) 0 0 0 1px,
  rgba(23,23,23,0.04) 0 1px 2px,
  #ffffff 0 0 0 1px inset;
```
Elevated (popover/card emphasis):
```css
box-shadow:
  rgba(23,23,23,0.10) 0 0 0 1px,
  rgba(23,23,23,0.10) 0 4px 12px,
  rgba(23,23,23,0.06) 0 12px 28px;
```

## 2. Typography

| Role | Family | Fallback |
|------|--------|----------|
| Sans (UI, prose, headings) | **DM Sans** | `ui-sans-serif, system-ui, sans-serif` |
| Mono (data, eyebrows, tickers, code) | **JetBrains Mono** | `ui-monospace, SFMono-Regular, monospace` |

Fonts load via Google Fonts `<link>` (DM Sans weights 400/500/600/700/800,
JetBrains Mono 400/500/700). Provide local fallbacks so a render without
network degrades gracefully, not catastrophically.

Type scale (base for 1920×1080; scale down via `--scale` for portrait):

| Token | Size | Weight | Use |
|-------|------|--------|-----|
| `display` | 88–104px | 800 | Hero / cover title (`-0.02em`) |
| `heading-1` | 52–64px | 700 | Slide headline |
| `stat-value` | 64–80px | 800 | Metric number (mono) |
| `copy` | 30–38px | 400–500 | Body, card text |
| `label` | 18–22px | 500 | Eyebrow, mono overlines (`0.12em` tracking, uppercase) |
| `caption` | 34–40px | 600 | Bottom speech caption |

## 3. Surfaces & Radius

- Cards: `background: var(--surface); box-shadow: <rest stack>; border-radius: 2px;`
  Avoid flat `border` for primary surfaces; dividers may use `--line` hairlines.
- Radius: **2px** for every element (cards, chips, inputs, thumbs). No pills.
- Never pure-black text on pure-white without the `--ink` token; never neon.

## 4. Background System (calm, not "alive with glow")

The light canvas is `#fafbfc`. Persistent, *subtle* layers (compositor-only
transform/opacity):

1. **Hairline grid** — an SVG `<pattern>` of 64px lines at `rgba(23,23,23,0.04)`.
   Provides structure without noise. Not animated (or a very slow opacity breathe
   ≤0.04 amplitude — optional).
2. **Top scanline accent** — a single 1px horizontal line with a blue gradient
   that sweeps once on hero (not a permanent glow).
3. **Slide transitions** — each fixed component enters with a GSAP slide+fade;
   only one component is on stage at a time (replaces the dark "panel swap").

Motion stays compositor-only (`transform`/`opacity`/`filter` only). No
per-frame layout, no `transition: all`.

## 5. Fixed Components (the only visual vocabulary)

Built by hand as standalone HTML templates. The LLM outputs JSON; the builder
injects data into these. **Four components:**

| # | Template | Drives | Purpose |
|---|----------|--------|---------|
| 1 | `cover.html` | `cover` + `headlines` | Cover card / video hero. Title, subtitle, kicker, 4 headline bullets, meta row. |
| 2 | `dashboard.html` (keypoint branch) | `slides[]` where `type:"keypoint"` | A single highlighted statement / quote / key takeaway — large, centered, one accent line. |
| 3 | `dashboard.html` (three_points branch) | `slides[]` where `type:"three_points"` | Exactly 3 structured points (title + body each) in a 3-up grid. |
| 4 | `dashboard.html` (outro branch) | `slides[]` where `type:"outro"` | Closing card: recap line + sign-off + brand lockup. |
| 5 | `dashboard.html` (table branch) | `slides[]` where `type:"table"` | Comparison table (funding rounds, metrics, rankings). |

The video master (`dashboard.html`) is a thin timeline orchestrator: it lays the
5 slide types as full-frame **slides**, each a HyperFrames `clip` with
`data-start`/`data-duration` aligned to the dialogue timeline, plus the persistent
embedded single-line caption and the dialogue audio. The slides are rendered
**inline** in `dashboard.html`'s JS (one `<section>` branch per `type`) — there are
no separate per-slide template files. `cover.html` is the only standalone slide
template and is shared by the 4-ratio static cover and the video hero. The
components themselves never change — only their injected data does.

## 6. Semantic Exception (direction)

We are a knowledge brand, so we avoid red/green "trading" semantics. The single
allowed deviation: when a number genuinely goes up/down and the data calls for
direction, use **neutral ink** for the figure and a small mono tag
(`▲ / ▼` or `+x% / -x%`) in `--ink-300`. Never use saturated `#10B981`/`#EF4444`.
If absolutely required by a brief, a muted `--up #2f9e6b` / `--down #d9544c` may
appear *only* inside a data table cell, never as a decorative glow.

## 7. Brand Lockup

- `lc.svg` mark placed small (top-left or bottom corner) as a quiet watermark at
  ~0.5 opacity. The mark carries its fixed multicolor K-line palette and is
  never recolored, never given a glow.
- Wordmark "LongCipher" in DM Sans 700, `--ink-300`, low emphasis.

## 8. Do / Don't

**Do:** keep edges sharp (2px); one blue accent; shadow-as-border; mono for all
numbers/labels; captions readable (contrast ≥ 4.5:1 on the caption plate).

**Don't:** introduce a 2nd accent hue; rounded/pill shapes; mesh/glow/shimmer;
AI-default fonts; let the LLM emit inline styles or new classes — styling only
lives in the fixed templates. Per-domain flavor (vocabulary, headline copy) lives
**only** in `script.json` data, never in CSS.

## 9. Content Modes (LLM picks one)

- `mode: "knowledge"` — a single-topic deep dive. `slides[]` walk one concept:
  cover → 2–3 `keypoint` → 1 `three_points` (mechanism/why/caveat) → `outro`.
- `mode: "digest"` — a daily multi-item roundup. `slides[]`串联 the day's items:
  cover → one `three_points` (today's 3 headlines) → several `keypoint` (each
  item as a takeaway) → `outro`. The `headlines` on the cover already串 the day.

The mode is a **prompting/structuring hint**, not a separate engine — both use
the same 4 fixed components.

## 10. Illustration Layer — cute flat stickers (the "human touch")

A deliberate, restrained exception to §0's "no pillowy corners": a **flat cute
illustration chip** that makes each slide feel less like a slide and more like a
knowledge card. The LLM never writes SVG — it picks a key from the fixed catalog
(`_icons.js`, injected into `dashboard.html` / `shorts.html`):

- **Catalog** (15 keys): `shield`, `rocket`, `chart`, `coins`, `cube`, `atom`,
  `bolt`, `net`, `lock`, `spark`, `pick`, `scale`, `bot`, `bank`, `handshake`.
  Each is brand-blue line art (`--accent` strokes, `--accent-text` details) on
  an `--accent-soft` chip with a 1px `--accent-hair` border and the rest
  shadow stack. Radius ≤ 16px on the chip ONLY (illustrations are the one place
  rounded forms are allowed); UI surfaces keep the 2px ceiling.
- **Placement**: keypoint / three_points / table / outro slides render the chip
  top-right (150×150px in the video, 44×44px in shorts). The keypoint stage
  gains `has-illust` padding (right: 24%) so the statement never collides.
- **Motion**: pop in with `back.out(1.7)` overshoot, then a gentle idle
  `rotation ±6°` yoyo wobble (0.9s, sine.inOut) — alive but not frantic.
- **Fallback**: an unknown `icon` key renders `spark` (the template's default),
  and a slide with no `icon` renders no chip. Never a broken image.

## 11. Analysis Chip & Callback Tags (information association)

Two fixed elements turn a list of facts into a *connected argument*:

- **Analysis chip** — `s.analysis` renders as a distinct "分析 / SO-WHAT" strip
  under the bullets: `--accent-soft` background, 3px `--accent` left border,
  mono label + 23px ink text. It is the *so-what* inference anchored to the
  chapter's numbers — never a generic slogan.
- **Callback tags** — `s.callback` (string or array) renders as small bordered
  `↳` tags under the analysis: 16px JetBrains Mono, `--ink-300` text, 2px
  radius, `--accent-text` arrow. These make cross-chapter links visible, so the
  viewer sees *why* the chapters belong together.

## 12. Mascot & Background Decorations (the "living frame")

The canvas itself is alive, not just the slides — but always in the background
layer (z-index 4, under the slides at 5) so nothing is ever occluded:

- **Mascot** — a cute hand-drawn brand-blue robot (`#mascot` in dashboard /
  shorts / cover). It floats gently (`y: ±14px`, 2.1s sine.inOut, finite
  repeat sized to the composition) and blinks on a fixed cadence (`scaleY
  0.08→1` on `.mascot-eyes`, which needs `transform-box: fill-box`). Bottom-
  right in the landscape video, bottom-left in vertical shorts, bottom-right on
  the static cover. **It never hides content**: z-index 4 sits under the slide
  layer, and the slides have transparent backgrounds so the robot stays visible
  as a quiet companion.
- **Background glyphs** — a fixed hand-built set of tiny brand-blue shapes
  (spark / dot / cross / ring / square) scattered at the frame edges, each
  bobbing and slowly rotating on its own phase (`tl.to(el, {y, rotation},
  sine.inOut, yoyo, finite repeat)`). Below the slides (z-index 1), they add
  texture without competing with the center content.
- **Rule**: like every other animation, the deco/mascot tweens use **finite**
  repeat counts derived from the composition duration — `repeat:-1` is rejected
  by the checker on a finite composition.
