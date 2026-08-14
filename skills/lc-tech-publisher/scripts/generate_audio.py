#!/usr/bin/env python3
"""generate_audio.py — synthesize the two-speaker dialogue, measure per-turn
durations, and assemble the merged podcast track.

The script's `podcast[]` is a list of dialogue turns, each tagged
`speaker: "male" | "female"`. Voices are resolved per speaker:
  • male   → meta.roles.maleVoice   (default zh-CN-YunxiNeural, 老高式自信讲解)
  • female → meta.roles.femaleVoice (default zh-CN-XiaoxiaoNeural, 小茉式好奇提问)

Two TTS backends via --tts:
  • edge (DEFAULT)  — Microsoft Edge Neural TTS via scripts/edge_tts.py.
                       No reference voice, no model download, no API key;
                       needs `pip install edge-tts` + internet.
  • cosyvoice       — local Fun-CosyVoice3-0.5B zero-shot voice cloning via
                       scripts/cosyvoice_tts.py. Needs your brand reference
                       voice (--prompt-wav) and the CosyVoice env.

Pipeline:
  1. Per turn: pick voice by speaker, call shim -> dist/audio/turn-NN.wav
  2. Measure each WAV with ffprobe -> dist/speaker_timestamps.json
  3. Concatenate turn WAVs -> dist/podcast_full.wav + .mp3
  4. Copy turn WAVs -> dist/video/audio/turn-NN.wav for the composition

Usage:
  # Edge (default, no reference voice needed)
  uv run python scripts/generate_audio.py --script dist/script.json --out dist

  # CosyVoice (single cloned voice for both speakers)
  uv run python scripts/generate_audio.py --script dist/script.json --tts cosyvoice \
      --prompt-wav /path/to/brand-voice.wav --prompt-text "…" \
      --speed 1.0 --lang zh --out dist

Produces:
  dist/audio/turn-NN.wav              per-turn narration (by speaker voice)
  dist/speaker_timestamps.json        { total, engine, turns:[{id,speaker,voice,start,end,duration,file}] }
  dist/podcast_full.wav               concatenated dialogue (podcast source)
  dist/podcast_full.mp3               podcast-ready MP3
  dist/video/audio/turn-NN.wav        copies for the composition
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

# Default two-speaker voices (can be overridden per-project in meta.roles).
MALE_VOICE = "zh-CN-YunxiNeural"
FEMALE_VOICE = "zh-CN-XiaoxiaoNeural"
FEMALE_VOICE_ALT = "zh-CN-XiaoyiNeural"
# English single-voice (user-specified for the EN video).
EN_VOICE = "en-US-AndrewNeural"

SKILL_ROOT = Path(__file__).resolve().parent.parent
EDGE_SHIM = SKILL_ROOT / "scripts" / "edge_tts.py"
COSY_SHIM = SKILL_ROOT / "scripts" / "cosyvoice_tts.py"
DEFAULT_PROMPT_TEXT = "希望你以后能够做的比我还好呦。"


def die(msg: str) -> None:
    sys.stderr.write(f"✗ {msg}\n")
    sys.exit(1)


def warn(msg: str) -> None:
    sys.stderr.write(f"! {msg}\n")


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
    p = argparse.ArgumentParser(description="Synthesize two-speaker dialogue + podcast")
    p.add_argument("--script", default="dist/script.json")
    p.add_argument("--tts", default="edge", choices=["edge", "cosyvoice"])
    p.add_argument("--prompt-wav", default=os.environ.get("COSYVOICE_PROMPT_WAV", ""))
    p.add_argument(
        "--prompt-text", default=os.environ.get("COSYVOICE_PROMPT_TEXT", DEFAULT_PROMPT_TEXT)
    )
    p.add_argument("--speed", default="1.0")
    p.add_argument("--lang", default="zh", choices=["zh", "en"])
    p.add_argument("--male-voice", default=os.environ.get("EDGE_TTS_MALE", MALE_VOICE))
    p.add_argument("--female-voice", default=os.environ.get("EDGE_TTS_FEMALE", FEMALE_VOICE))
    p.add_argument("--en-voice", default=os.environ.get("EDGE_TTS_EN", EN_VOICE))
    p.add_argument("--rate", default=os.environ.get("EDGE_TTS_RATE", "-2%"))
    p.add_argument("--volume", default=os.environ.get("EDGE_TTS_VOLUME", "+0%"))
    p.add_argument("--out", default="dist")
    args = p.parse_args()

    tts = args.tts
    lang = args.lang
    script_path = Path(args.script)
    out_dir = Path(args.out).resolve()

    if not script_path.exists():
        die(f"missing script: {script_path} (run parse-article first)")
    script = json.loads(script_path.read_text(encoding="utf-8"))

    # Pick the dialogue turns for the requested language. English falls back to
    # the primary zh dialogue (with a warning) if podcastEn[] is not authored.
    if lang == "en":
        turns = script.get("podcastEn")
        if not isinstance(turns, list) or not turns:
            warn("podcastEn[] missing — falling back to podcast[] for the EN audio")
            turns = script.get("podcast")
    else:
        turns = script.get("podcast")
    if not isinstance(turns, list) or not turns:
        die("script.json has no podcast[] dialogue turns (see --validate / SKILL.md)")

    meta = script.get("meta", {}) or {}
    en_voice = meta.get("enVoice") or args.en_voice

    # Per-speaker voice resolution. CosyVoice clones a single reference voice.
    roles = meta.get("roles", {}) or {}
    if tts == "edge":
        if lang == "en":
            # EN video uses one specified voice for both speakers.
            voice_for = {"male": en_voice, "female": en_voice}
        else:
            voice_for = {
                "male": roles.get("maleVoice") or args.male_voice,
                "female": roles.get("femaleVoice") or args.female_voice,
            }
    else:
        # cosyvoice: one cloned voice for everyone
        voice_for = {"male": None, "female": None}

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

    # Language-specific output subdirs so the zh + en passes don't collide.
    sub = "_en" if lang == "en" else ""
    audio_dir = out_dir / f"audio{sub}"
    # The composition for this language lives at dist/video{lang} and references
    # audio clips relative to its own dir (audio/turn-NN.wav), so copy there.
    video_audio_dir = out_dir / f"video_{lang}" / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    video_audio_dir.mkdir(parents=True, exist_ok=True)

    timing: list[dict] = []
    cursor = 0.0

    for i, turn in enumerate(turns):
        text = (turn.get("text") or "").strip()
        speaker = turn.get("speaker", "male")
        if not text:
            die(f"turn {turn.get('id', i + 1)} has empty text")
        idx = f"{i + 1:02d}"
        wav_path = audio_dir / f"turn-{idx}.wav"
        txt_path = audio_dir / f"turn-{idx}.txt"
        txt_path.write_text(text, encoding="utf-8")

        # explicit per-turn voice wins, else resolve by speaker
        voice = turn.get("voice") or voice_for.get(speaker) or args.male_voice

        if tts == "edge":
            sys.stdout.write(
                f"· edge-tts [{idx}] speaker={speaker} voice={voice} rate={args.rate} … {text[:40]}…\n"
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
                    voice,
                    "--rate",
                    args.rate,
                    "--volume",
                    args.volume,
                ]
            )
            if res.returncode != 0:
                die(f"Edge TTS failed for turn {idx}")
            if not wav_path.exists():
                die(f"Edge TTS produced no output for turn {idx}")
        else:
            sys.stdout.write(
                f"· cosyvoice [{idx}] speaker={speaker} {args.lang} speed={args.speed} … {text[:40]}…\n"
            )
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
                die(f"CosyVoice failed for turn {idx}")
            if not wav_path.exists():
                die(f"CosyVoice produced no output for turn {idx}")

        duration = wav_duration(wav_path)
        rel = f"audio/turn-{idx}.wav"
        timing.append(
            {
                "id": turn.get("id", idx),
                "speaker": speaker,
                "voice": voice,
                "text": text,
                "file": rel,
                "start": round(cursor, 3),
                "end": round(cursor + duration, 3),
                "duration": round(duration, 3),
            }
        )
        cursor += duration

    # Copy into composition dir
    for i in range(len(timing)):
        idx = f"{i + 1:02d}"
        shutil.copyfile(audio_dir / f"turn-{idx}.wav", video_audio_dir / f"turn-{idx}.wav")

    # Assemble podcast track
    list_file = audio_dir / "concat.txt"
    list_file.write_text(
        "\n".join(f"file '{audio_dir / t['file'].replace('audio/', '')}'" for t in timing) + "\n",
        encoding="utf-8",
    )
    concat_wav = out_dir / f"podcast_full{sub}.wav"
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
    concat_mp3 = out_dir / f"podcast_full{sub}.mp3"
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
        "lang": lang,
        "voices": voice_for if tts == "edge" else None,
        "promptText": args.prompt_text if tts == "cosyvoice" else None,
        "speed": args.speed if tts == "cosyvoice" else None,
        "turns": timing,
    }
    ts_name = f"speaker_timestamps{sub}.json" if sub else "speaker_timestamps.json"
    (out_dir / ts_name).write_text(
        json.dumps(timestamps, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    male_n = sum(1 for t in timing if t["speaker"] == "male")
    sys.stdout.write(
        f"✓ audio generated ({engine_label}, lang={lang}): {len(timing)} turns "
        f"({male_n} male / {len(timing) - male_n} female), total {timestamps['total']}s\n"
        f"  dist/audio{sub}/turn-*.wav\n  dist/video/audio{sub}/turn-*.wav\n"
        f"  dist/podcast_full{sub}.wav + .mp3\n  dist/{ts_name}\n"
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
