#!/usr/bin/env python3
"""build_composition.py — generate the HyperFrames video composition from
script.json + timestamps.json.

Usage:
  uv run python scripts/build_composition.py --script dist/script.json \
      --timings dist/timestamps.json --out dist/video

Produces:
  dist/video/index.html         master composition (scenes + captions + audio)
  dist/video/hyperframes.json   project config

Scene data-duration is set EXACTLY to the scene audio duration from
timestamps.json, and the GSAP timeline is absolute and aligned to it.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HYPERFRAMES_JSON = '{\n  "$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",\n  "paths": { "assets": "assets" }\n}\n'

STYLE = """
      :root {
        --bg-100: #ffffff;
        --bg-200: #fafafa;
        --ink-100: #171717;
        --ink-900: #4d4d4d;
        --ink-700: #8f8f8f;
        --hairline: #ebebeb;
        --accent: #0070f3;
      }
      * { margin: 0; padding: 0; box-sizing: border-box; }
      body, html {
        width: 1920px; height: 1080px;
        background: var(--bg-100);
        overflow: hidden;
        font-family: "Inter", "Geist Sans", system-ui, -apple-system, sans-serif;
        color: var(--ink-100);
      }
      #master-root { position: relative; width: 1920px; height: 1080px; }

      /* ── Scene layout ── */
      .scene {
        position: absolute; inset: 0;
        display: flex; flex-direction: column;
        justify-content: center;
        padding: 64px 160px;
        background: var(--bg-100);
        visibility: hidden;
      }
      .scene-bg-mesh {
        position: absolute; inset: 0;
        background:
          radial-gradient(900px 500px at 22% 30%, rgba(0,124,240,0.20), transparent 65%),
          radial-gradient(1100px 700px at 80% 35%, rgba(0,223,216,0.16), transparent 60%),
          radial-gradient(700px 500px at 50% 85%, rgba(121,40,202,0.12), transparent 65%);
        opacity: 0.6;
        pointer-events: none;
      }
      .scene-eyebrow {
        font-family: "Geist Mono", ui-monospace, SFMono-Regular, Menlo, monospace;
        font-size: 24px; letter-spacing: 0.08em; text-transform: uppercase;
        color: var(--ink-700);
        margin-bottom: 24px;
      }
      .scene-title {
        font-size: 72px; font-weight: 600; line-height: 1.1;
        letter-spacing: -0.02em; text-wrap: balance;
        max-width: 1500px;
        margin-bottom: 40px;
      }
      .scene-bullets { list-style: none; max-width: 1400px; }
      .scene-bullet {
        display: flex; align-items: baseline; gap: 16px;
        font-size: 36px; font-weight: 400; line-height: 1.4;
        color: var(--ink-900);
        margin-bottom: 16px;
      }
      .bullet-dot {
        flex: 0 0 12px; height: 12px; align-self: center;
        border-radius: 9999px;
        background: var(--accent);
      }
      .scene-code {
        margin-top: 32px;
        padding: 28px 32px;
        background: var(--bg-200);
        box-shadow: inset 0 0 0 1px rgba(0,0,0,0.08);
        border-radius: 6px;
        font-family: "Geist Mono", ui-monospace, SFMono-Regular, Menlo, monospace;
        font-size: 30px; line-height: 1.5;
        color: var(--ink-100);
        max-width: 1500px;
        overflow: hidden;
        white-space: pre-wrap;
      }

      /* ── Caption ── */
      .cap {
        position: absolute;
        bottom: 88px; left: 50%;
        transform: translateX(-50%);
        max-width: 1600px;
        padding: 14px 32px;
        border-radius: 14px;
        background: rgba(23,23,23,0.55);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        color: #ffffff;
        font-size: 44px; font-weight: 600; line-height: 1.2;
        letter-spacing: -0.01em;
        text-align: center;
        visibility: hidden;
        z-index: 50;
      }
"""


def die(msg: str) -> None:
    sys.stderr.write(f"✗ {msg}\n")
    sys.exit(1)


def esc(s) -> str:
    return (
        str(s if s is not None else "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def esc_attr(s) -> str:
    return esc(s).replace('"', "&quot;")


def main() -> None:
    p = argparse.ArgumentParser(description="Build the HyperFrames video composition")
    p.add_argument("--script", default="dist/script.json")
    p.add_argument("--timings", default="dist/timestamps.json")
    p.add_argument("--out", default="dist/video")
    args = p.parse_args()

    script_path = Path(args.script)
    timings_path = Path(args.timings)
    out_dir = Path(args.out)

    if not script_path.exists():
        die(f"missing script: {script_path}")
    if not timings_path.exists():
        die(f"missing timings: {timings_path} (run generate-audio first)")

    script = json.loads(script_path.read_text(encoding="utf-8"))
    timings = json.loads(timings_path.read_text(encoding="utf-8"))
    scenes = script.get("scenes")
    t_scenes = timings.get("scenes")

    if not isinstance(scenes, list) or len(scenes) == 0:
        die("script.json has no scenes")
    if len(scenes) != len(t_scenes):
        die(f"scene count mismatch: script={len(scenes)} timings={len(t_scenes)}")
    if timings.get("total", 0) <= 0:
        die("timings.total must be > 0")

    TOTAL = round(timings["total"] + 0.5, 3)  # 0.5s tail

    scene_els: list[str] = []
    cap_els: list[str] = []
    audio_els: list[str] = []
    timeline_blocks: list[str] = []

    for i, scene in enumerate(scenes):
        t = t_scenes[i]
        idx = f"{i + 1:02d}"
        start = t["start"]
        dur = t["duration"]
        track = i + 1
        sel = f'[data-scene="{idx}"]'
        cap_sel = f'[data-caption="{idx}"]'

        bullets = "\n".join(
            f'          <li class="scene-bullet"><span class="bullet-dot"></span>{esc(b)}</li>'
            for b in (scene.get("points") or [])
        )
        code_block = (
            f'          <pre class="scene-code"><code>{esc(scene["code"])}</code></pre>'
            if scene.get("code")
            else ""
        )

        scene_els.append(f"""      <div class="scene clip" data-scene="{idx}" data-start="{start}" data-duration="{dur}" data-track-index="{track}">
        <div class="scene-bg-mesh"></div>
        <div class="scene-eyebrow">{esc_attr(scene.get("id", ""))} · {esc_attr(scene.get("keyword", ""))}</div>
        <h1 class="scene-title">{esc(scene.get("title", ""))}</h1>
        <ul class="scene-bullets">
{bullets}
        </ul>
{code_block}
      </div>""")

        cap_els.append(
            f'      <div class="cap clip" data-caption="{idx}" data-start="{start}" data-duration="{dur}" data-track-index="{track + 20}">{esc(scene.get("narration", ""))}</div>'
        )

        audio_els.append(
            f'      <audio class="clip" src="audio/scene-{idx}.wav" data-start="{start}" data-duration="{dur}" data-track-index="{track + 40}" data-volume="1"></audio>'
        )

        s = start
        timeline_blocks.append(f"""    // ── scene {idx} ({t.get("id", "")}) @ {s}s – {(s + dur):.1f}s ──
    {{
      const sc = document.querySelector('{sel}');
      tl.set(sc, {{ autoAlpha: 1 }});
      tl.fromTo(sc.querySelector(".scene-eyebrow"),
        {{ y: -12, autoAlpha: 0 }}, {{ y: 0, autoAlpha: 1, duration: 0.4, ease: "power2.out" }}, {s} + 0.1);
      tl.fromTo(sc.querySelector(".scene-title"),
        {{ y: 24, autoAlpha: 0 }}, {{ y: 0, autoAlpha: 1, duration: 0.5, ease: "power3.out" }}, {s} + 0.25);
      tl.fromTo(sc.querySelectorAll(".scene-bullet"),
        {{ y: 20, autoAlpha: 0 }}, {{ y: 0, autoAlpha: 1, duration: 0.4, ease: "power3.out", stagger: 0.12 }}, {s} + 0.5);
      const code = sc.querySelector(".scene-code");
      if (code) tl.fromTo(code,
        {{ y: 16, autoAlpha: 0 }}, {{ y: 0, autoAlpha: 1, duration: 0.5, ease: "power2.out" }}, {s} + 0.9);
      const cap = document.querySelector('{cap_sel}');
      tl.fromTo(cap,
        {{ y: 8, autoAlpha: 0 }}, {{ y: 0, autoAlpha: 1, duration: 0.3, ease: "power3.out" }}, {s} + 0.15);
    }}""")

    lang = esc_attr(script.get("meta", {}).get("lang", "zh"))
    title = esc_attr(script.get("meta", {}).get("title", "LongCipher Explain"))

    html = f"""<!doctype html>
<html lang="{lang}">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{title}</title>
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>{STYLE}    </style>
  </head>
  <body>
    <div
      id="master-root"
      data-composition-id="master"
      data-width="1920"
      data-height="1080"
      data-start="0"
      data-duration="{TOTAL}"
    >
{chr(10).join(scene_els)}
    </div>

    <!-- captions: body-level siblings -->
{chr(10).join(cap_els)}

    <!-- audio: body-level siblings -->
{chr(10).join(audio_els)}

    <script>
      window.__timelines = window.__timelines || {{}};
      var tl = gsap.timeline({{ paused: true }});

{chr(10).join(timeline_blocks)}

      // final fade-out tail
      tl.to("#master-root", {{ autoAlpha: 0, duration: 0.5, ease: "power2.inOut" }}, {TOTAL} - 0.5);

      window.__timelines["master"] = tl;
    </script>
  </body>
</html>
"""

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "index.html").write_text(html, encoding="utf-8")
    (out_dir / "hyperframes.json").write_text(HYPERFRAMES_JSON, encoding="utf-8")

    sys.stdout.write(
        f"✓ composition written: {out_dir / 'index.html'} ({len(scenes)} scenes, {TOTAL}s)\n"
        f"  Next: cd dist/video && npx --yes hyperframes lint && npx --yes hyperframes check\n"
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
