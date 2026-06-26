---
version: "1.0"
name: LongCipher Design System
description: A Vercel Geist-inspired design system — minimal, high-contrast, developer-focused. Stark black-and-ink on near-white canvas with a multi-color mesh gradient as the sole decorative system.
---

# LongCipher Design System

## Design Philosophy

Interfaces succeed because of hundreds of small choices. This document is the living record of those choices — a design system so restrained it borders on philosophical. The page is overwhelmingly white with near-black text, creating a gallery-like emptiness where every element earns its pixel. This isn't minimalism as decoration; it's minimalism as engineering principle.

**Core Principles:**

- **Earn your pixel.** Every element must justify its existence. If removal doesn't break comprehension, remove it.
- **Content is king.** The surface disappears; the information stands. Whitespace is not emptiness — it's structure.
- **Consistency over novelty.** Reuse tokens, patterns, and rhythms. Surprise belongs in the product, not the chrome.
- **Accessibility is non-negotiable.** WCAG AA contrast (4.5:1 for body text), keyboard-operable flows, and visible focus rings are requirements, not nice-to-haves.

---

## 1. Colors

### 1.1 Gray Scale (10 Steps)

Each step encodes intent, not just lightness:

| Step | Hex | Intent |
|------|-----|--------|
| `gray-100` | `#f2f2f2` | Default background |
| `gray-200` | `#ebebeb` | Hover background |
| `gray-300` | `#e6e6e6` | Active background |
| `gray-400` | `#eaeaea` | Default border |
| `gray-500` | `#c9c9c9` | Hover border |
| `gray-600` | `#a8a8a8` | Active border |
| `gray-700` | `#8f8f8f` | Solid fill, disabled text |
| `gray-800` | `#7d7d7d` | Solid fill, hover |
| `gray-900` | `#4d4d4d` | Secondary text & icons |
| `gray-1000` | `#171717` | Primary text & icons |

Alpha variants (`gray-alpha-100` through `gray-alpha-1000`) are translucent and layer over any background; use for borders, dividers, overlays, hover states.

### 1.2 Surface Colors

| Token | Hex | Use |
|-------|-----|-----|
| `background-100` | `#ffffff` | Primary page & card surface |
| `background-200` | `#fafafa` | Secondary surface, subtle separation |

### 1.3 Accent Scales

Each accent runs 10 steps (`100`–`1000`). Use hex everywhere; P3 wide-gamut `oklch()` variants available for high-end displays.

| Scale | Semantic Role | Key Values |
|-------|--------------|------------|
| **Blue** | Success, links, focus | `#0070f3` (link), `#006bff` (focus ring) |
| **Red** | Errors, destructive | `#ee0000` (error), `#fc0035` (solid) |
| **Amber** | Warnings, pending | `#f5a623` (warning) |
| **Green** | Positive, confirmed | `#28a948` |
| **Teal** | Data, secondary accent | `#00ac96` |
| **Purple** | Code, developer console | `#7928ca` |
| **Pink** | Preview, highlight | `#ff0080` |

### 1.4 Brand Gradient

The signature decoration is a three-pair gradient stack — the entire decorative system:

| Pair | Start | End | Use |
|------|-------|-----|-----|
| **Develop** | `#007cf0` | `#00dfd8` | Blue-to-teal, deploy/develop rhythm |
| **Preview** | `#7928ca` | `#ff0080` | Violet-to-pink, preview surfaces |
| **Ship** | `#ff4d4d` | `#f9cb28` | Coral-to-amber, ship surfaces |

The three pairs collapse into a single multi-color mesh gradient as the hero atmospheric backdrop. Used at hero scale only — never miniaturize to an icon or reduce to a single colour.

### 1.5 Selection

| Token | Value |
|-------|-------|
| `selection-bg` | `#171717` |
| `selection-fg` | `#f2f2f2` |

### 1.6 P3 Wide-Gamut

Every accent scale ships a `*-p3` variant in `oklch()` for Display P3 screens. Example:

```css
color: #006bff;
color: oklch(57.61% 0.2508 258.23); /* P3 override */
```

### 1.7 Semantic Color Tokens

Semantic tokens decouple intent from raw values. They sit on top of the primitive scales and are the **primary path** for component styling. Primitives (`gray-100`..`gray-1000`, accent scales) are escape hatches when no semantic token fits.

#### Surfaces

| Token | Light | Dark | Purpose |
|-------|-------|------|---------|
| `bg-background` | `#ffffff` | `#000000` | Page background |
| `bg-subtle` | `gray-100` `#f2f2f2` | `gray-100` `#1a1a1a` | Quietest page surface |
| `bg-elevated` | `gray-200` `#ebebeb` | `gray-200` `#222222` | Cards, sections raised above page |

#### Text

| Token | Light | Dark | Purpose |
|-------|-------|------|---------|
| `text-emphasis` | `gray-1000` | `gray-1000` | Headings, prominent labels, input values |
| `text-default` | `gray-900` | `gray-900` | Body text, button labels, form labels |
| `text-muted` | `gray-700` | `gray-700` | Captions, metadata, disabled text |
| `text-placeholder` | `gray-600` | `gray-700` | Input placeholders |
| `text-on-brand` | `#ffffff` | `#000000` | Text inside primary button |

#### Borders

| Token | Light | Dark | Purpose |
|-------|-------|------|---------|
| `border-default` | `gray-400` | `gray-400` | Cards, sections, dividers |
| `border-subtle` | `gray-200` | `gray-200` | Quieter static border |
| `border-interactive` | `gray-alpha-300` | `gray-alpha-300` | Interactive component borders (button, select, input) |

#### Interactive (gray)

| Token | Light | Dark | Purpose |
|-------|-------|------|---------|
| `bg-interactive` | `gray-alpha-200` | `gray-alpha-200` | Rest bg for buttons, selects, inputs |
| `bg-interactive-hover` | `gray-alpha-300` | `gray-alpha-300` | Hover, focus, pressed, expanded, selected |
| `ring-focus` | `gray-alpha-300` | `gray-alpha-300` | Default focus ring |

#### Brand (primary button)

| Token | Light | Dark | Purpose |
|-------|-------|------|---------|
| `bg-brand` | `gray-1000` `#171717` | `gray-1000` `#ededed` | Primary button rest |
| `bg-brand-hover` | `gray-900` | `gray-900` | Primary button hover |
| `ring-brand` | `gray-alpha-400` | `gray-alpha-400` | Primary button focus ring |

#### Error (red, destructive)

| Token | Primitive | Purpose |
|-------|-----------|---------|
| `bg-error` | `red-200` | Invalid input bg, destructive button rest |
| `bg-error-hover` | `red-400` | Destructive button hover |
| `border-error` | `red-600` | Invalid input, toast error, form validation |
| `border-error-subtle` | `red-400` | Quieter error border |
| `text-error` | `red-700` | Error text, error icons, validation messages |
| `ring-error` | `red-500` | Destructive button focus ring |

#### Warning (amber)

| Token | Primitive | Purpose |
|-------|-----------|---------|
| `bg-warning` | `amber-200` | Warning tag, toast warning bg |
| `border-warning` | `amber-600` | Toast warning outline |
| `border-warning-subtle` | `amber-400` | Quieter warning border |
| `text-warning` | `amber-700` | Warning icons, banners, pending spinners |

#### Success (green)

| Token | Primitive | Purpose |
|-------|-----------|---------|
| `bg-success` | `green-200` | Success tag, toast success bg |
| `border-success` | `green-600` | Toast success, switch checked |
| `border-success-subtle` | `green-400` | Quieter success border |
| `text-success` | `green-700` | Success icons, copy feedback, healthy states |

#### Info (blue)

| Token | Primitive | Purpose |
|-------|-----------|---------|
| `bg-info` | `blue-200` | Info tag |
| `border-info-subtle` | `blue-400` | Info tag border |
| `text-info` | `blue-700` | Informational icons, status text |

#### Link

| Token | Primitive | Purpose |
|-------|-----------|---------|
| `text-link` | `blue-700` | Clickable text, links |
| `border-link` | `blue-700` | Link hover underline |
| `ring-link` | `blue-500` | Link focus ring |

### 1.8 Semantic vs Primitive Rules

- **Prefer semantic tokens** for all component styling. They decouple intent from value, collapse `dark:` variants into single tokens, and survive scale changes.
- **Fall through to primitives** when: the intent has no semantic token (e.g., softer text tiers), one-off decorative use (gradient stops), or mid-scale grays (`gray-400` through `gray-600`) that have no semantic name.

---

## 2. Typography

### 2.1 Font Families

| Role | Family | Fallback Stack |
|------|--------|----------------|
| UI & prose | `Geist Sans` | `Inter, system-ui, -apple-system, sans-serif` |
| Code & data | `Geist Mono` | `ui-monospace, SFMono-Regular, Menlo, Monaco, monospace` |

Open-source substitutes: *Inter* (geometric sans, enable `ss01`, `ss02`), *JetBrains Mono* (mono).

### 2.2 Font Features

- Ligatures: `"liga"` enabled globally.
- Tabular numbers: `font-variant-numeric: tabular-nums` for number columns/comparisons.
- Text wrapping: `text-wrap: balance` or `text-pretty` on headings to prevent widows/orphans.

### 2.3 Heading Tokens

| Token | Size | Weight | Line Height | Letter Spacing | Use |
|-------|------|--------|-------------|----------------|-----|
| `heading-72` | 72px | 600 | 72px | -4.32px | Hero display |
| `heading-64` | 64px | 600 | 64px | -3.84px | Hero display |
| `heading-56` | 56px | 600 | 56px | -3.36px | Hero display |
| `heading-48` | 48px | 600 | 56px | -2.88px | Hero headline |
| `heading-40` | 40px | 600 | 48px | -2.4px | Section headline |
| `heading-32` | 32px | 600 | 40px | -1.28px | Section headline |
| `heading-24` | 24px | 600 | 32px | -0.96px | Card cluster headline |
| `heading-20` | 20px | 600 | 26px | -0.4px | Inline micro-heading |
| `heading-16` | 16px | 600 | 24px | -0.32px | Small heading |
| `heading-14` | 14px | 600 | 20px | -0.28px | Compact heading |

### 2.4 Body & Label Tokens

| Token | Size | Weight | Line Height | Letter Spacing | Use |
|-------|------|--------|-------------|----------------|-----|
| `copy-24` | 24px | 400 | 36px | 0 | Lead paragraph |
| `copy-20` | 20px | 400 | 36px | 0 | Lead paragraph |
| `copy-18` | 18px | 400 | 28px | 0 | Lead paragraph |
| `copy-16` | 16px | 400 | 24px | 0 | Default body |
| `copy-14` | 14px | 400 | 20px | 0 | Secondary body |
| `copy-13` | 13px | 400 | 18px | 0 | Compact body |
| `label-20` | 20px | 400 | 32px | 0 | Navigation label |
| `label-16` | 16px | 400 | 20px | 0 | Form label |
| `label-14` | 14px | 400 | 20px | 0 | Table header, metadata |
| `label-13` | 13px | 400 | 16px | 0 | Compact label |
| `label-12` | 12px | 400 | 16px | 0 | Caption, badge |

### 2.5 Button Tokens

| Token | Size | Weight | Line Height |
|-------|------|--------|-------------|
| `button-16` | 16px | 500 | 20px |
| `button-14` | 14px | 500 | 20px |
| `button-12` | 12px | 500 | 16px |

### 2.6 Mono Tokens

| Token | Size | Weight | Line Height | Use |
|-------|------|--------|-------------|-----|
| `label-14-mono` | 14px | 400 | 20px | Technical label |
| `label-13-mono` | 13px | 400 | 20px | Code caption |
| `label-12-mono` | 12px | 400 | 16px | Section eyebrow |
| `copy-14-mono` | 14px | 400 | 20px | Inline code |
| `copy-13-mono` | 13px | 400 | 18px | Code block |

### 2.7 Typography Rules

- **Weight 600 is the display ceiling.** Never use 700 or heavier.
- **Negative tracking is part of the voice.** Display sizes use aggressive -2.4 to -0.4px tracking. Never letter-space positively on Geist Sans.
- **Sentence-case headlines, period-terminated.** The deliberate period is part of the brand voice.
- **Mono for the technical layer only.** Section eyebrows, code blocks, terminal mockups. Body paragraphs never in mono.
- **`copy-14` and `label-14` cover most text.** Default to these.

---

## 3. Spacing

### 3.1 Scale (4px Base)

| Token | Value |
|-------|-------|
| `1` / `xxs` | 4px |
| `2` / `xs` | 8px |
| `3` / `sm` | 12px |
| `4` / `md` | 16px |
| `6` / `lg` | 24px |
| `8` / `xl` | 32px |
| `10` / `2xl` | 40px |
| `16` / `4xl` | 64px |
| `24` / `5xl` | 96px |

### 3.2 Rhythm

Three-step rhythm:

- **8px** inside a group (between related items)
- **16px** between groups
- **32–40px** between sections

### 3.3 Container Padding

| Context | Padding |
|---------|---------|
| Card (default) | 24px |
| Card (compact) | 16px |
| Card (hero) | 32px |
| Section band | 64–96px top/bottom |
| Page horizontal | 24px desktop, 16px mobile |

### 3.4 Grid

- Max content width: 1200px (legacy) / 1400px (current)
- Center with horizontal gutters
- Breakpoints: `sm` 401px, `md` 601px, `lg` 961px, `xl` 1200px, `2xl` 1400px

---

## 4. Shapes (Border Radius)

| Token | Value | Use |
|-------|-------|-----|
| `sm` | 6px | Everyday surfaces, controls, inputs, buttons |
| `md` | 12px | Menus, modals, dialogs |
| `lg` | 16px | Fullscreen surfaces, hero cards |
| `full` | 9999px | Pills, avatars, circular controls |

Rules:

- Child radius ≤ parent radius; concentric so curves align.
- One radius family per view — don't mix rounded and sharp corners.
- Marketing CTAs: 100px pill. Nav buttons: 6px square.

---

## 5. Elevation & Depth

### 5.1 Shadow Stack

| Level | Treatment | Use |
|-------|-----------|-----|
| **0 — Flat** | No shadow, no border | Full-bleed hero bands, dark sections |
| **1 — Hairline** | `inset 0 0 0 1px rgba(0,0,0,0.08)` | Default card chrome |
| **2 — Subtle** | `0 1px 1px rgba(0,0,0,0.02), 0 2px 2px rgba(0,0,0,0.04)` + hairline | Slightly elevated cards |
| **3 — Soft** | `0 2px 2px rgba(0,0,0,0.04), 0 8px 8px -8px rgba(0,0,0,0.04)` + hairline | Feature cards |
| **4 — Float** | `0 2px 2px rgba(0,0,0,0.04), 0 8px 16px -4px rgba(0,0,0,0.04)` + hairline | Pricing cards, popovers |
| **5 — Modal** | `0 1px 1px rgba(0,0,0,0.02), 0 8px 16px -4px rgba(0,0,0,0.04), 0 24px 32px -8px rgba(0,0,0,0.06)` + hairline | Modals, dialogs |

### 5.2 Shadow Rules

- **Stacked shadows** — multiple small offsets layered to fake natural light. Never a single heavy drop.
- **Inset hairline rings** always added so the card edge stays crisp.
- **Shadow-as-border philosophy**: semi-transparent shadows replace traditional borders for edge clarity and smoother transitions.
- Hierarchy comes from tonal surfaces and borders first; shadows stay subtle.

### 5.3 Depth Cues

- **Polarity-flipped dark band**: switching surface to `#171717` is the chief depth cue between bands.
- **Mesh gradient as atmospheric depth**: the hero's multi-stop gradient is the only "atmospheric" effect — applied as a flat 2D backdrop, never 3D.

### 5.4 Atmospheric Effects

| Effect | Value | Use |
|--------|-------|-----|
| **Noise texture** | Subtle noise PNG overlay at low opacity | Hero backgrounds, atmospheric depth — adds grain that prevents banding on large gradients |
| **Glass blur** | `backdrop-filter: blur(25px)` | Overlay panels, floating menus, modals that sit over content — creates frosted-glass depth |

```css
/* Noise overlay for hero backgrounds */
.hero::after {
  content: "";
  position: absolute;
  inset: 0;
  background: url("/noise.png") repeat;
  opacity: 0.03;
  pointer-events: none;
}

/* Glass blur for floating panels */
.glass-panel {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(25px);
  -webkit-backdrop-filter: blur(25px);
}

[data-theme="dark"] .glass-panel {
  background: rgba(0, 0, 0, 0.8);
}
```

Rules:

- Noise opacity stays below 0.05 — visible as texture, not as pattern.
- Glass blur requires a fallback solid background for browsers without `backdrop-filter`.
- Never use glass blur on scrollable content — it's for floating overlays only.

---

## 6. Motion

### 6.1 Principles

- **Instant is best.** A duration of `0ms` is often the snappiest choice. Only animate when it clarifies cause & effect or adds deliberate delight.
- **Honor `prefers-reduced-motion`.** Provide a reduced-motion variant or disable nonessential motion.
- **Compositor-friendly.** Only animate `transform` and `opacity`. Avoid layout-affecting properties (`width`, `height`, `top`, `left`).
- **Never `transition: all`.** Explicitly list only the properties you intend to animate.
- **Interruptible.** Animations must be cancelable by user input mid-animation.
- **Input-driven.** Avoid autoplay; animate in response to actions.

### 6.2 Durations & Easing

| Context | Duration | Easing |
|---------|----------|--------|
| State changes | ~150ms | `cubic-bezier(0.175, 0.885, 0.32, 1.1)` |
| Popovers, tooltips | ~200ms | Same |
| Overlays, modals | ~300ms | Same |

### 6.3 SVG Transforms

Apply CSS transforms to `<g>` wrappers and set `transform-box: fill-box; transform-origin: center;` to avoid Safari bugs.

---

## 7. Components

### 7.1 Buttons

| Variant | Background | Text | Typography | Radius | Height | Use |
|---------|-----------|------|------------|--------|--------|-----|
| `button-primary` | `gray-1000` | `background-100` | `button-14` | `sm` (6px) | 40px | Single most important action |
| `button-secondary` | `background-100` | `gray-1000` | `button-14` | `sm` (6px) | 40px | Secondary action, hairline border |
| `button-tertiary` | transparent | `gray-1000` | `button-14` | `sm` (6px) | 40px | Low-emphasis, tints on hover |
| `button-error` | `red-800` | `#ffffff` | `button-14` | `sm` (6px) | 40px | Destructive actions |
| `button-small` | — | — | `button-14` | `sm` (6px) | 32px | Compact context |
| `button-large` | — | — | `button-16` | `sm` (6px) | 48px | Marketing CTA |

**Button States:**

- Hover: step up fill (`100` → `200`), border (`400` → `500`)
- Active: step up again (`200` → `300`, `500` → `600`)
- Disabled: `gray-100` fill, `gray-700` text, `not-allowed` cursor
- Focus: two-layer ring — `box-shadow: 0 0 0 2px #ffffff, 0 0 0 4px #006bff`

### 7.2 Inputs

| Variant | Background | Text | Typography | Radius | Height |
|---------|-----------|------|------------|--------|--------|
| `input` | `background-100` | `gray-1000` | `label-14` | `sm` (6px) | 40px |
| `input-small` | — | — | `label-14` | `sm` (6px) | 32px |
| `input-large` | — | — | `label-16` | `sm` (6px) | 48px |

### 7.3 Cards

| Variant | Background | Radius | Padding | Shadow Level |
|---------|-----------|--------|---------|--------------|
| `card-default` | `background-100` | `sm` (6px) | 24px | Level 1 |
| `card-marketing` | `background-100` | `sm` (6px) | 24px | Level 3 |
| `card-marketing-large` | `background-100` | `md` (12px) | 32px | Level 4 |
| `card-soft` | `background-200` | `sm` (6px) | 24px | Level 1 |
| `card-dark` | `gray-1000` | `sm` (6px) | 32px | Level 0 |

### 7.4 Navigation

| Element | Height | Background | Typography |
|---------|--------|-----------|------------|
| Nav bar | 64px | `background-100` | `label-14` |
| Nav link | — | transparent | `label-14` |
| Nav CTA | 28px | `gray-1000` | `label-14` (500) |

### 7.5 Badges & Banners

| Variant | Background | Text | Radius | Padding |
|---------|-----------|------|--------|---------|
| `badge` | `background-200` | `gray-900` | `full` | 0 8px |
| `banner` | `background-200` | `gray-900` | `full` | 8px 12px |

### 7.6 Banner (Page-Level Messages)

Page or section-level messages with automatic icon assignment. Use `Tag` for inline item labels instead.

| Appearance | Icon | Use |
|------------|------|-----|
| `green` | Confetti/Check | Success and completion |
| `yellow`/`amber` | Warning | Caution and pending states |
| `red` | Warning | Critical states, irreversible actions |
| `blue` | Info | Informational elements |
| `gray` | Info | Neutral messages |

```tsx
<Banner appearance="green">Your API key has been generated.</Banner>
<Banner appearance="yellow">Your plan expires in 3 days.</Banner>
<Banner appearance="red">Build failed. Bundle exceeds 50 MB.</Banner>
<Banner appearance="blue">New feature: Webhooks are now available.</Banner>
```

Rules:

- Use `role="alert"` for error and warning banners.
- Banner auto-selects the icon based on `appearance`; never override the icon.
- One banner per section maximum. Stack vertically if multiple are needed.
- Banner is for page-level messages; use `Toast` for transient feedback.

### 7.7 Component State Pattern

Use a `state` prop instead of separate boolean props (`disabled`, `loading`, `readOnly`, `invalid`). Each state value is self-sufficient — `state="loading"` already prevents interaction, so don't also add `disabled`.

| State | Behavior |
|-------|----------|
| `normal` | Default interactive state |
| `loading` | Shows spinner, prevents interaction, keeps original label |
| `disabled` | Grayed out, `not-allowed` cursor |
| `read-only` | Displays value but not editable |
| `invalid` | Error styling applied |

```tsx
// ✅ Correct
<Button state="loading">Deploy Project</Button>
<Input state="invalid" />

// ❌ Wrong — redundant
<Button state="loading" disabled>Deploy Project</Button>
```

### 7.8 Marketing vs Product Component Separation

Marketing pages and product UI use **separate component systems**. Never mix them.

| System | Use For | Examples |
|--------|---------|----------|
| **Product UI** (`src/ui/`) | Dashboard, authenticated pages | `Button`, `TextField`, `Dialog`, `Select` |
| **Public primitives** (`src/website/`) | Marketing pages, landing pages | `PublicHeading`, `PublicText`, `PublicButton` |

Rules:

- Marketing pages use dark-first design; product UI supports both themes.
- Marketing `PublicHeading` sizes 7–8 use display font; product `Heading` uses body font.
- Marketing `PublicButton` has `white` | `black` | `fade` | `red` appearances; product `Button` has `white` | `gray` | `fade` | `fade-red` | `red`.
- Before creating a new component, search for an existing one in the correct system.

---

## 8. Interactions

### 8.1 Keyboard & Focus

- All flows are keyboard-operable, following [WAI-ARIA Authoring Patterns](https://www.w3.org/WAI/ARIA/apg/patterns/).
- Every focusable element shows a visible focus ring. Prefer `:focus-visible` over `:focus`.
- Use `:focus-within` for grouped controls.
- Never `outline-none` without a visual focus replacement.

### 8.2 Hit Targets

- Visual target and hit target must match. If visual target < 24px, expand hit target to ≥ 24px.
- On mobile, minimum touch target is 44px.
- No dead zones: if part of a control looks interactive, it should be interactive.
- Label + control share a single hit target for checkboxes/radios.

### 8.3 Forms

- `<input>` font size ≥ 16px on mobile to prevent iOS Safari auto-zoom.
- Never block paste. Never block keystrokes; allow any input and show validation.
- Placeholders end with `…` and show an example pattern (e.g., `sk-012345679…`).
- Keep submit button enabled until submission starts. Then disable, show spinner, keep original label.
- Add short show-delay (~150–300ms) to avoid flicker on fast responses.
- Errors shown inline next to fields; focus first error on submit.
- Every control has a `<label>` or `aria-label`.
- Set `autocomplete` and meaningful `name` values for autofill.
- Warn before navigation when unsaved changes exist.

### 8.4 Links & Routing

- Use `<a>` or `<Link>` for navigation. **Never** use `<div onClick>` or `<button>` for routing.
- Standard browser behavior (Cmd+Click, middle-click) must work.
- Deep-link everything: filters, tabs, pagination, expanded panels.

### 8.5 Drag & Drop

- Disable text selection and apply `inert` on dragged elements.
- Set `touch-action: manipulation` to prevent double-tap zoom.
- Set `-webkit-tap-highlight-color` intentionally.

### 8.6 URL as State

Persist UI state in the URL so refresh, sharing, and Back/Forward work. Use `nuqs` or similar.

### 8.7 Optimistic Updates

Update UI immediately when success is likely. On failure, show error and roll back or provide Undo.

---

## 9. Layout & Performance

- **Let browser size things.** Prefer Flex/Grid over JS measurement. Avoid `getBoundingClientRect` / `offsetHeight` in render.
- **Safe areas.** Full-bleed layouts use `env(safe-area-inset-*)` for notches.
- **Scrollbars.** Only render useful scrollbars. Use `overflow-x-hidden` on containers. Set `overscroll-behavior: contain` in modals/drawers.
- **Scroll positions persist.** Back/Forward restores prior scroll.
- **Large lists** (>50 items): virtualize (`virtua` or `content-visibility: auto`).
- **Preloading.** Critical above-fold images get `priority`. Fonts: `<link rel="preload" as="font" font-display="swap">`.
- **Preconnect.** `<link rel="preconnect">` for CDN/asset domains.
- **No image-caused CLS.** Set explicit `width` and `height` on `<img>`.
- **Network latency budgets.** `POST/PATCH/DELETE` complete in <500ms.
- **Hydration-safe.** Inputs must not lose focus or value after hydration.

---

## 10. Accessibility

- **Contrast.** Hold WCAG AA (4.5:1 for body text). Prefer [APCA](https://apcacontrast.com/) for perceptual accuracy.
- **Redundant status cues.** Don't rely on color alone; include text labels or icons.
- **ARIA labeling.** Icon-only buttons need `aria-label`. Images need `alt` (or `alt=""` if decorative). Decorative icons: `aria-hidden="true"`.
- **Async updates.** `aria-live="polite"` for toasts, loading states, inline validation.
- **Semantics before ARIA.** Prefer native elements (`button`, `a`, `label`, `table`) before `aria-*`.
- **Headings & skip link.** Hierarchical `<h1>`–`<h6>` and a "Skip to content" link.
- **`scroll-margin-top`** on heading anchors for deep-linking.
- **Locale-aware.** Format dates/numbers with `Intl.DateTimeFormat` / `Intl.NumberFormat`. Detect language via `Accept-Language` / `navigator.languages`, never IP/GPS.
- **Shield verbatim content.** Wrap brand names, code tokens, identifiers with `translate="no"`.

---

## 11. Voice & Content

### 11.1 Copywriting Principles

- **Active voice, 2nd person.** "Install the CLI" not "The CLI will be installed."
- **Title Case** for headings, buttons, labels, tabs ([Chicago style](https://title.sh/)). Sentence case for body, helper text, toasts.
- **Action-oriented.** Buttons use verb + noun: "Deploy Project", "Delete Member". Never "Confirm", "OK", or a bare verb.
- **Concise.** Use as few words as possible. Prefer `&` over `and` where space-constrained.
- **Numerals for counts.** "8 deployments" not "eight deployments".
- **Non-breaking spaces.** `10&nbsp;MB`, `⌘&nbsp;+&nbsp;K`, brand names.

### 11.2 Punctuation

- Use real ellipsis `…` instead of three periods `...`.
- Prefer curly quotes `"` `"` over straight quotes `" "`.
- Loading states end with `…`: "Deploying…", "Saving…".

### 11.3 Errors & Empty States

- **Constructive errors.** Don't just state the problem; guide the exit:
  - ❌ "Invalid API key"
  - ✅ "Your API key is incorrect or expired. Generate a new key in your account settings."
- **Empty states** point to the first action: "No deployments yet. Push to your Git repository to create one."
- **Toasts** name the specific thing that changed, drop trailing period, never say "successfully":
  - ❌ "Successfully deleted the project."
  - ✅ "Project deleted"

### 11.4 Placeholders

Signal emptiness by ending with `…` and showing an example pattern:

- `sk-012345679…`
- `+1 (123) 456-7890`

---

## 12. Do's and Don'ts

### Do

- Use the gray scale to rank information: `1000` for primary text, `900` for secondary, `700` for disabled.
- Prefer semantic tokens (`text-default`, `bg-elevated`, `border-error`) over raw primitives for component styling.
- Use `state` prop for component states (`loading`, `disabled`, `invalid`, `read-only`) — don't use separate booleans.
- Keep solid accent color for state and the single most important action per view.
- Show focus ring on every interactive element at `:focus-visible`.
- Apply typography tokens instead of setting font-size/line-height/weight by hand.
- Layer stacked shadows (multiple small offsets + inset hairline) rather than single heavy drops.
- Cycle surfaces: `background-100` → `background-200` → `gray-1000` polarity-flipped bands.
- Set every code block and technical eyebrow in mono. Mono is the voice of the platform.
- Tie interactive elements to URL state. Deep-link everything.
- Provide immediate optimistic updates with graceful rollbacks on failure.
- Ensure destructive actions have confirmation modals or an undo window.
- Use `Banner` for page-level messages; `Toast` for transient feedback.
- Separate marketing components from product UI — never mix the two systems.

### Don't

- Don't use positive letter-spacing on Geist Sans — it runs tight.
- Don't use `transition: all` or animate layout properties like `height`/`width`.
- Don't block pasting in inputs or use `preventDefault` on `onPaste`.
- Don't disable zoom (`maximum-scale=1` or `user-scalable=no`).
- Don't render `<button>` for links or `<div>` for buttons.
- Don't use `autoFocus` on mobile (triggers keyboard, causes layout shift).
- Don't signal state with color alone; pair with icon or text label.
- Don't use `background-200` as a general fill; it's for subtle separation only.
- Don't mix rounded and sharp corners, or more than two font weights, in one view.
- Don't swap `gray-*` for `background-*`; they're separate scales.
- Don't introduce new accent colours beyond the defined palette.
- Don't render headlines in all-caps. Sentence-case + negative tracking is non-negotiable.
- Don't promote Geist Sans to weight 700. Display ceiling is 600.
- Don't use raw primitives when a semantic token exists for the intent.
- Don't combine `state="loading"` with `disabled` — the state prop is self-sufficient.

---

## 13. Agent Prompt Guide

When instructing AI coding agents to generate UI with this design system:

### Quick Rules

- **Framework**: React / Next.js / Tailwind CSS
- **Typography**: Geist Sans/Mono, `"liga"` enabled, tabular-nums for data.
- **Spacing/Layout**: Flex/Grid, `min-w-0` on flex children for text truncation.
- **State**: URL-driven over `useState` for UI configuration.
- **Colors**: Use the gray scale tokens. Accent colors for state only.

### Example Prompts

- *"Create a hero section. Headline 48px Geist weight 600, tracking-tight (-2.88px), text-wrap: balance. CTA button is native `<button>`, keeps label but shows spinner on submit. Uses shadow-border `box-shadow: 0 0 0 1px rgba(0,0,0,0.08)`."*
- *"Build a form input for an API key. Must have explicit `<label>`, input font-size 16px (mobile safe), autocomplete='off', placeholder ending in '…', allows paste, validates on submit. Focus uses two-layer ring: `0 0 0 2px #fff, 0 0 0 4px #006bff`."*
- *"Design a 3-column card grid. Cards use stacked shadows (Level 3). Titles use Title Case. Images have explicit width/height to prevent CLS. Wrap card in `<Link>` for routing."*

### Review Checklist

When reviewing generated UI code:

1. Icon-only buttons need `aria-label`
2. Form controls need `<label>` or `aria-label`
3. `<button>` for actions, `<a>`/`<Link>` for navigation
4. Visible focus ring on all interactive elements
5. Never `transition: all` — list properties explicitly
6. Never block paste
7. Images need explicit `width`/`height`
8. Large lists (>50 items) need virtualization
9. `font-variant-numeric: tabular-nums` for number columns
10. `…` not `...`; curly quotes not straight quotes

---

## 14. Dark Theme

The dark theme uses the same token names with inverted values. Apply `color-scheme: dark` on `<html>` so scrollbars and native inputs get proper contrast. Set `<meta name="theme-color" content="#000000">` to align the browser's theme color.

### 14.1 Dark Gray Scale

| Step | Hex | Intent |
|------|-----|--------|
| `gray-100` | `#1a1a1a` | Default background (dark) |
| `gray-200` | `#222222` | Hover background |
| `gray-300` | `#2a2a2a` | Active background |
| `gray-400` | `#333333` | Default border |
| `gray-500` | `#444444` | Hover border |
| `gray-600` | `#555555` | Active border |
| `gray-700` | `#777777` | Solid fill, disabled text |
| `gray-800` | `#999999` | Solid fill, hover |
| `gray-900` | `#cccccc` | Secondary text & icons |
| `gray-1000` | `#ededed` | Primary text & icons |

### 14.2 Dark Surface Colors

| Token | Hex | Use |
|-------|-----|-----|
| `background-100` | `#000000` | Primary page & card surface |
| `background-200` | `#0a0a0a` | Secondary surface, subtle separation |

### 14.3 Dark Accent Adjustments

Accent scales shift slightly for dark backgrounds to maintain contrast:

| Scale | Light Mode Key | Dark Mode Key | Notes |
|-------|---------------|--------------|-------|
| Blue | `#0070f3` | `#3291ff` | Lighter for AA contrast on dark |
| Red | `#ee0000` | `#ff0000` | Brighter on dark surfaces |
| Amber | `#f5a623` | `#ffc107` | Increased luminance |
| Green | `#28a948` | `#4ceb5e` | Lighter green |
| Teal | `#00ac96` | `#00e3c4` | Brighter teal |
| Purple | `#7928ca` | `#a855f7` | Lighter purple |
| Pink | `#f22782` | `#ff69b4` | Lighter for AA contrast on dark |

### 14.4 Dark Shadow Stack

Shadows are near-invisible on dark surfaces. Use lighter border + subtle glow instead:

| Level | Treatment | Use |
|-------|-----------|-----|
| **0 — Flat** | No shadow, no border | Full-bleed sections |
| **1 — Hairline** | `inset 0 0 0 1px rgba(255,255,255,0.08)` | Default card chrome |
| **2 — Subtle** | `0 1px 1px rgba(255,255,255,0.02), 0 2px 2px rgba(255,255,255,0.04)` + hairline | Slightly elevated |
| **3 — Soft** | `0 2px 2px rgba(255,255,255,0.04), 0 8px 8px -8px rgba(255,255,255,0.04)` + hairline | Feature cards |
| **4 — Float** | `0 2px 2px rgba(255,255,255,0.04), 0 8px 16px -4px rgba(255,255,255,0.04)` + hairline | Popovers |
| **5 — Modal** | `0 1px 1px rgba(255,255,255,0.02), 0 8px 16px -4px rgba(255,255,255,0.04), 0 24px 32px -8px rgba(255,255,255,0.06)` + hairline | Modals |

### 14.5 Dark Component Overrides

| Component | Property | Light | Dark |
|-----------|----------|-------|------|
| `button-primary` | background | `gray-1000` (`#171717`) | `gray-1000` (`#ededed`) |
| `button-primary` | text | `background-100` (`#ffffff`) | `background-100` (`#000000`) |
| `button-secondary` | background | `background-100` | `background-100` |
| `button-secondary` | border | `gray-alpha-400` | `gray-alpha-400` |
| `input` | background | `background-100` | `background-100` |
| `input` | border | `gray-alpha-400` | `gray-alpha-400` |
| `card-default` | background | `background-100` | `background-100` |
| Focus ring | inner gap | `#ffffff` | `#000000` |
| Focus ring | outer ring | `#006bff` | `#3291ff` |

### 14.6 Dark Selection

| Token | Value |
|-------|-------|
| `selection-bg` | `#ededed` |
| `selection-fg` | `#0a0a0a` |

### 14.7 Dark Theme CSS

```css
/* Apply on <html> for dark mode */
color-scheme: dark;

/* Override surface tokens */
:root[data-theme="dark"] {
  --background-100: #000000;
  --background-200: #0a0a0a;
  --gray-100: #1a1a1a;
  --gray-200: #222222;
  --gray-300: #2a2a2a;
  --gray-400: #333333;
  --gray-500: #444444;
  --gray-600: #555555;
  --gray-700: #777777;
  --gray-800: #999999;
  --gray-900: #cccccc;
  --gray-1000: #ededed;
  --blue-700: #3291ff;
  --red-700: #ff0000;
  --amber-700: #ffc107;
  --green-700: #4ceb5e;
  --teal-700: #00e3c4;
  --purple-700: #a855f7;
  --pink-700: #ff69b4;
  --selection-bg: #ededed;
  --selection-fg: #0a0a0a;
}
```

### 14.8 Dark Theme Rules

- `color-scheme: dark` on `<html>` fixes scrollbar, input, and native UI contrast.
- `<meta name="theme-color">` must match the page background.
- Shadows use white/alpha instead of black/alpha.
- Native `<select>` needs explicit `background-color` and `color` (Windows dark-mode bug).
- Don't flip polarity of brand gradient — it stays the same in both themes.
- Interactive states step **down** the scale on dark (hover: `100` → `200` stays same direction, but visually lighter).

---

## 15. Tailwind CSS Configuration

Map all design tokens to Tailwind CSS theme configuration.

### 15.1 `tailwind.config.ts`

```typescript
import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class", '[data-theme="dark"]'],
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        background: {
          100: "var(--background-100)",
          200: "var(--background-200)",
        },
        gray: {
          100: "var(--gray-100)",
          200: "var(--gray-200)",
          300: "var(--gray-300)",
          400: "var(--gray-400)",
          500: "var(--gray-500)",
          600: "var(--gray-600)",
          700: "var(--gray-700)",
          800: "var(--gray-800)",
          900: "var(--gray-900)",
          1000: "var(--gray-1000)",
          "alpha-100": "var(--gray-alpha-100)",
          "alpha-200": "var(--gray-alpha-200)",
          "alpha-300": "var(--gray-alpha-300)",
          "alpha-400": "var(--gray-alpha-400)",
          "alpha-500": "var(--gray-alpha-500)",
          "alpha-600": "var(--gray-alpha-600)",
          "alpha-700": "var(--gray-alpha-700)",
          "alpha-800": "var(--gray-alpha-800)",
          "alpha-900": "var(--gray-alpha-900)",
          "alpha-1000": "var(--gray-alpha-1000)",
        },
        blue: {
          100: "var(--blue-100)",
          200: "var(--blue-200)",
          300: "var(--blue-300)",
          400: "var(--blue-400)",
          500: "var(--blue-500)",
          600: "var(--blue-600)",
          700: "var(--blue-700)",
          800: "var(--blue-800)",
          900: "var(--blue-900)",
          1000: "var(--blue-1000)",
        },
        red: {
          100: "var(--red-100)",
          200: "var(--red-200)",
          300: "var(--red-300)",
          400: "var(--red-400)",
          500: "var(--red-500)",
          600: "var(--red-600)",
          700: "var(--red-700)",
          800: "var(--red-800)",
          900: "var(--red-900)",
          1000: "var(--red-1000)",
        },
        amber: {
          100: "var(--amber-100)",
          200: "var(--amber-200)",
          300: "var(--amber-300)",
          400: "var(--amber-400)",
          500: "var(--amber-500)",
          600: "var(--amber-600)",
          700: "var(--amber-700)",
          800: "var(--amber-800)",
          900: "var(--amber-900)",
          1000: "var(--amber-1000)",
        },
        green: {
          100: "var(--green-100)",
          200: "var(--green-200)",
          300: "var(--green-300)",
          400: "var(--green-400)",
          500: "var(--green-500)",
          600: "var(--green-600)",
          700: "var(--green-700)",
          800: "var(--green-800)",
          900: "var(--green-900)",
          1000: "var(--green-1000)",
        },
        teal: {
          100: "var(--teal-100)",
          200: "var(--teal-200)",
          300: "var(--teal-300)",
          400: "var(--teal-400)",
          500: "var(--teal-500)",
          600: "var(--teal-600)",
          700: "var(--teal-700)",
          800: "var(--teal-800)",
          900: "var(--teal-900)",
          1000: "var(--teal-1000)",
        },
        purple: {
          100: "var(--purple-100)",
          200: "var(--purple-200)",
          300: "var(--purple-300)",
          400: "var(--purple-400)",
          500: "var(--purple-500)",
          600: "var(--purple-600)",
          700: "var(--purple-700)",
          800: "var(--purple-800)",
          900: "var(--purple-900)",
          1000: "var(--purple-1000)",
        },
        pink: {
          100: "var(--pink-100)",
          200: "var(--pink-200)",
          300: "var(--pink-300)",
          400: "var(--pink-400)",
          500: "var(--pink-500)",
          600: "var(--pink-600)",
          700: "var(--pink-700)",
          800: "var(--pink-800)",
          900: "var(--pink-900)",
          1000: "var(--pink-1000)",
        },
      },
      fontFamily: {
        sans: ["Geist Sans", "Inter", "system-ui", "-apple-system", "sans-serif"],
        mono: ["Geist Mono", "ui-monospace", "SFMono-Regular", "Menlo", "Monaco", "monospace"],
      },
      fontSize: {
        "heading-72": ["72px", { lineHeight: "72px", fontWeight: "600", letterSpacing: "-4.32px" }],
        "heading-64": ["64px", { lineHeight: "64px", fontWeight: "600", letterSpacing: "-3.84px" }],
        "heading-56": ["56px", { lineHeight: "56px", fontWeight: "600", letterSpacing: "-3.36px" }],
        "heading-48": ["48px", { lineHeight: "56px", fontWeight: "600", letterSpacing: "-2.88px" }],
        "heading-40": ["40px", { lineHeight: "48px", fontWeight: "600", letterSpacing: "-2.4px" }],
        "heading-32": ["32px", { lineHeight: "40px", fontWeight: "600", letterSpacing: "-1.28px" }],
        "heading-24": ["24px", { lineHeight: "32px", fontWeight: "600", letterSpacing: "-0.96px" }],
        "heading-20": ["20px", { lineHeight: "26px", fontWeight: "600", letterSpacing: "-0.4px" }],
        "heading-16": ["16px", { lineHeight: "24px", fontWeight: "600", letterSpacing: "-0.32px" }],
        "heading-14": ["14px", { lineHeight: "20px", fontWeight: "600", letterSpacing: "-0.28px" }],
        "copy-24": ["24px", { lineHeight: "36px" }],
        "copy-20": ["20px", { lineHeight: "36px" }],
        "copy-18": ["18px", { lineHeight: "28px" }],
        "copy-16": ["16px", { lineHeight: "24px" }],
        "copy-14": ["14px", { lineHeight: "20px" }],
        "copy-13": ["13px", { lineHeight: "18px" }],
        "label-20": ["20px", { lineHeight: "32px" }],
        "label-16": ["16px", { lineHeight: "20px" }],
        "label-14": ["14px", { lineHeight: "20px" }],
        "label-13": ["13px", { lineHeight: "16px" }],
        "label-12": ["12px", { lineHeight: "16px" }],
        "button-16": ["16px", { lineHeight: "20px", fontWeight: "500" }],
        "button-14": ["14px", { lineHeight: "20px", fontWeight: "500" }],
        "button-12": ["12px", { lineHeight: "16px", fontWeight: "500" }],
      },
      borderRadius: {
        sm: "6px",
        md: "12px",
        lg: "16px",
        full: "9999px",
      },
      spacing: {
        xxs: "4px",
        xs: "8px",
        sm: "12px",
        md: "16px",
        lg: "24px",
        xl: "32px",
        "2xl": "40px",
        "3xl": "48px",
        "4xl": "64px",
        "5xl": "96px",
      },
      boxShadow: {
        "level-1": "inset 0 0 0 1px rgba(0,0,0,0.08)",
        "level-2": "0 1px 1px rgba(0,0,0,0.02), 0 2px 2px rgba(0,0,0,0.04), inset 0 0 0 1px rgba(0,0,0,0.08)",
        "level-3": "0 2px 2px rgba(0,0,0,0.04), 0 8px 8px -8px rgba(0,0,0,0.04), inset 0 0 0 1px rgba(0,0,0,0.08)",
        "level-4": "0 2px 2px rgba(0,0,0,0.04), 0 8px 16px -4px rgba(0,0,0,0.04), inset 0 0 0 1px rgba(0,0,0,0.08)",
        "level-5": "0 1px 1px rgba(0,0,0,0.02), 0 8px 16px -4px rgba(0,0,0,0.04), 0 24px 32px -8px rgba(0,0,0,0.06), inset 0 0 0 1px rgba(0,0,0,0.08)",
        "focus-ring": "0 0 0 2px #ffffff, 0 0 0 4px #006bff",
        "dark-level-1": "inset 0 0 0 1px rgba(255,255,255,0.08)",
        "dark-level-2": "0 1px 1px rgba(255,255,255,0.02), 0 2px 2px rgba(255,255,255,0.04), inset 0 0 0 1px rgba(255,255,255,0.08)",
        "dark-level-3": "0 2px 2px rgba(255,255,255,0.04), 0 8px 8px -8px rgba(255,255,255,0.04), inset 0 0 0 1px rgba(255,255,255,0.08)",
        "dark-level-4": "0 2px 2px rgba(255,255,255,0.04), 0 8px 16px -4px rgba(255,255,255,0.04), inset 0 0 0 1px rgba(255,255,255,0.08)",
        "dark-level-5": "0 1px 1px rgba(255,255,255,0.02), 0 8px 16px -4px rgba(255,255,255,0.04), 0 24px 32px -8px rgba(255,255,255,0.06), inset 0 0 0 1px rgba(255,255,255,0.08)",
        "dark-focus-ring": "0 0 0 2px #000000, 0 0 0 4px #3291ff",
      },
      screens: {
        sm: "401px",
        md: "601px",
        lg: "961px",
        xl: "1200px",
        "2xl": "1400px",
      },
      transitionTimingFunction: {
        spring: "cubic-bezier(0.175, 0.885, 0.32, 1.1)",
      },
      keyframes: {
        "fade-in": {
          from: { opacity: "0" },
          to: { opacity: "1" },
        },
        "slide-up": {
          from: { transform: "translateY(4px)", opacity: "0" },
          to: { transform: "translateY(0)", opacity: "1" },
        },
      },
      animation: {
        "fade-in": "fade-in 150ms cubic-bezier(0.175, 0.885, 0.32, 1.1)",
        "slide-up": "slide-up 200ms cubic-bezier(0.175, 0.885, 0.32, 1.1)",
      },
    },
  },
  plugins: [],
};

export default config;
```

### 15.2 CSS Variables (Light Theme)

```css
:root {
  --background-100: #ffffff;
  --background-200: #fafafa;
  --gray-100: #f2f2f2;
  --gray-200: #ebebeb;
  --gray-300: #e6e6e6;
  --gray-400: #eaeaea;
  --gray-500: #c9c9c9;
  --gray-600: #a8a8a8;
  --gray-700: #8f8f8f;
  --gray-800: #7d7d7d;
  --gray-900: #4d4d4d;
  --gray-1000: #171717;
  --gray-alpha-100: #0000000d;
  --gray-alpha-200: #00000015;
  --gray-alpha-300: #00000014;
  --gray-alpha-400: #0000001a;
  --gray-alpha-500: #00000036;
  --gray-alpha-600: #0000003d;
  --gray-alpha-700: #00000070;
  --gray-alpha-800: #00000082;
  --gray-alpha-900: #000000b3;
  --gray-alpha-1000: #000000e8;
  --blue-100: #f0f7ff;
  --blue-200: #e9f4ff;
  --blue-300: #dfefff;
  --blue-400: #cae7ff;
  --blue-500: #94ccff;
  --blue-600: #48aeff;
  --blue-700: #006bff;
  --blue-800: #0059ec;
  --blue-900: #005ff2;
  --blue-1000: #002359;
  --red-100: #ffeeef;
  --red-200: #ffe8ea;
  --red-300: #ffe3e4;
  --red-400: #ffd7d6;
  --red-500: #ffb1b3;
  --red-600: #ff676d;
  --red-700: #fc0035;
  --red-800: #ea001d;
  --red-900: #d8001b;
  --red-1000: #47000c;
  --amber-100: #fff6de;
  --amber-200: #fff4cf;
  --amber-300: #fff1c1;
  --amber-400: #ffdc73;
  --amber-500: #ffc543;
  --amber-600: #ffa600;
  --amber-700: #ffae00;
  --amber-800: #ff9300;
  --amber-900: #aa4d00;
  --amber-1000: #561900;
  --green-100: #ecfdec;
  --green-200: #e5fce7;
  --green-300: #d3fad1;
  --green-400: #b9f5bc;
  --green-500: #82eb8d;
  --green-600: #4ce15e;
  --green-700: #28a948;
  --green-800: #279141;
  --green-900: #107d32;
  --green-1000: #003a00;
  --teal-100: #defffb;
  --teal-200: #ddfef6;
  --teal-300: #ccf9f1;
  --teal-400: #b1f7ec;
  --teal-500: #52f0db;
  --teal-600: #00e3c4;
  --teal-700: #00ac96;
  --teal-800: #00927f;
  --teal-900: #007f70;
  --teal-1000: #003f34;
  --purple-100: #faf0ff;
  --purple-200: #f9f0ff;
  --purple-300: #f6e8ff;
  --purple-400: #f2d9ff;
  --purple-500: #dfa7ff;
  --purple-600: #c979ff;
  --purple-700: #a000f8;
  --purple-800: #8500d1;
  --purple-900: #7d00cc;
  --purple-1000: #2f004e;
  --pink-100: #ffe8f6;
  --pink-200: #ffe8f3;
  --pink-300: #ffdfeb;
  --pink-400: #ffd3e1;
  --pink-500: #fdb3cc;
  --pink-600: #f97ea7;
  --pink-700: #f22782;
  --pink-800: #e4106e;
  --pink-900: #c41562;
  --pink-1000: #460523;
}
```

### 15.3 Semantic Token CSS Variables (Light Theme)

```css
:root {
  /* Surfaces */
  --bg-background: var(--background-100);
  --bg-subtle: var(--gray-100);
  --bg-elevated: var(--gray-200);

  /* Text */
  --text-emphasis: var(--gray-1000);
  --text-default: var(--gray-900);
  --text-muted: var(--gray-700);
  --text-placeholder: var(--gray-600);
  --text-on-brand: #ffffff;

  /* Borders */
  --border-default: var(--gray-400);
  --border-subtle: var(--gray-200);
  --border-interactive: var(--gray-alpha-300);

  /* Interactive (gray) */
  --bg-interactive: var(--gray-alpha-200);
  --bg-interactive-hover: var(--gray-alpha-300);
  --ring-focus: var(--gray-alpha-300);

  /* Brand */
  --bg-brand: var(--gray-1000);
  --bg-brand-hover: var(--gray-900);
  --ring-brand: var(--gray-alpha-400);

  /* Error */
  --bg-error: var(--red-200);
  --bg-error-hover: var(--red-400);
  --border-error: var(--red-600);
  --border-error-subtle: var(--red-400);
  --text-error: var(--red-700);
  --ring-error: var(--red-500);

  /* Warning */
  --bg-warning: var(--amber-200);
  --border-warning: var(--amber-600);
  --border-warning-subtle: var(--amber-400);
  --text-warning: var(--amber-700);

  /* Success */
  --bg-success: var(--green-200);
  --border-success: var(--green-600);
  --border-success-subtle: var(--green-400);
  --text-success: var(--green-700);

  /* Info */
  --bg-info: var(--blue-200);
  --border-info-subtle: var(--blue-400);
  --text-info: var(--blue-700);

  /* Link */
  --text-link: var(--blue-700);
  --border-link: var(--blue-700);
  --ring-link: var(--blue-500);
}
```

### 15.4 CSS Variables (Dark Theme Override)

```css
[data-theme="dark"] {
  --background-100: #000000;
  --background-200: #0a0a0a;
  --gray-100: #1a1a1a;
  --gray-200: #222222;
  --gray-300: #2a2a2a;
  --gray-400: #333333;
  --gray-500: #444444;
  --gray-600: #555555;
  --gray-700: #777777;
  --gray-800: #999999;
  --gray-900: #cccccc;
  --gray-1000: #ededed;
  --blue-700: #3291ff;
  --red-700: #ff0000;
  --amber-700: #ffc107;
  --green-700: #4ceb5e;
  --teal-700: #00e3c4;
  --purple-700: #a855f7;
  --pink-700: #ff69b4;

  /* Semantic overrides — most auto-resolve via var(), only asymmetric ones listed */
  --text-on-brand: #000000;
  --text-placeholder: var(--gray-700);
}
```

### 15.5 Tailwind Class Mapping Quick Reference

| Design Token | Tailwind Class |
|-------------|----------------|
| `background-100` | `bg-background-100` |
| `background-200` | `bg-background-200` |
| `gray-1000` text | `text-gray-1000` |
| `gray-900` text | `text-gray-900` |
| `gray-700` disabled | `text-gray-700` |
| `heading-48` | `text-heading-48` |
| `copy-16` | `text-copy-16` |
| `label-14` | `text-label-14` |
| `button-14` | `text-button-14` |
| `sm` radius | `rounded-sm` |
| `md` radius | `rounded-md` |
| `full` radius | `rounded-full` |
| `level-1` shadow | `shadow-level-1` |
| `level-3` shadow | `shadow-level-3` |
| Focus ring | `shadow-focus-ring` |
| Dark focus ring | `dark:shadow-dark-focus-ring` |
| Spring easing | `ease-spring` |
| Spacing `lg` | `p-lg` / `gap-lg` / `m-lg` |

#### Semantic Token Classes

| Semantic Token | Tailwind Class | Replaces |
|---------------|----------------|----------|
| `bg-background` | `bg-[var(--bg-background)]` | `bg-background-100` |
| `bg-subtle` | `bg-[var(--bg-subtle)]` | `bg-gray-100` |
| `bg-elevated` | `bg-[var(--bg-elevated)]` | `bg-gray-200` |
| `text-emphasis` | `text-[var(--text-emphasis)]` | `text-gray-1000` |
| `text-default` | `text-[var(--text-default)]` | `text-gray-900` |
| `text-muted` | `text-[var(--text-muted)]` | `text-gray-700` |
| `text-placeholder` | `text-[var(--text-placeholder)]` | `text-gray-600` |
| `border-default` | `border-[var(--border-default)]` | `border-gray-400` |
| `bg-error` | `bg-[var(--bg-error)]` | `bg-red-200` |
| `text-error` | `text-[var(--text-error)]` | `text-red-700` |
| `bg-success` | `bg-[var(--bg-success)]` | `bg-green-200` |
| `text-success` | `text-[var(--text-success)]` | `text-green-700` |
| `bg-warning` | `bg-[var(--bg-warning)]` | `bg-amber-200` |
| `text-warning` | `text-[var(--text-warning)]` | `text-amber-700` |
| `text-link` | `text-[var(--text-link)]` | `text-blue-700` |

Or define them in `tailwind.config.ts` extend:

```typescript
colors: {
  "bg-background": "var(--bg-background)",
  "bg-subtle": "var(--bg-subtle)",
  "bg-elevated": "var(--bg-elevated)",
  "text-emphasis": "var(--text-emphasis)",
  "text-default": "var(--text-default)",
  "text-muted": "var(--text-muted)",
  "text-placeholder": "var(--text-placeholder)",
  "border-default": "var(--border-default)",
  "bg-error": "var(--bg-error)",
  "text-error": "var(--text-error)",
  "bg-success": "var(--bg-success)",
  "text-success": "var(--text-success)",
  "bg-warning": "var(--bg-warning)",
  "text-warning": "var(--text-warning)",
  "text-link": "var(--text-link)",
}
```

### 15.6 Responsive Pattern Examples

```tsx
// Hero section
<section className="px-md py-4xl md:py-5xl">
  <h1 className="text-heading-48 md:text-heading-64 tracking-tight text-balance">
    Build and deploy on the AI Cloud.
  </h1>
</section>

// Card grid — using semantic tokens
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-lg">
  <div className="bg-[var(--bg-elevated)] rounded-sm p-lg shadow-level-3">
    <h3 className="text-[var(--text-emphasis)] text-heading-24">Title</h3>
    <p className="text-[var(--text-default)] text-copy-14">Description</p>
  </div>
</div>

// Button — using semantic tokens
<button className="bg-[var(--bg-brand)] text-[var(--text-on-brand)] text-button-14 rounded-sm h-10 px-2.5
  hover:bg-[var(--bg-brand-hover)]
  focus-visible:shadow-focus-ring focus-visible:outline-none
  disabled:bg-[var(--bg-subtle)] disabled:text-[var(--text-muted)] disabled:cursor-not-allowed
  transition-colors duration-150 ease-spring">
  Deploy Project
</button>

// Error input — using semantic tokens
<input className="bg-[var(--bg-error)] border-[var(--border-error)] text-[var(--text-emphasis)]
  rounded-sm h-10 px-3 text-label-14
  focus-visible:shadow-[var(--ring-error)]" />

// Banner
<div role="alert" className="bg-[var(--bg-success)] border-[var(--border-success-subtle)] rounded-md p-md">
  <span className="text-[var(--text-success)]">Your API key has been generated.</span>
</div>

// Dark mode — semantic tokens auto-resolve, no dark: needed for most cases
<div className="bg-[var(--bg-elevated)] rounded-sm p-lg shadow-level-3">
  ...
</div>
```

---

## References

- [Vercel Design Guidelines](https://vercel.com/design/guidelines)
- [Vercel Geist Design System](https://vercel.com/design)
- [Web Interface Guidelines (vercel-labs)](https://github.com/vercel-labs/web-interface-guidelines)
- [Awesome Design MD — Vercel](https://github.com/VoltAgent/awesome-design-md/tree/main/design-md/vercel)
- [Geist Font](https://vercel.com/font)
- [Resend Design Skills](https://github.com/resend/design-skills)
- [Resend Design System](https://resend.com/design)
