#!/usr/bin/env python3
"""render_cover.py — render the cover composition and extract a 1920×1080 PNG.

Usage:
  uv run python scripts/render_cover.py --project dist/cover \
      --output output/cover.png --width 1920 --height 1080

The cover is a 1s HyperFrames composition; this script renders it to a
temp MP4 (draft quality) and grabs frame 1 with ffmpeg.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def die(msg: str) -> None:
    sys.stderr.write(f"✗ {msg}\n")
    sys.exit(1)


def run(cmd: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
    res = subprocess.run(
        cmd, encoding="utf-8", capture_output=True, timeout=600, cwd=str(cwd) if cwd else None
    )
    if res.returncode != 0:
        sys.stderr.write(f"! {' '.join(cmd)} failed:\n{res.stderr or res.stdout}\n")
    return res


def main() -> None:
    p = argparse.ArgumentParser(description="Render the branded cover PNG")
    p.add_argument("--project", default="dist/cover")
    p.add_argument("--output", default="output/cover.png")
    p.add_argument("--width", default="1920")
    p.add_argument("--height", default="1080")
    args = p.parse_args()

    project = Path(args.project).resolve()
    output = Path(args.output).resolve()
    if not (project / "cover.html").exists():
        die(f"missing {project / 'cover.html'} (run build-cover first)")
    output.parent.mkdir(parents=True, exist_ok=True)

    tmp_mp4 = project / "_cover_tmp.mp4"
    sys.stdout.write("· rendering cover (draft)…\n")
    render = run(
        [
            "npx",
            "--yes",
            "hyperframes",
            "render",
            "--output",
            str(tmp_mp4),
            "--quality",
            "draft",
        ],
        cwd=project,
    )
    if render.returncode != 0:
        die("hyperframes render failed (see output above)")
    if not tmp_mp4.exists():
        die(f"render produced no file: {tmp_mp4}")

    sys.stdout.write(f"· extracting frame 1 → {output}\n")
    grab = run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(tmp_mp4),
            "-frames:v",
            "1",
            "-vf",
            f"scale={args.width}:{args.height}",
            str(output),
        ]
    )
    if grab.returncode != 0:
        die("ffmpeg frame extraction failed")

    tmp_mp4.unlink(missing_ok=True)

    if not output.exists():
        die(f"no PNG produced: {output}")
    sys.stdout.write(f"✓ cover image: {output} ({args.width}×{args.height})\n")
    sys.exit(0)


if __name__ == "__main__":
    main()
