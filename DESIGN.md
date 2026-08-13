# LongCipher Design System

> A restrained, technical design system for the LongCipher account portal and brand surface. The interface serves the task: log in, update credentials, manage security — without friction or personality getting in the way. Every element earns its pixel.

---

## 1. Design Philosophy

**Design serves the task.** Users arrive mid-auth-flow and want to complete an action, fast. The system is deliberately quiet: near-white backgrounds, near-black text, one blue accent, shadow-as-border for depth, precise typographic hierarchy. No decorative flourish, no rainbow gradients, no AI-default visual tropes.

**De-AI commitments** (what we explicitly avoid):
- No saturated AI-default typefaces (Geist, Inter, Roboto). Use **DM Sans** + **JetBrains Mono**.
- No rounded, pillowy corners. Edges are nearly square — a technical, deliberate feel.
- No multi-color mesh gradients, no blob logos, no glow auras.
- No purple/violet/indigo accents. One blue only.
- No "AI shimmer," no animated gradient borders, no autoplay motion.

**Brand as mark, not decoration.** The LongCipher identity is carried by real vector marks (`lc.svg`, `lc11.svg`, `lc169.svg`, `lc31.svg`, `lc43.svg` at the repo root) — geometric, monochrome, built from the letterforms. These are the brand, not a gradient blob. Use them as-is; do not wrap them in gradient containers.

---

## 2. Typography

### Fonts

| Role | Family | Notes |
|------|--------|-------|
| UI / Headings | **DM Sans** | Geometric sans, distinctive character, not AI-saturated |
| Code / Data | **JetBrains Mono** | Technical identifiers, keys, tokens, tabular data |

```css
--font-sans: "DM Sans", ui-sans-serif, system-ui, sans-serif;
--font-mono: "JetBrains Mono", ui-monospace, SFMono-Regular, monospace;
```

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

| Token | Hex | Role |
|-------|-----|------|
| Primary Blue | `#0a72ef` | Actions, links, active states, focus |
| Error Red | `#ff5b4f` | Errors, destructive actions, validation |
| Focus Blue | `hsla(212,100%,48%,1)` | `:focus-visible` ring |

Use `:focus-within` to group focus on composite controls.

### Blue-tinted Neutral Scale

The subtle tint creates subconscious harmony with the primary blue.

| Scale | Hex | Role |
|-------|-----|------|
| 50  | `#ffffff` | Pure white cards |
| 100 | `#f6f7f9` | Tinted off-white |
| 200 | `#eceef2` | Light surfaces |
| 300 | `#e0e2e8` | Borders, dividers |
| 400 | `#b4b8c2` | Muted text |
| 500 | `#888d98` | Secondary text |
| 600 | `#6b6e75` | Body text on dark |
| 700 | `#4e5159` | Headings on dark |
| 800 | `#2a2d33` | Dark surfaces |
| 900 | `#171718` | Primary text |
| 950 | `#0a0a0c` | Dark backgrounds |

### Rules
- **One accent only.** Blue is the single brand color. Never introduce a second hue for decoration.
- **No rainbow / mesh gradients.** Backgrounds are solid off-white. The brand mark is monochrome.
- **State contrast:** `:hover`, `:active`, `:focus` must be visibly higher-contrast than rest. Never rely on color alone — always pair with a text label or icon.
- **Browser theming:** `<meta name="theme-color" content="#fafbfc">`. For dark themes set `color-scheme: dark` on `<html>`.

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

Do **not** use 6/8/12/16px radii, full-round pills, or circular avatars anywhere in this system.

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
  - Curly quotes `“ ”` over straight `" "`.
  - `&` over `and` where space-constrained.
- **Action-oriented ambiguity:** buttons specific ("Save API Key").
- **Constructive errors:** guide the exit, don't just state the problem. "Your API key is incorrect. Generate a new key in settings."
- **i18n safety:** wrap brand names and code tokens in `translate="no"`. Format dates/numbers with `Intl.DateTimeFormat` / `Intl.NumberFormat` — never hardcode formats.

---

## 8. Layout & Performance

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
  --color-error: #ff5b4f;
  --font-sans: "DM Sans", ui-sans-serif, system-ui, sans-serif;
  --font-mono: "JetBrains Mono", ui-monospace, monospace;
  --radius-sm: 2px; /* the only radius in the system */
}
```

**Example prompts for agents:**
- *"Create a form input. Explicit `<label>`, input font-size 16px (mobile safe), `autocomplete='off'`, placeholder ending in `…` with example pattern, allows paste, validates on submit. Focus uses shadow-based ring (no `outline:none` without replacement). Radius 2px."*
- *"Design a settings card. Shadow-as-border `box-shadow: 0 0 0 1px rgba(23,23,23,0.08)`. Labels DM Sans 600. Data values JetBrains Mono. Radius 2px, sharp corners."*
- *"Build a nav bar. Brand name DM Sans 700, tracking -0.02em. Nav links DM Sans 500, tracking -0.01em. Single blue accent `#0a72ef`."*
- *"Render the LongCipher mark from `lc.svg` as a monochrome logo. No gradient wrapper, no glow."*

---

## 13. Appendix — Brand Assets

Real vector marks at repo root (use as-is, monochrome, no gradient containers):

| File | Use |
|------|-----|
| `lc.svg` | Primary logo / wordmark |
| `lc11.svg` | Compact / square variant |
| `lc169.svg` | Wide / banner variant |
| `lc31.svg` | Alternate mark |
| `lc43.svg` | Alternate mark |

These replace the old mesh-gradient blob logo. They are the brand; treat them as precise geometry, not decoration.
