# LongCipher Design System

> A restrained, technical design system for the LongCipher account portal and brand surface. The interface serves the task: log in, update credentials, manage security — without friction or personality getting in the way. Every element earns its pixel.

---

## 1. Design Philosophy

**Design serves the task.** Users arrive mid-auth-flow and want to complete an action, fast. The system is deliberately quiet: near-white backgrounds, near-black text, one blue accent, shadow-as-border for depth, precise typographic hierarchy. No decorative flourish, no rainbow gradients, no AI-default visual tropes.

**De-AI commitments** (what we explicitly avoid):
- No saturated AI-default typefaces (Geist, Inter, Roboto). Use **DM Sans** + **JetBrains Mono**.
- No rounded, pillowy corners. Edges are nearly square — a technical, deliberate feel.
- No multi-color mesh gradients, no blob logos, no glow auras.
- No purple/violet/indigo accents. One blue only — **this rule applies to all UI elements (lines, borders, text, fills). The brand logo mark is the single intentional exception: it is a fixed multicolor asset (see §13) and is never recolored.**
- No "AI shimmer," no animated gradient borders, no autoplay motion.

**Brand as mark, not decoration.** The LongCipher identity is carried by real vector marks (`lc.svg`, `lc11.svg`, `lc169.svg`, `lc31.svg`, `lc43.svg` at the repo root). The core mark is built from the letterforms with **K-line–inspired geometry** and uses a **fixed multicolor palette** (red `#FF0000`, green `#08C477`, dark `#2A2A2A`, light `#FAFAF9`) — this is an intentional brand asset, not a gradient blob. The light `#FAFAF9` element is **negative space** between the K-line strokes: on a light canvas it reads as a gap matching the page; on dark surfaces it reads as a bright separator. Use the marks **as-is**; never recolor, regradient, or wrap them in gradient containers.

Lockup variants (`lc11/31/43/169`) embed the `LongCipher` wordmark as **DM Sans 700 path outlines** (no system-font dependency) in brand blue `#0a72ef`, tracking `-0.02em`. The video/cover lockup uses the pure mark `lc.svg` for the icon and renders the `LongCipher` wordmark in **DM Sans 700** via CSS (see the skill's `{{LOGO}}` + `.lockup span`) — never JetBrains Mono, never a system font. Do not substitute the embedded-text variants (`lc31/43/169`) for the animated lockup.

---

## 2. Typography

### Fonts

| Role | Family | Notes |
|------|--------|-------|
| UI / Headings | **DM Sans** | Geometric sans, distinctive character, not AI-saturated |
| Code / Data | **JetBrains Mono** | Technical identifiers, keys, tokens, tabular data |

```css
--font-sans: "DM Sans", "PingFang SC", "Microsoft YaHei", "Noto Sans SC", "Noto Sans CJK SC", ui-sans-serif, system-ui, sans-serif;
--font-mono: "JetBrains Mono", ui-monospace, SFMono-Regular, monospace;
```

- **CJK:** DM Sans is Latin-only. Chinese glyphs fall back to the system CJK face (PingFang SC / Microsoft YaHei / Noto Sans SC). Prefer loading a self-hosted Noto Sans SC / Source Han Sans subset when shipping Chinese UI copy, and list it **before** the generic `ui-sans-serif` fallback. Never let CJK land on a default serif.

- Load with `rel="preload" as="font" font-display="swap"`.
- Enable ligatures globally: `font-feature-settings: "liga" 1;`
- Use tabular nums for data/number columns: `font-variant-numeric: tabular-nums;` (`"tnum"`).
- Headings: `text-wrap: balance` (or `text-pretty`) to prevent widows/orphans.

### Scale (fixed rem — product UI has consistent DPI)

```
display  2.25rem / 36px   700   -0.02em   page titles
title    1.5rem  / 24px   700   -0.02em   section / card titles
heading  1.125rem/ 18px   600   -0.01em   subsections
body     0.9375rem/15px   400   0        base text (line-height 1.5)
small    0.8125rem/13px   400   0        captions, hints
tiny     0.6875rem/11px   500   0.04em   overlines, uppercase labels (mono)
code     0.875rem / 14px   400   —        mono data / identifiers
```

### Brand typography
- Wordmark / logo lockup: **DM Sans 700**, tracking `-0.02em`.
- Nav links: **DM Sans 500**, tracking `-0.01em`.

---

## 3. Color

### Core

| Token | Hex | Role |
|-------|-----|------|
| Near-Black | `#171718` | Primary text, headings (slight blue tint) |
| Off-White | `#fafbfc` | Page background (subtle blue tint) |
| Pure White | `#ffffff` | Card / elevated surfaces |
| Pure Black | `#000000` | High-contrast text on white (optional) |

### Semantic

| Token | Hex | Role | Contrast on `#fafbfc` |
|-------|-----|------|----------------------|
| Primary Blue | `#0a72ef` | Buttons, fills, focus ring, large text, non-text UI | 4.34:1 (AA large / UI 3:1) |
| Accent Text | `#0a63d0` | **Links and blue body text** (AA on light) | 5.47:1 (AA) |
| Error Red | `#ff5b4f` | Error icons, borders, large text only | 2.95:1 (not for body text) |
| Error Text | `#c62d2d` | Error **message text** on light | 5.05:1 (AA) |
| Focus Blue | `hsla(212,100%,48%,1)` | `:focus-visible` ring | 3:1 UI ✓ |

**Contrast is a hard rule.** `#0a72ef` is **not** AA for normal-size text on the off-white canvas — use `#0a63d0` for any link or blue label under 24px. Same for errors: `#ff5b4f` is an ink/icon color only; error copy uses `#c62d2d`. Always verify with WCAG 2.x (4.5:1 body, 3:1 large/UI) before shipping.

Use `:focus-within` to group focus on composite controls.

### Blue-tinted Neutral Scale

The subtle tint creates subconscious harmony with the primary blue.

| Scale | Hex | Role | Contrast on `#fafbfc` |
|-------|-----|------|----------------------|
| 50  | `#ffffff` | Pure white cards | — |
| 100 | `#f6f7f9` | Tinted off-white | — |
| 200 | `#eceef2` | Light surfaces | — |
| 300 | `#e0e2e8` | Borders, dividers (non-text) | 1.30:1 |
| 400 | `#b4b8c2` | Placeholder / disabled icons only (never readable copy) | 1.92:1 |
| 500 | `#888d98` | Large secondary text (≥24px) or icons; not body copy | 3.21:1 |
| 550 | `#565a63` | **Muted body text** on light (AA) | 6.67:1 |
| 600 | `#6b6e75` | Secondary text on light (AA); body text on dark | 4.93:1 |
| 700 | `#4e5159` | Headings on dark / secondary on light | 8.20:1 |
| 800 | `#2a2d33` | Dark surfaces | — |
| 900 | `#171718` | Primary text | 17.29:1 |
| 950 | `#0a0a0c` | Dark backgrounds | — |

**Readable-text floor:** anything a user must read at body size lives at scale ≥550 (`#565a63`) on light, or ≥600 on white. 400/500 are for decoration, placeholders, and large type only.

### Dark Theme

| Token | Light | Dark |
|-------|-------|------|
| Canvas | `#fafbfc` | `#0a0a0c` |
| Surface | `#ffffff` | `#2a2d33` |
| Ink | `#171718` | `#ededed` |
| Ink secondary | `#4e5159` | `#b4b8c2` |
| Ink muted | `#565a63` | `#888d98` |
| Line | `#e0e2e8` | `#3a3e46` |
| Accent | `#0a72ef` | `#3d8bff` (slightly lifted for dark AA) |
| Accent text | `#0a63d0` | `#7eb0ff` |
| Error text | `#c62d2d` | `#ff8a80` |
| Shadows | black/alpha stack | white/alpha stack |

Focus ring (dark): `0 0 0 1px hsla(212,100%,62%,1), 0 0 0 4px hsla(212,100%,62%,0.22)`.
The brand **mark keeps its fixed multicolor palette in both themes** — `#FAFAF9` light gaps become the bright separator on dark. Never invent a "dark logo".

### Rules
- **One accent only.** Blue is the single UI brand color. Never introduce a second hue for decoration. The brand **mark** is the single intentional exception: a fixed multicolor K-line asset (red/green/dark/light) — never recolor it (see §13).
- **No rainbow / mesh gradients.** Backgrounds are solid off-white (or solid dark-950 in dark theme).
- **State contrast:** `:hover`, `:active`, `:focus` must be visibly higher-contrast than rest. Never rely on color alone — always pair with a text label or icon.
- **Browser theming:** `<meta name="theme-color" content="#fafbfc">` (dark: `#0a0a0c`). For dark themes set `color-scheme: dark` on `<html>`.

---

## 4. Corner Radius — Keep It Sharp

**Avoid rounded corners.** The system is technical and deliberate; near-square edges read as precise, not playful.

| Element | Radius | Rationale |
|---------|--------|-----------|
| Page / large containers | `0` | Hard edges |
| Cards / panels | `2px` | Barely-there soften; reads as square |
| Inputs / buttons | `2px` | Consistent with cards |
| Pills / badges / tags | `2px` | No full-round pills |
| Avatars / thumbnails | `2px` | Square, not circular |
| Tooltips / popovers | `2px` | Sharp |

**Nested radii rule:** child radius ≤ parent radius, and concentric so curves align mathematically. With a 2px system this is trivially satisfied.

Do **not** use 6/8/12/16px radii, full-round pills, or circular avatars on **UI surfaces** (cards, inputs, buttons, chips, modals, tooltips).

**Two documented exceptions** (everything else stays at 2px):
1. **Illustration chips** (the cute flat icon plates in the media skill): up to `16px`, chip only — the icon art is allowed rounded forms. UI chrome around it stays 2px.
2. **Diagram primitives** inside charts/flows (process-node rings, connection dots, pulse dots, terminal traffic-light dots): `border-radius: 50%` is allowed as *diagram language*, not UI chrome. The container/surface around a diagram still uses 2px.

---

## 5. Depth & Elevation (Shadow-as-Border)

Replace CSS borders with layered, multi-shadow stacks for crisp edges and ambient depth. The stack combines an inner highlight, a crisp ring, and soft ambient shadow.

**Card / surface (rest):**
```css
box-shadow:
  rgba(23,23,23,0.06) 0 0 0 1px,
  rgba(23,23,23,0.04) 0 1px 2px,
  #ffffff 0 0 0 1px inset;
```

**Input / control (rest):**
```css
box-shadow:
  rgba(23,23,23,0.08) 0 0 0 1px,
  rgba(23,23,23,0.04) 0 1px 1px;
```

**Input (focus-visible):**
```css
box-shadow:
  hsla(212,100%,48%,1) 0 0 0 1px,
  hsla(212,100%,48%,0.18) 0 0 0 4px,
  rgba(23,23,23,0.04) 0 1px 1px;
outline: none; /* replaced by visible ring above — never outline:none without a ring */
```

**Elevated (popover, modal, dropdown):**
```css
box-shadow:
  rgba(23,23,23,0.10) 0 0 0 1px,
  rgba(23,23,23,0.10) 0 4px 12px,
  rgba(23,23,23,0.06) 0 12px 28px;
```

Rules:
- Two+ layers minimum (ambient + direct light).
- Never use flat `border` for primary surfaces; use the shadow ring. Dividers may use `neutral-300` hairlines.
- Honor `prefers-reduced-motion`; provide calm static fallbacks.

---

## 6. Components & Interactions

### Forms & Inputs
- **Explicit `<label>`** for every control (or `aria-label`). No floating-label-only forms.
- **Hit targets:** generous. Label + control share one hit target (no dead zones). If visual target < 24px, expand hit area to ≥ 24px.
- **Mobile inputs:** `<input>` font-size **≥ 16px** to prevent iOS Safari zoom. Never `user-scalable=no`.
- **Paste & typing:** never block paste, never `preventDefault` on `onPaste`, never block keystrokes. Allow any input; show validation feedback.
- **autocomplete:** `off` on auth fields unless the browser should remember.
- **Placeholders:** signal emptiness with an ellipsis `…` and show an example pattern, e.g. `sk-012345679…`.
- **Submission:** keep submit enabled until submission starts; then disable, show a spinner, keep original label. Add a short show-delay (~150–300ms) to avoid flicker on fast responses.
- **No `autoFocus` on mobile** (triggers keyboard + layout shift).

### Links & Buttons
- **Navigation** uses `<a>` / `<Link>` — never `<div onClick>` or `<button>` for routing. Cmd/Ctrl+Click must open new tab.
- **Actions** use `<button>` exclusively.
- **Labels:** specific and action-oriented. "Save API Key", not "Continue". Title Case for buttons (Chicago style).

### Skeletons & Tooltips
- **Stable skeletons:** mirror final content exactly to avoid CLS.
- **Tooltip timing:** delay the first tooltip in a group; subsequent peers have no delay.

### Drag & Drop
- Disable text selection; apply `inert` on dragged elements so hover/selection don't trigger together.

---

## 7. Copywriting (Voice)

- **Active voice, 2nd person.** "Install the CLI", not "The CLI will be installed." Avoid first person.
- **Capitalization:** Title Case for headings & buttons (Chicago). Sentence case on marketing pages.
- **Numbers & units:** numerals for counts ("8 deployments"). Non-breaking space between number and unit (`10&nbsp;MB`, `⌘&nbsp;K`).
- **Punctuation:**
  - Real ellipsis `…`, not `...`.
  - Curly quotes `“ ”` over straight `" "` (this document uses them in prose examples).
  - `&` over `and` where space-constrained.
- **Action-oriented ambiguity:** buttons specific ("Save API Key").
- **Constructive errors:** guide the exit, don't just state the problem. "Your API key is incorrect. Generate a new key in settings."
- **i18n safety:** wrap brand names and code tokens in `translate="no"`. Format dates/numbers with `Intl.DateTimeFormat` / `Intl.NumberFormat` — never hardcode formats.

---

## 8. Layout, Spacing & Performance

### Spacing rhythm

```
Base unit:  4px
Scale:      4  8  12  16  24  32  48  64  96
Group:      8px  →  16px  →  32px   (three-step: tight / related / section)
```

- Micro (label↔control): `4–8px`.
- Related items in a card: `12–16px`.
- Between cards / sections: `24–32px`.
- Page gutters: `24px` mobile, `32–48px` desktop.
- Never use arbitrary values like `7px` / `13px` / `22px` — snap to the scale.

### Layout & performance

- **Let the browser size things:** prefer Flex/Grid over JS measurement. Avoid layout reads in render (`getBoundingClientRect`, `offsetHeight`).
- **`min-w-0`** on flex children to allow text truncation.
- **Safe areas:** full-bleed layouts use `env(safe-area-inset-*)`.
- **URL as state:** persist filters, tabs, expanded panels, pagination in the URL (e.g. `nuqs`) so refresh/share/Back-Forward work.
- **Scrollbars:** only useful ones. `overflow-x: hidden` on containers to kill unwanted horizontal scroll. `overscroll-behavior: contain` in modals/drawers.
- **Virtualization:** lists > 50 items must be virtualized (`virtua` or `content-visibility: auto`).
- **Preloading:** preload above-fold images (`priority`) and fonts (`rel="preload" as="font" font-display="swap"`).

---

## 9. Animation & Motion

- **Honor `prefers-reduced-motion`** with a calm fallback.
- **Compositor-friendly:** animate only `transform` and `opacity`. Never `width`/`height`/`top`.
- **Never `transition: all`** — list properties explicitly (causes jank).
- **Interruptible:** cancelable, respond to input mid-animation. Avoid autoplay.
- **SVG transforms:** apply CSS transforms to `<g>` wrappers; set `transform-box: fill-box; transform-origin: center;` (avoids Safari bugs).

---

## 10. Accessibility

- **Keyboard focus:** `:focus-visible` ring is mandatory. Never `outline: none` without a visual replacement. Group with `:focus-within`.
- **ARIA:** icon-only buttons get `aria-label`; images get `alt` (or `alt=""` if decorative); decorative icons get `aria-hidden="true"`.
- **Async updates:** `aria-live="polite"` for toasts, loading states, inline validation.
- **Locale:** `translate="no"` on brand/code tokens; `Intl.*` for dates/numbers.

---

## 11. Do & Don't

### Do
- Use shadow-as-border instead of CSS borders for cards/inputs.
- Tie UI state to the URL (deep-link everything).
- Optimistic updates with graceful rollback on failure.
- Destructive actions get confirmation modals or an undo window.
- `<label>` (or `aria-label`) on every control.
- Keep edges sharp (≤2px radius).

### Don't
- `transition: all` or animate `height`/`width`.
- Block paste / `preventDefault` on `onPaste`.
- Disable zoom (`maximum-scale=1`, `user-scalable=no`).
- Render `<button>` for links or `<div>` for buttons.
- Use `autoFocus` on mobile.
- Use rounded/pill/circular shapes, rainbow gradients, glow auras, or AI-default fonts (Geist/Inter/Roboto).
- Introduce a second accent color beyond the single blue.

---

## 12. Tech Stack & Agent Prompt Guide

**Stack:** Leptos (Rust) + Tailwind CSS v4 for the account portal. Brand assets are static SVG at repo root.

**Tailwind v4 tokens (example):**
```css
@theme {
  --color-ink: #171718;
  --color-canvas: #fafbfc;
  --color-surface: #ffffff;
  --color-blue: #0a72ef;
  --color-blue-text: #0a63d0;
  --color-error: #ff5b4f;
  --color-error-text: #c62d2d;
  --font-sans: "DM Sans", "PingFang SC", "Microsoft YaHei", "Noto Sans SC", ui-sans-serif, system-ui, sans-serif;
  --font-mono: "JetBrains Mono", ui-monospace, monospace;
  --radius-sm: 2px; /* the only UI radius in the system */
}
```

**Example prompts for agents:**
- *"Create a form input. Explicit `<label>`, input font-size 16px (mobile safe), `autocomplete='off'`, placeholder ending in `…` with example pattern, allows paste, validates on submit. Focus uses shadow-based ring (no `outline:none` without replacement). Radius 2px."*
- *"Design a settings card. Shadow-as-border `box-shadow: 0 0 0 1px rgba(23,23,23,0.08)`. Labels DM Sans 600. Data values JetBrains Mono. Radius 2px, sharp corners."*
- *"Build a nav bar. Brand name DM Sans 700, tracking -0.02em. Nav links DM Sans 500, tracking -0.01em. Single blue accent `#0a72ef`."*
- *"Render the LongCipher mark from `lc.svg` as-is — fixed multicolor K-line palette, never recolored, never monochrome-forced. No gradient wrapper, no glow."*

---

## 13. Appendix — Brand Assets

Real vector marks at repo root (use as-is, **fixed multicolor K-line palette**, no gradient containers, never recolor):

| File | Size | Use |
|------|------|-----|
| `lc.svg` | 1024×1024 | Pure mark (no text) — primary asset; video/cover lockup icon, favicons, avatars |
| `lc11.svg` | 1024×1024 | 1:1 mark + `LongCipher` wordmark (DM Sans paths, `#0a72ef`) |
| `lc31.svg` | 1800×600 | 3:1 lockup + slogan "AI NATIVE PAYMENT AND TRADING" |
| `lc43.svg` | 2400×1800 | 4:3 lockup + slogan |
| `lc169.svg` | 3200×1800 | 16:9 lockup + slogan (hero / social header) |

All five share one geometry, one light fill (`#FAFAF9`), one wordmark color (`#0a72ef`), and DM Sans **path outlines** (no `font-family` dependency — identical on every OS). They carry `role="img"` + `<title>`. Rebuild with `scripts/rebuild_logos.py`.

### Fixed mark palette (never recolor)

| Role | Hex | Note |
|------|-----|------|
| Light / negative space | `#FAFAF9` | Gap between K-line strokes. Reads as page gap on light; bright separator on dark. |
| Dark stroke | `#2A2A2A` | |
| Red stroke | `#FF0000` | |
| Green accent | `#08C477` | Small square only — never a status color (fails AA on light). |
| Wordmark / slogan | `#0a72ef` | The single UI accent. Slogan at `0.72` opacity. |

### Clearspace & minimum size

- **Clearspace:** leave at least **½ the mark height** of empty space on every side of the mark, or **cap-height of the wordmark** for lockups. Nothing (text, rules, UI chrome) enters that zone.
- **Minimum sizes:** pure mark `lc.svg` ≥ **16px** (favicon extreme) / **24px** preferred. Lockups with wordmark ≥ **32px** tall for `lc11`; `lc31`/`lc169` ≥ **120px** wide.
- Below 16px, use `lc.svg` alone — never stack a wordmark under 12px cap height.

### Misuse (never)

- Recolor, monochrome-force, invert, or add gradients/glows/shadows to the mark.
- Stretch, rotate, skew, or crop the hexagon.
- Substitute a system font for the wordmark (lockups already ship as paths — do not re-typeset).
- Use `lc11/31/43/169` as the animated video lockup icon (use `lc.svg` + CSS wordmark).
- Place the mark on a busy photo without a solid plate or sufficient clearspace.
- Use `#08C477` green as a UI status color (contrast 2.21:1 on light — decorative only).

### Favicon / app icon set (ship alongside)

| File | Size | Notes |
|------|------|-------|
| `favicon.svg` | vector | `lc.svg` (optionally with `prefers-color-scheme` light-gaps tweak) |
| `favicon-16.png` / `favicon-32.png` | 16 / 32 | ICO fallback bundle also recommended |
| `apple-touch-icon.png` | 180×180 | Opaque background (`#fafbfc` or `#0a0a0c`), no transparency |
| `icon-192.png` / `icon-512.png` | 192 / 512 | PWA |
| `icon-512-maskable.png` | 512 | Safe zone = center 66% (mark scaled to ~60% of canvas) |

Generate from `lc.svg` (pure mark). Keep padding so the hexagon isn't clipped at round OS masks.

### Usage in product UI

These replace the old mesh-gradient blob logo. They are the brand; treat them as precise geometry, not decoration. The embedded-wordmark variants (`lc11/31/43/169`) are for static placements (page headers, social avatars, leave-behinds) — **the animated video/cover lockup uses `lc.svg` (pure mark) + a DM Sans `LongCipher` rendered by CSS, not an embedded-text variant.**
