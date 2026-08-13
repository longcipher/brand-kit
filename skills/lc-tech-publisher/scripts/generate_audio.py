#!/usr/bin/env python3
"""generate_audio.py — synthesize per-scene narration, measure durations, and
assemble the podcast track.

Two TTS backends are supported via --tts:
  • edge (DEFAULT)  — Microsoft Edge Neural TTS via scripts/edge_tts.py.
                       No reference voice, no model download, no API key;
                       needs `pip install edge-tts` + internet. Default voice
                       zh-CN-yunxi.
  • cosyvoice       — local Fun-CosyVoice3-0.5B zero-shot voice cloning via
                       scripts/cosyvoice_tts.py. Needs your brand reference
                       voice (--prompt-wav) and the CosyVoice env.

Pipeline (per backend):
  1. Per scene: call the Python shim -> dist/audio/scene-NN.wav
  2. Measure each WAV with ffprobe -> timestamps.json (scene timings)
  3. Concatenate scene WAVs -> dist/podcast_full.wav + .mp3

Usage:
  # Edge (default, no reference voice needed)
  uv run python scripts/generate_audio.py --script dist/script.json --out dist

  # CosyVoice (brand voice clone)
  uv run python scripts/generate_audio.py --script dist/script.json --tts cosyvoice \
      --prompt-wav /path/to/brand-voice.wav --prompt-text "…" \
      --speed 1.0 --lang zh --out dist

Produces:
  dist/audio/scene-NN.wav         per-scene narration
  dist/timestamps.json            { total, engine, scenes: [{id,start,end,duration}] }
  dist/podcast_full.wav           concatenated narration (podcast source)
  dist/podcast_full.mp3           podcast-ready MP3
  dist/video/audio/scene-NN.wav   copies for the composition
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
EDGE_SHIM = SKILL_ROOT / "scripts" / "edge_tts.py"
COSY_SHIM = SKILL_ROOT / "scripts" / "cosyvoice_tts.py"
DEFAULT_PROMPT_TEXT = "希望你以后能够做的比我还好呦。"
DEFAULT_VOICE = "zh-CN-yunxi"


def die(msg: str) -> None:
    sys.stderr.write(f"✗ {msg}\n")
    sys.exit(1)


def run(cmd: list[str], **opts) -> subprocess.CompletedProcess:
    res = subprocess.run(cmd, encoding="utf-8", capture_output=True, timeout=600, **opts)
    if res.returncode != 0:
        sys.stderr.write(f"! {' '.join(cmd)} failed:\n{res.stderr or res.stdout}\n")
    return res


def wav_duration(file: Path) -> float:
    res = run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "csv=p=0",
            str(file),
        ]
    )
    try:
        d = float(res.stdout.strip())
    except ValueError:
        d = float("nan")
    if not d > 0:
        die(f"cannot measure duration of {file}")
    return d


def main() -> None:
    p = argparse.ArgumentParser(description="Synthesize per-scene narration + podcast")
    p.add_argument("--script", default="dist/script.json")
    p.add_argument("--tts", default="edge", choices=["edge", "cosyvoice"])
    p.add_argument("--prompt-wav", default=os.environ.get("COSYVOICE_PROMPT_WAV", ""))
    p.add_argument(
        "--prompt-text", default=os.environ.get("COSYVOICE_PROMPT_TEXT", DEFAULT_PROMPT_TEXT)
    )
    p.add_argument("--speed", default="1.0")
    p.add_argument("--lang", default="zh")
    p.add_argument("--voice", default=os.environ.get("EDGE_TTS_VOICE", DEFAULT_VOICE))
    p.add_argument("--rate", default=os.environ.get("EDGE_TTS_RATE", "-2%"))
    p.add_argument("--volume", default=os.environ.get("EDGE_TTS_VOLUME", "+0%"))
    p.add_argument("--out", default="dist")
    args = p.parse_args()

    tts = args.tts
    script_path = Path(args.script)
    out_dir = Path(args.out).resolve()

    if not script_path.exists():
        die(f"missing script: {script_path} (run parse-article first)")
    script = json.loads(script_path.read_text(encoding="utf-8"))
    scenes = script.get("scenes")
    if not isinstance(scenes, list) or not scenes:
        die("script.json has no scenes")

    python_bin = os.environ.get("COSYVOICE_PY", os.environ.get("TTS_PY", "python3"))

    if tts == "edge":
        engine_label = "edge-tts"
        if not EDGE_SHIM.exists():
            die(f"missing python shim: {EDGE_SHIM}")
    else:
        engine_label = "cosyvoice3"
        if not COSY_SHIM.exists():
            die(f"missing python shim: {COSY_SHIM}")
        if not args.prompt_wav or not Path(args.prompt_wav).exists():
            die(
                "missing brand reference voice. Pass --prompt-wav <wav> (or set COSYVOICE_PROMPT_WAV).\n"
                '  This is your "brand voice" — a short clean recording of the narrator.'
            )

    audio_dir = out_dir / "audio"
    video_audio_dir = out_dir / "video" / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    video_audio_dir.mkdir(parents=True, exist_ok=True)

    timing: list[dict] = []
    cursor = 0.0

    for i, scene in enumerate(scenes):
        text = (scene.get("narration") or "").strip()
        if not text:
            die(f"scene {scene.get('id', i + 1)} has empty narration")
        idx = f"{i + 1:02d}"
        wav_path = audio_dir / f"scene-{idx}.wav"
        txt_path = audio_dir / f"scene-{idx}.txt"
        txt_path.write_text(text, encoding="utf-8")

        if tts == "edge":
            sys.stdout.write(
                f"· edge-tts [{idx}] voice={args.voice} rate={args.rate} … {text[:40]}…\n"
            )
            res = run(
                [
                    python_bin,
                    str(EDGE_SHIM),
                    "--text",
                    str(txt_path),
                    "--out",
                    str(wav_path),
                    "--voice",
                    args.voice,
                    "--rate",
                    args.rate,
                    "--volume",
                    args.volume,
                ]
            )
            if res.returncode != 0:
                die(f"Edge TTS failed for scene {idx}")
            if not wav_path.exists():
                die(f"Edge TTS produced no output for scene {idx}")
        else:
            sys.stdout.write(f"· cosyvoice [{idx}] {args.lang} speed={args.speed} … {text[:40]}…\n")
            res = run(
                [
                    python_bin,
                    str(COSY_SHIM),
                    "--text",
                    str(txt_path),
                    "--out",
                    str(wav_path),
                    "--prompt-wav",
                    args.prompt_wav,
                    "--prompt-text",
                    args.prompt_text,
                    "--speed",
                    args.speed,
                    "--lang",
                    args.lang,
                ],
                env={**os.environ, "COSYVOICE_HOME": os.environ.get("COSYVOICE_HOME", "")},
            )
            if res.returncode != 0:
                die(f"CosyVoice failed for scene {idx}")
            if not wav_path.exists():
                die(f"CosyVoice produced no output for scene {idx}")

        duration = wav_duration(wav_path)
        timing.append(
            {
                "id": scene.get("id", idx),
                "file": f"audio/scene-{idx}.wav",
                "start": round(cursor, 3),
                "end": round(cursor + duration, 3),
                "duration": round(duration, 3),
            }
        )
        cursor += duration

    # Copy into composition dir
    for i in range(len(timing)):
        idx = f"{i + 1:02d}"
        shutil.copyfile(audio_dir / f"scene-{idx}.wav", video_audio_dir / f"scene-{idx}.wav")

    # Assemble podcast track
    list_file = audio_dir / "concat.txt"
    list_file.write_text(
        "\n".join(f"file '{audio_dir / t['file'].replace('audio/', '')}'" for t in timing) + "\n",
        encoding="utf-8",
    )
    concat_wav = out_dir / "podcast_full.wav"
    run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(list_file),
            "-c",
            "copy",
            str(concat_wav),
        ]
    )
    concat_mp3 = out_dir / "podcast_full.mp3"
    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(concat_wav),
            "-codec:a",
            "libmp3lame",
            "-qscale:a",
            "2",
            str(concat_mp3),
        ]
    )

    timestamps = {
        "total": round(cursor, 3),
        "engine": engine_label,
        "voice": args.voice if tts == "edge" else None,
        "promptText": args.prompt_text if tts == "cosyvoice" else None,
        "speed": args.speed if tts == "cosyvoice" else None,
        "lang": args.lang if tts == "cosyvoice" else None,
        "scenes": timing,
    }
    (out_dir / "timestamps.json").write_text(
        json.dumps(timestamps, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    sys.stdout.write(
        f"✓ audio generated ({engine_label}): {len(scenes)} scenes, total {timestamps['total']}s\n"
        f"  dist/audio/scene-*.wav\n  dist/video/audio/scene-*.wav\n  dist/podcast_full.wav + .mp3\n  dist/timestamps.json\n"
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
