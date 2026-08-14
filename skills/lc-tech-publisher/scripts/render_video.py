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
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import subtitle_util as sub


def die(msg: str) -> None:
    sys.stderr.write(f"✗ {msg}\n")
    sys.exit(1)


# Re-export for any external callers; the canonical implementation lives in
# subtitle_util.py so the embedded captions and the .srt sidecar stay identical.
split_subtitles = sub.split_subtitles


def build_srt(timestamps: dict, lang: str) -> str:
    """Build an .srt from speaker_timestamps, one cue per short line."""
    blocks: list[str] = []
    idx = 1
    for turn in timestamps.get("turns", []):
        text = (turn.get("text") or "").strip()
        if not text:
            continue
        cues = split_subtitles(text, lang)
        if not cues:
            continue
        start = float(turn["start"])
        end = float(turn["end"])
        span = max(end - start, 0.001)
        # distribute the turn's time span across cues by relative length
        weights = [len(c) for c in cues]
        total_w = sum(weights) or 1
        cursor = start
        for c, w in zip(cues, weights):
            dur = span * (w / total_w)
            seg_end = cursor + dur
            blocks.append(
                f"{idx}\n"
                f"{_srt_time(cursor)} --> {_srt_time(seg_end)}\n"
                f"{c}\n"
            )
            idx += 1
            cursor = seg_end
    return "\n".join(blocks).rstrip() + "\n"


def _srt_time(t: float) -> str:
    t = max(t, 0.0)
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


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
    p.add_argument("--srt-only", action="store_true")
    p.add_argument("--lang", default="zh", choices=["zh", "en"])
    p.add_argument("--quality", default="standard")
    args = p.parse_args()

    sub = "_en" if args.lang == "en" else ""
    project = Path(args.project).resolve()
    output = Path(args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    # SRT-only mode: regenerate the sidecar subtitles without re-rendering.
    if args.srt_only:
        if not output.exists():
            die(f"missing {output} (render the video/podcast first)")
        srt_path = output.with_suffix(".srt")
        _write_srt(srt_path, project, sub, args.lang)
        sys.exit(0)

    # Podcast-only mode
    if args.audio_only:
        src_mp3 = project / f"podcast_full{sub}.mp3"
        if not src_mp3.exists():
            die(f"missing {src_mp3} (run generate-audio first)")
        shutil.copyfile(src_mp3, output)
        srt_path = output.with_suffix(".srt")
        _write_srt(srt_path, project, sub, args.lang)
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
    srt_path = output.with_suffix(".srt")
    _write_srt(srt_path, project, sub, args.lang)
    sys.stdout.write(f"✓ video: {output}\n")
    sys.exit(0)


def _write_srt(srt_path: Path, project: Path, sub: str, lang: str) -> None:
    """Emit a same-named .srt next to the rendered video/podcast if the
    speaker-timestamp source exists."""
    ts_name = f"speaker_timestamps{sub}.json" if sub else "speaker_timestamps.json"
    ts_path = project / ts_name
    if not ts_path.exists():
        # try the dist root where generate-audio.py actually writes it
        ts_path = project.parent / ts_name
    if not ts_path.exists():
        sys.stderr.write(f"! skip SRT: missing {ts_name}\n")
        return
    try:
        timestamps = json.loads(ts_path.read_text(encoding="utf-8"))
        srt = build_srt(timestamps, lang)
        srt_path.write_text(srt, encoding="utf-8")
        n = len(re.findall(r"^\d+\s*$", srt, re.MULTILINE))
        sys.stdout.write(f"✓ subtitles: {srt_path} ({n} cues)\n")
    except Exception as e:  # never fail the whole render for subtitles
        sys.stderr.write(f"! SRT generation failed: {e}\n")


if __name__ == "__main__":
    main()
