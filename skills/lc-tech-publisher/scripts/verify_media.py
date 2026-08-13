#!/usr/bin/env python3
"""verify_media.py — inspect a rendered MP4 or MP3 with ffprobe and confirm
the expected streams / duration.

Usage:
  uv run python scripts/verify_media.py output/explainer_video.mp4
  uv run python scripts/verify_media.py output/podcast_full.mp3 [--expected 62.4]

MP4: requires one h264 video stream + one audio stream.
MP3: requires a non-empty audio stream with a finite duration.
Exits 0 on success, 1 on failure.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def die(msg: str) -> None:
    sys.stderr.write(f"✗ {msg}\n")
    sys.exit(1)


def main() -> None:
    p = argparse.ArgumentParser(description="Verify rendered media with ffprobe")
    p.add_argument("target", help="media file to verify")
    p.add_argument("--expected", type=float, default=None, help="expected duration in seconds")
    args = p.parse_args()

    target = Path(args.target)
    if not target.exists():
        die(f"file not found: {target}")

    probe = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration:stream=index,codec_type,codec_name",
            "-of",
            "json",
            str(target),
        ],
        encoding="utf-8",
        capture_output=True,
    )
    if probe.returncode != 0:
        die(f"ffprobe failed: {probe.stderr}")

    try:
        info = json.loads(probe.stdout)
    except json.JSONDecodeError:
        die("ffprobe returned unparseable output")

    duration = info.get("format", {}).get("duration")
    try:
        duration = float(duration)
    except (TypeError, ValueError):
        duration = float("nan")
    streams = info.get("streams", [])
    report = {
        "file": str(target),
        "duration": duration,
        "streams": [s.get("codec_type") for s in streams],
    }

    if target.name.lower().endswith(".mp3"):
        audio = [s for s in streams if s.get("codec_type") == "audio"]
        if not audio:
            die(f"no audio stream in {target}")
        if not duration > 0:
            die(f"bad duration in {target}")
        sys.stdout.write(f"✓ {target}: mp3 audio {duration:.2f}s\n")
        sys.exit(0)

    video = [s for s in streams if s.get("codec_type") == "video"]
    audio = [s for s in streams if s.get("codec_type") == "audio"]
    errors: list[str] = []
    if not video:
        errors.append("no video stream")
    if video and video[0].get("codec_name") != "h264":
        errors.append(f"video codec is {video[0].get('codec_name')}, expected h264")
    if not audio:
        errors.append("no audio stream")
    if not duration > 0:
        errors.append("bad duration")
    if (
        args.expected
        and duration == duration
        and abs(duration - args.expected) > args.expected * 0.05
    ):
        errors.append(f"duration {duration:.1f}s differs from expected {args.expected}s by >5%")

    if errors:
        die(
            f"verification failed for {target}:\n"
            + "\n".join(f"  - {e}" for e in errors)
            + "\n"
            + json.dumps(report, ensure_ascii=False, indent=2)
        )

    sys.stdout.write(f"✓ {target}: h264 video + {len(audio)} audio stream, {duration:.2f}s\n")
    sys.exit(0)


if __name__ == "__main__":
    main()
