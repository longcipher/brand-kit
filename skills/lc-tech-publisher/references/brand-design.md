# LongCipher Brand Design System (Video & Cover Tokens)

This is the render-side distillation of the LongCipher design system. The full spec lives in the repo root `DESIGN.md`; every token below is a *hard rule* for generated HTML. Do not invent colors, weights, or spacings outside this document.

## Design Philosophy

- **Earn your pixel.** Every element on screen justifies itself. If removal doesn't break comprehension, remove it.
- **Content is king.** The surface disappears; the information stands. Whitespace is structure, not emptiness.
- **Consistency over novelty.** Reuse tokens and rhythms. Surprise belongs in the content, not the chrome.
- **Mono is the voice of the platform.** Technical eyebrows, code, and labels live in JetBrains Mono.

## 1. Colors

### Surfaces

| Token | Light | Dark | Use |
|-------|-------|------|-----|
| `background-100` | `#fafbfc` | `#0a0a0c` | Primary canvas (default for explainer scenes) |
| `background-200` | `#f6f7f9` | `#2a2d33` | Secondary surface, subtle separation |
| `ink-100` | `#171718` | `#ededed` | Primary text, headings |
| `ink-900` | `#4e5159` | `#b4b8c2` | Secondary text, body copy |
| `ink-700` | `#888d98` | `#888d98` | Muted captions, metadata |
| `hairline` | `#e0e2e8` | `#2a2d33` | Borders, dividers, hairlines |

### Accent (state + link only)

| Token | Hex | Use |
|-------|-----|-----|
| `blue-700` | `#0a72ef` | The **single** accent — links, focus, keywords, the one emphasized moment per scene |
| `red-700` | `#ff5b4f` | Errors, destructive (rarely on screen) |

**Accent budget:** one accent only — `#0a72ef`. No second hue, no rainbow, no pink/amber/green multi-accent. Blue is used for keywords/emphasis only; solid blue for the single most important moment per scene.

### Atmosphere (restrained, single-blue)

No rainbow mesh gradients. The only atmospheric device is a single, low-alpha blue radial wash, used sparingly as a large backdrop — never miniaturized, never as an icon.

```css
/* Hero atmosphere — covers and scene intro backgrounds only */
.bg-atmosphere {
  background:
    radial-gradient(1000px 600px at 25% 30%, rgba(10,114,239,0.10), transparent 65%),
    radial-gradient(900px 700px at 80% 40%, rgba(10,114,239,0.06), transparent 60%);
}
```

## 2. Typography

### Font Families

| Role | Family | Fallback |
|------|--------|----------|
| Sans (UI, prose, headings) | DM Sans | `system-ui, -apple-system, sans-serif` |
| Mono (code, eyebrows, labels) | JetBrains Mono | `ui-monospace, SFMono-Regular, Menlo, monospace` |

Use local/system fonts at render time — do not rely on CDN font fetches. System-ui is an acceptable substitute if DM Sans is not bundled.

### Heading & Body Tokens (scaled for 1920×1080)

| Token | Size | Weight | Line Height | Tracking | Use |
|-------|------|--------|-------------|----------|-----|
| `display` | 120px | 700 | 1.0 | `-0.02em` | Cover hero title |
| `heading-1` | 72px | 700 | 1.1 | `-0.02em` | Scene headline |
| `heading-2` | 48px | 600 | 1.15 | `-0.015em` | Sub-headline |
| `copy` | 36px | 400 | 1.4 | `0` | Body, bullets |
| `label` | 28px | 400 | 1.3 | `0` | Metadata, small text |
| `eyebrow` | 24px | 400 | 1.2 | `0.08em` | Mono, uppercase corner label |
| `code` | 30px | 400 | 1.5 | `0` | Mono code block |
| `caption` | 44px | 600 | 1.2 | `-0.01em` | Bottom speech caption |

**Rules:**

- Display/headings may use **700**; body stays 400. Avoid 800+.
- Display and headings use **negative tracking** (`-0.02em`). Never positively letter-space DM Sans headings.
- Sentence-case headlines. The deliberate period is part of the voice.
- Mono for the technical layer only: eyebrows, code, terminal labels. Body paragraphs are never mono.

## 3. Spacing (4px base)

| Token | Value | Use |
|-------|-------|-----|
| `xxs` | 4px | Tight gaps |
| `xs` | 8px | Inside-group gaps |
| `sm` | 12px | Compact gaps |
| `md` | 16px | Between-group gaps |
| `lg` | 24px | Card padding |
| `xl` | 32px | Section padding |
| `2xl` | 40px | Large section padding |
| `4xl` | 64px | Scene padding / margins |

Rhythm: 8px inside a group → 16px between groups → 32–40px between sections.

## 4. Shapes & Elevation

| Token | Value |
|-------|-------|
| `radius-sm` | 2px (the only radius — cards, controls, code blocks) |

**No pills, no circular avatars, no 6/12/16px rounding.** Sharp, technical edges throughout.

**Shadow-as-border** — semi-transparent shadows replace borders for edge clarity:

```css
.hairline {
  box-shadow: inset 0 0 0 1px rgba(23, 23, 24, 0.08);
}
.card {
  box-shadow:
    0 2px 2px rgba(23, 23, 24, 0.04),
    0 8px 8px -8px rgba(23, 23, 24, 0.04),
    inset 0 0 0 1px rgba(23, 23, 24, 0.08);
}
```

Dark theme: use `rgba(255,255,255,…)` alpha shadows instead.

## 5. Brand Lockup

- **Logo:** the vector mark from `assets/logos/lc.svg` (monochrome geometric). Never stretch, never rotate the mark, never recolor it, never add a border or glow around it.
- Lockup on covers: mark top-left at 48px, sized 120px, followed by the wordmark "LongCipher" in DM Sans 700, `#171718`.
- The single-blue atmospheric wash is the only decoration. Do not stack additional decorations.

## 6. Layout Grid (1920×1080)

- 64px outer margin, 24px gutter, 12-column grid.
- Scene content column: max 1600px, centered.
- Bottom caption zone: centered, y ≈ 980px, max width 1600px.
- Code blocks: full content column width, `background-200`, hairline, radius-sm, mono 30px.
- Eyebrow: top-left corner (48, 48), mono 24px, `#8f8f8f`, uppercase, letter-spacing 0.08em.

## 7. Voice & Content

- Active voice, second person: "Install the CLI", not "The CLI will be installed."
- Concise. As few words as possible. Numerals for counts ("8 deployments").
- Title Case / 中文标题句首大写 for headings; sentence case for body.
- Non-breaking spaces in code: `10&nbsp;MB`, `⌘&nbsp;+&nbsp;K`.
- Errors are constructive: state the problem and the exit, never just the problem.

## 8. Do / Don't

**Do:**

- Cycle surfaces `background-100` → `background-200` → dark `ink-100` bands for depth.
- Keep solid accent for one emphasized element per scene.
- Set eyebrows, code, and terminal labels in mono.
- Use hairline + stacked shadows instead of heavy borders.
- Keep scenes airy — whitespace is the primary layout tool.

**Don't:**

- Don't introduce new accent colors beyond the single blue `#0a72ef`.
- Don't use rainbow/mesh gradients or multi-color backdrops.
- Don't use positive letter-spacing on DM Sans headings.
- Don't render headings in all-caps (sentence case + negative tracking is non-negotiable).
- Don't use weight 800+.
- Don't mix rounded and sharp corners in one scene — corners are always 2px.
- Don't put body copy in mono.
- Don't use AI-default fonts (Geist, Inter, Roboto).
