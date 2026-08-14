#!/usr/bin/env python3
"""render_cover.py — render a cover composition and extract a PNG.

Usage (single ratio):
  uv run python scripts/render_cover.py --project dist/cover \
      --name cover_16x9 --output output/cover_16x9.png

The cover is a 1s HyperFrames composition; this script renders it to a
temp MP4 (standard quality) and grabs a frame with ffmpeg. The `--name`
selects which ratio file (e.g. `cover_16x9.html`) under `--project`.

To render all four ratios, loop in the shell:
  for r in 16x9 9x16 4x3 3x4; do
    uv run python scripts/render_cover.py --project dist/cover \
      --name "cover_$r" --output "output/cover_$r.png"
  done
"""

from __future__ import annotations

import argparse
import json
import shutil
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


def render_one(project: Path, src_name: str, output: Path, width: str, height: str) -> None:
    """Render a single cover ratio to a PNG (downscaled to width×height)."""
    src = project / src_name
    if not src.exists():
        die(f"missing {src} (run build-cover first)")

    if not (project / "hyperframes.json").exists():
        die(f"missing {project / 'hyperframes.json'} (run build-cover first)")

    index_backup = None
    created_tmp_index = False
    if src.name != "index.html":
        index_path = project / "index.html"
        if index_path.exists() and not index_path.samefile(src):
            index_backup = project / "_index_backup.html"
            shutil.move(index_path, index_backup)
        shutil.copyfile(src, index_path)
        created_tmp_index = True

    output.parent.mkdir(parents=True, exist_ok=True)

    def cleanup() -> None:
        if created_tmp_index:
            (project / "index.html").unlink(missing_ok=True)
        if index_backup is not None and index_backup.exists():
            shutil.move(index_backup, project / "index.html")

    tmp_mp4 = project / f"_cover_{src.stem}.mp4"
    sys.stdout.write(f"· rendering {src_name} (standard)…\n")
    render = run(
        [
            "npx",
            "--yes",
            "hyperframes",
            "render",
            "--output",
            str(tmp_mp4),
            "--quality",
            "standard",
        ],
        cwd=project,
    )
    if render.returncode != 0:
        cleanup()
        die("hyperframes render failed (see output above)")
    if not tmp_mp4.exists():
        cleanup()
        die(f"render produced no file: {tmp_mp4}")

    sys.stdout.write(f"· extracting frame at 2.5s → {output}\n")
    grab = run(
        [
            "ffmpeg",
            "-y",
            "-ss",
            "2.5",
            "-i",
            str(tmp_mp4),
            "-frames:v",
            "1",
            "-vf",
            f"scale={width}:{height}",
            str(output),
        ]
    )
    tmp_mp4.unlink(missing_ok=True)
    if grab.returncode != 0:
        cleanup()
        die("ffmpeg frame extraction failed")
    if not output.exists():
        cleanup()
        die(f"no PNG produced: {output}")
    cleanup()
    sys.stdout.write(f"✓ cover image: {output} ({width}×{height})\n")


def main() -> None:
    p = argparse.ArgumentParser(description="Render branded cover PNG(s)")
    p.add_argument("--project", default="dist/cover")
    p.add_argument(
        "--name", default="cover_16x9", help="cover file basename (no .html), e.g. cover_16x9"
    )
    p.add_argument("--output", default="output/cover_16x9.png")
    p.add_argument("--width", default="1920")
    p.add_argument("--height", default="1080")
    p.add_argument(
        "--all", action="store_true",
        help="render all four ratios from manifest.json (16x9/9x16/4x3/3x4)",
    )
    args = p.parse_args()

    project = Path(args.project).resolve()

    if args.all:
        manifest_path = project / "manifest.json"
        if not manifest_path.exists():
            die(f"missing {manifest_path} (run build-cover first)")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        out_root = Path(args.output).resolve().parent
        for name, info in manifest.get("ratios", {}).items():
            w, h = info["width"], info["height"]
            out_file = out_root / f"cover_{name}.png"
            render_one(project, info["html"], out_file, str(w), str(h))
        sys.exit(0)

    render_one(
        project,
        args.name if args.name.endswith(".html") else f"{args.name}.html",
        Path(args.output).resolve(),
        str(args.width),
        str(args.height),
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
