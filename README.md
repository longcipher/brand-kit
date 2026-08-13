# LongCipher Design System

A restrained, technical design system for the LongCipher account portal and brand surface. Near-white canvas, near-black ink, one blue accent, shadow-as-border depth, precise typographic hierarchy. No AI-default flourishes — no rainbow gradients, no pillowy corners, no saturated default fonts.

## Design Philosophy

> Design serves the task. Every element earns its pixel.

**Earn your pixel.** Every element must justify its existence. The page is overwhelmingly off-white (`#fafbfc`) with near-black (`#171718`) text, creating a quiet surface where content stands. This isn't minimalism as decoration — it's minimalism as engineering principle.

**Core tenets:**

- **Content over chrome.** The surface disappears; the information stands.
- **Consistency over novelty.** Reuse tokens, patterns, and rhythms.
- **Accessibility is a requirement.** WCAG AA contrast, keyboard-operable flows, visible focus rings.
- **Shadow-as-border.** Semi-transparent shadows replace traditional borders for subtler depth.
- **Sharp edges.** Avoid rounded corners — 2px is the ceiling. Precise, technical, deliberate.
- **One accent.** A single blue (`#0a72ef`). No second hue, no rainbow.

## Files

| File | Description |
|------|-------------|
| **[DESIGN.md](DESIGN.md)** | Complete design system specification — colors, typography, spacing, components, interactions, voice |
| **[lc.svg](lc.svg)** | Pure logo (no text/slogan) |
| **[lc11.svg](lc11.svg)** | 1:1 logo with text |
| **[lc31.svg](lc31.svg)** | 3:1 logo with text and slogan |
| **[lc43.svg](lc43.svg)** | 4:3 logo with text and slogan |
| **[lc169.svg](lc169.svg)** | 16:9 logo with text and slogan |
| **[skills/lc-tech-publisher](skills/lc-tech-publisher/)** | Agent Skill — turn an article into a LongCipher cover + podcast + explainer video |

## Agent Skill: LongCipher Tech Publisher

After pushing this repo to GitHub, install the skill with:

```bash
npx skills add longcipher/brand-kit --skill lc-tech-publisher --full-depth
```

Then ask your agent (Claude Code / Cursor / Codex):

> 用 lc-tech-publisher 把这篇文章转成我们的品牌媒体包(封面 + 播客 + 视频)

It runs a 7-step local pipeline — article parsing, narration via Microsoft Edge Neural TTS by default (`zh-CN-yunxi`, free, no API key, no reference voice; `edge-tts` installed via `uv sync` + internet) with an optional local Fun-CosyVoice3-0.5B brand-voice clone, branded cover, HyperFrames composition with audio-synced GSAP timelines — and delivers `output/cover.png`, `output/podcast_full.mp3`, and `output/explainer_video.mp4`. The orchestration scripts are Python, managed with `uv`; only the HyperFrames render step wraps a Node runtime via `npx`.

See [skills/lc-tech-publisher/README.md](skills/lc-tech-publisher/README.md) for the full workflow.

## Quick Reference

### Colors

```text
Primary:    #171718  (near-black ink, blue-tinted)
Background: #fafbfc  (off-white canvas)
Surface:    #ffffff  (pure white cards)
Hairline:   #e0e2e8  (neutral-300, borders/dividers)
Blue:       #0a72ef  (the single accent — actions, links, focus)
Error:      #ff5b4f  (red, errors/destructive)
Focus:      hsla(212,100%,48%,1)
```

### Typography

```text
Display:   DM Sans, 700 weight, -0.02em tracking
Body:      DM Sans, 400 weight, 0 tracking
Code:      JetBrains Mono, 400 weight, tabular-nums
```

### Spacing

```text
Base:  4px
Group: 8px → 16px → 32px (three-step rhythm)
```

### Radius — keep it sharp

```text
All elements: 2px (the only radius in the system)
No pills, no circular avatars, no 6/12/16px rounding.
```

### Dark Theme

```text
Surfaces:  #0a0a0c → #2a2d33
Text:      #ededed (primary), #b4b8c2 (secondary)
Shadows:   White/alpha instead of black/alpha
Focus:     0 0 0 1px hsla(212,100%,48%,1), 0 0 0 4px hsla(212,100%,48%,0.18)
```

### Tailwind Mapping (v4)

```text
Colors:    bg-canvas, bg-surface, text-ink, bg-blue, bg-error
Type:      font-sans (DM Sans), font-mono (JetBrains Mono)
Shadow:    shadow-border (ring), shadow-card, shadow-elevated
Radius:    rounded-sm (2px) — the only radius
Motion:    transition-[transform,opacity] duration-150
Dark:      dark:shadow-elevated, dark:shadow-focus-ring
```

### Semantic Tokens

```text
Surfaces:  bg-canvas, bg-surface, bg-subtle
Text:      text-ink, text-body, text-muted, text-placeholder
Borders:   shadow-border (hairline via shadow)
States:    bg-error, text-link, ring-blue
Brand:     bg-blue, ring-blue
```

Semantic tokens decouple intent from raw values — prefer them over primitives for component styling. They auto-resolve in dark mode.

See [DESIGN.md](DESIGN.md) for the complete spec (color, typography, shadow-as-border, components, voice, a11y).

## References

- [Vercel Design Guidelines](https://vercel.com/design/guidelines)
- [Vercel Geist Design System](https://vercel.com/design)
- [Web Interface Guidelines (vercel-labs)](https://github.com/vercel-labs/web-interface-guidelines)
- [Awesome Design MD — Vercel](https://github.com/VoltAgent/awesome-design-md/tree/main/design-md/vercel)
- [Geist Font](https://vercel.com/font)
- [Resend Design Skills](https://github.com/resend/design-skills)
- [Resend Design System](https://resend.com/design)
