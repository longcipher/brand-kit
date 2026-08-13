# LongCipher Motion & Audio Language

Defines how motion and audio behave in LongCipher explainers. The goal is *calm, engineered motion* — the visual counterpart of the "earn your pixel" philosophy.

## 1. Motion Principles

- **Minimal & engineered.** Slide + fade combinations. No bouncy gimmicks, no decorative loops, no random motion.
- **One idea at a time.** A scene enters, holds, and yields. Never more than 3 simultaneous animations.
- **Compositor-friendly.** Only animate `transform` and `opacity`. Never animate layout properties (`width`, `height`, `top`, `left`).
- **Sync is absolute.** Every scene's animation window equals the scene's audio duration (from `timestamps.json`).

## 2. Motion Vocabulary (GSAP)

### Easings

| Context | Easing | Duration |
|---------|--------|----------|
| Scene container entrance | `power3.out` | 0.6s |
| Headline reveal | `power3.out` | 0.5s |
| Bullet / card stagger | `power3.out` | 0.4s each, `stagger: 0.12` |
| Eyebrow / mono label | `power2.out` | 0.4s |
| Keyword emphasis (scale) | `back.out(1.7)` | 0.5s |
| Scene transition (out) | `power2.inOut` | 0.3s |
| Caption pop-in | `power3.out` | 0.3s |

### Entrance Pattern (per scene)

```js
// absolute timeline, aligned to timestamps.json
tl.set(scene, { autoAlpha: 1 });
tl.fromTo(scene.querySelector(".scene-eyebrow"),
  { y: -12, autoAlpha: 0 },
  { y: 0, autoAlpha: 1, duration: 0.4, ease: "power2.out" },
  sceneStart + 0.1);
tl.fromTo(scene.querySelector(".scene-title"),
  { y: 24, autoAlpha: 0 },
  { y: 0, autoAlpha: 1, duration: 0.5, ease: "power3.out" },
  sceneStart + 0.25);
tl.fromTo(scene.querySelectorAll(".scene-bullet"),
  { y: 20, autoAlpha: 0 },
  { y: 0, autoAlpha: 1, duration: 0.4, ease: "power3.out", stagger: 0.12 },
  sceneStart + 0.5);
tl.fromTo(scene.querySelector(".scene-code"),
  { y: 16, autoAlpha: 0 },
  { y: 0, autoAlpha: 1, duration: 0.5, ease: "power2.out" },
  sceneStart + 0.9);
```

Offset the first entrance by 0.1–0.3s. Keep at least three ease styles per scene.

### Keyword Emphasis

When narration hits a key term, scale the term 1.0 → 1.05 and tint it the scene accent:

```js
tl.to(term, { scale: 1.05, color: "#0070f3", duration: 0.5, ease: "back.out(1.7)" }, termStart);
tl.to(term, { scale: 1.0, duration: 0.4, ease: "power2.out" }, termStart + 1.2);
```

Use sparingly — one emphasis per scene at most.

### Captions

Bottom-centered `.cap` element, `#ffffff` on `rgba(17,17,17,0.55)` pill, `backdrop-filter: blur(12px)`, radius 14px, pop-in 0.3s. The caption text is **identical** to the narration text for that scene.

## 3. Audio Language

### Narration (VO)

- Generated with the `hyperframes` CLI bundled Kokoro TTS — no API key, no Python.
- **Mandarin default:** `zf_xiaobei` (see `references/tts.md` for the full voice table).
- **Pace guidance (Kokoro speed):**
  - `0.7–0.8` — tutorial / complex technical content
  - `1.0` — natural default
  - `1.1–1.2` — intros, upbeat
- Target: ~3.2–3.6 chars/sec for zh, ~2.4 words/sec for en.
- Voice tone: **calm, precise, trustworthy** — a technical teacher, not a salesman.

### Music / SFX (optional)

- **BGM:** Lo-Fi or ambient tech pad. Keep it under the voice: target ≈ **-22 dB** relative to VO; never let it compete with narration.
- **SFX:** soft whooshes for scene transitions at most. No UI clicks, no game-like pings.
- If no music asset is available, deliver clean VO — silence is on-brand.

## 4. Timing Contract

The master timeline is **absolute**, driven by `timestamps.json`:

| Field | Meaning |
|-------|---------|
| `scenes[i].start` | Timeline second the scene + its audio begin |
| `scenes[i].end` | Timeline second the scene ends |
| `scenes[i].duration` | `end - start`, must equal the audio clip duration |
| `data-duration` (composition) | Sum of all scene durations + 0.5s tail |

Rules:

1. Scene `data-duration` == scene audio duration (from ffprobe).
2. Audio `<audio class="clip">` starts at `scenes[i].start`, duration = scene duration.
3. Caption `.cap.clip` starts at `scenes[i].start`, duration = scene duration.
4. Final scene gets a 0.5s fade-out tail so the video ends cleanly, not abruptly.

## 5. Duration Budget

For a `meta.target_seconds` of T:

```text
scenes      = 5–8 scenes
per scene   ≈ T / scenes.length   (aim 8–20s per scene)
intro hook  ≈ first scene carries the title + thesis
closing     ≈ last scene is a recap + "LongCipher" lockup
```

If the narration runs long, trim prose before scaling the timeline — never compress a scene's audio to fit.
