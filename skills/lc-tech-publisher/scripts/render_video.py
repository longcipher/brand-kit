#!/usr/bin/env python3
"""render_video.py — render the video composition and optionally mux the
podcast track for the cleanest audio; also a podcast-only mode.

Usage:
  # full explainer video (render + mux podcast audio)
  uv run python scripts/render_video.py --project dist/video \
      --audio dist/podcast_full.wav --output output/explainer_video.mp4

  # podcast MP3 only (no video render)
  uv run python scripts/render_video.py --audio-only \
      --project dist --output output/podcast_full.mp3
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def die(msg: str) -> None:
    sys.stderr.write(f"✗ {msg}\n")
    sys.exit(1)


def run(cmd: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
    res = subprocess.run(
        cmd, encoding="utf-8", capture_output=True, timeout=900, cwd=str(cwd) if cwd else None
    )
    if res.returncode != 0:
        sys.stderr.write(f"! {' '.join(cmd)} failed:\n{res.stderr or res.stdout}\n")
    return res


def main() -> None:
    p = argparse.ArgumentParser(description="Render the explainer video / podcast")
    p.add_argument("--project", default="dist/video")
    p.add_argument("--audio")
    p.add_argument("--output", default="output/explainer_video.mp4")
    p.add_argument("--audio-only", action="store_true")
    p.add_argument("--quality", default="standard")
    args = p.parse_args()

    project = Path(args.project).resolve()
    output = Path(args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    # Podcast-only mode
    if args.audio_only:
        src_mp3 = project / "podcast_full.mp3"
        if not src_mp3.exists():
            die(f"missing {src_mp3} (run generate-audio first)")
        shutil.copyfile(src_mp3, output)
        sys.stdout.write(f"✓ podcast: {output}\n")
        sys.exit(0)

    # Full video mode
    if not (project / "index.html").exists():
        die(f"missing {project / 'index.html'} (run build-composition first)")

    tmp_video = project / "_raw_video.mp4"
    sys.stdout.write(f"· rendering video ({args.quality})…\n")
    render = run(
        [
            "npx",
            "--yes",
            "hyperframes",
            "render",
            "--output",
            str(tmp_video),
            "--quality",
            args.quality,
        ],
        cwd=project,
    )
    if render.returncode != 0:
        die("hyperframes render failed (see output above)")
    if not tmp_video.exists():
        die(f"render produced no file: {tmp_video}")

    audio_path = Path(args.audio) if args.audio else None
    if audio_path and audio_path.exists():
        sys.stdout.write(f"· muxing audio {audio_path}\n")
        mux = run(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(tmp_video),
                "-i",
                str(audio_path),
                "-c:v",
                "copy",
                "-c:a",
                "aac",
                "-shortest",
                str(output),
            ]
        )
        if mux.returncode != 0:
            die("ffmpeg mux failed (fall back to raw video)")
    else:
        sys.stdout.write("· no --audio given; keeping baked-in per-scene audio\n")
        shutil.copyfile(tmp_video, output)

    if not output.exists():
        die(f"no MP4 produced: {output}")
    sys.stdout.write(f"✓ video: {output}\n")
    sys.exit(0)


if __name__ == "__main__":
    main()
