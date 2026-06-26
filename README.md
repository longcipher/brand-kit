# LongCipher Design System

A Vercel Geist-inspired design system — minimal, high-contrast, developer-focused. Stark black-and-ink on near-white canvas, with a multi-color mesh gradient as the sole decorative system.

## Design Philosophy

> Interfaces succeed because of hundreds of choices.

**Earn your pixel.** Every element must justify its existence. The page is overwhelmingly white (`#ffffff`) with near-black (`#171717`) text, creating a gallery-like emptiness where content stands. This isn't minimalism as decoration — it's minimalism as engineering principle.

**Core tenets:**

- **Content over chrome.** The surface disappears; the information stands.
- **Consistency over novelty.** Reuse tokens, patterns, and rhythms.
- **Accessibility is a requirement.** WCAG AA contrast, keyboard-operable flows, visible focus rings.
- **Shadow-as-border.** Semi-transparent shadows replace traditional borders for subtler depth.
- **Negative tracking is the voice.** Display type uses aggressive negative letter-spacing — text as compressed infrastructure.

## Files

| File | Description |
|------|-------------|
| **[DESIGN.md](DESIGN.md)** | Complete design system specification — colors, typography, spacing, components, interactions, voice |
| **[lc.svg](lc.svg)** | Pure logo (no text/slogan) |
| **[lc11.svg](lc11.svg)** | 1:1 logo with text |
| **[lc31.svg](lc31.svg)** | 3:1 logo with text and slogan |
| **[lc43.svg](lc43.svg)** | 4:3 logo with text and slogan |
| **[lc169.svg](lc169.svg)** | 16:9 logo with text and slogan |

## Quick Reference

### Colors

```text
Primary:    #171717  (ink-near-black)
Background: #ffffff  (pure white)
Canvas Soft: #fafafa  (page body)
Hairline:   #ebebeb  (borders, dividers)
Link:       #0070f3  (blue)
Error:      #ee0000  (red)
Warning:    #f5a623  (amber)
Pink:       #ff0080  (highlight)
```

### Typography

```text
Display:   Geist Sans, 600 weight, -2.4px tracking
Body:      Geist Sans, 400 weight, 0 tracking
Code:      Geist Mono, 400 weight, 12-13px
```

### Spacing

```text
Base:  4px
Group: 8px → 16px → 32px (three-step rhythm)
```

### Radius

```text
Controls:  6px
Modals:    12px
Fullscreen: 16px
Pills:     9999px
```

### Dark Theme

```text
Surfaces:  #000000 → #0a0a0a
Text:      #ededed (primary), #cccccc (secondary)
Shadows:   White/alpha instead of black/alpha
Focus:     0 0 0 2px #000, 0 0 0 4px #3291ff
```

### Tailwind Mapping

```text
Colors:    bg-background-100, text-gray-1000, bg-blue-700
Type:      text-heading-48, text-copy-16, text-label-14
Shadow:    shadow-level-1 ... shadow-level-5
Radius:    rounded-sm (6px), rounded-md (12px), rounded-full (9999px)
Motion:    ease-spring, transition-colors duration-150
Dark:      dark:shadow-dark-level-3, dark:shadow-dark-focus-ring
```

### Semantic Tokens (Resend-Inspired)

```text
Surfaces:  bg-background, bg-subtle, bg-elevated
Text:      text-emphasis, text-default, text-muted, text-placeholder
Borders:   border-default, border-subtle, border-interactive
States:    bg-error, bg-success, bg-warning, bg-info, text-link
Brand:     bg-brand, bg-brand-hover, ring-brand
```

Semantic tokens decouple intent from raw values — prefer them over primitives for component styling. They auto-resolve in dark mode.

See [DESIGN.md §14](DESIGN.md#14-dark-theme) for full dark theme tokens and [§15](DESIGN.md#15-tailwind-css-configuration) for the complete Tailwind config.

## References

- [Vercel Design Guidelines](https://vercel.com/design/guidelines)
- [Vercel Geist Design System](https://vercel.com/design)
- [Web Interface Guidelines (vercel-labs)](https://github.com/vercel-labs/web-interface-guidelines)
- [Awesome Design MD — Vercel](https://github.com/VoltAgent/awesome-design-md/tree/main/design-md/vercel)
- [Geist Font](https://vercel.com/font)
- [Resend Design Skills](https://github.com/resend/design-skills)
- [Resend Design System](https://resend.com/design)
