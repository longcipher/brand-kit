#!/usr/bin/env python3
"""edge_tts.py — thin TTS backend wrapping Microsoft Edge Neural TTS.

This is one of the Python files in the LongCipher publisher skill. The TS
pipeline calls it once per scene via subprocess (same pattern as calling
ffmpeg or hyperframes). Edge TTS is a pure-Python package (pip install
edge-tts) that streams from Microsoft's free online neural voices — **no
reference voice, no model download, no API key** — but it does require an
internet connection at synth time.

Usage:
  python3 scripts/edge_tts.py \
      --text "你好，世界" \
      --out scene-01.wav \
      --voice zh-CN-YunxiNeural --rate "-2%" --volume "+0%"

Environment:
  TTS_PY   interpreter with edge_tts installed (default: sys.executable)

Notes:
  - Output is saved as WAV (16-bit PCM) via ffmpeg, so the TS pipeline can
    measure duration uniformly with ffprobe regardless of the backend.
  - Voices: zh-CN-YunxiNeural (male, default), zh-CN-XiaoxiaoNeural (female), etc.
"""

import argparse
import asyncio
import json
import os
import subprocess
import sys
import tempfile

DEFAULT_VOICE = "zh-CN-YunxiNeural"


def die(msg):
    sys.stderr.write(f"✗ edge_tts: {msg}\n")
    sys.exit(1)


async def _synth(text, out_path, voice, rate, volume):
    # The script is itself named edge_tts.py, so `import edge_tts` would resolve
    # to THIS file. Strip the script's own dir (and the cwd, which equals it when
    # run as `python3 scripts/edge_tts.py`) from sys.path before importing the
    # real PyPI package.
    import os  # noqa: E402
    import sys  # noqa: E402
    import time  # noqa: E402

    _self_dir = os.path.dirname(os.path.abspath(__file__))
    # Remove the script's own directory (and cwd alias) so `import edge_tts`
    # resolves to the real PyPI package, not this file. Also drop any stale
    # cached module entry that may already point at this script.
    sys.path = [p for p in sys.path if p != "" and os.path.abspath(p) != _self_dir]
    sys.modules.pop("edge_tts", None)
    import edge_tts  # noqa: E402

    # Edge TTS occasionally drops a stream mid-request (NoAudioReceived),
    # especially on longer segments. Retry with linear backoff so the
    # publisher pipeline is resilient to transient network blips.
    max_attempts = 6
    last_err = None
    for attempt in range(1, max_attempts + 1):
        try:
            with tempfile.TemporaryDirectory() as td:
                mp3 = os.path.join(td, "clip.mp3")
                communicate = edge_tts.Communicate(text, voice, rate=rate, volume=volume)
                await communicate.save(mp3)
                # transcode to WAV (16-bit PCM) so ffprobe duration is uniform
                res = subprocess.run(
                    ["ffmpeg", "-y", "-i", mp3, "-acodec", "pcm_s16le", out_path],
                    capture_output=True,
                    text=True,
                )
                if res.returncode != 0:
                    die(f"ffmpeg transcode failed: {res.stderr.strip()[-500:]}")
            print(f"✓ {out_path} (voice={voice})", file=sys.stderr)
            return out_path
        except Exception as e:  # transient stream error
            last_err = e
            if attempt < max_attempts:
                sys.stderr.write(f"· edge-tts retry {attempt}/{max_attempts}: {e}\n")
                time.sleep(2.0 * attempt)
    die(f"edge_tts failed after {max_attempts} attempts: {last_err}")


def synth_one(text, out_path, voice, rate, volume):
    try:
        import edge_tts  # noqa: F401
    except Exception as e:  # pragma: no cover
        die(f"edge_tts not installed (pip install edge-tts): {e}")
    return asyncio.run(_synth(text, out_path, voice, rate, volume))


def main():
    p = argparse.ArgumentParser(description="Edge Neural TTS shim for lc-tech-publisher")
    p.add_argument("--text", required=True, help="text to synthesize, or a .txt file path")
    p.add_argument("--out", required=True, help="output WAV path")
    p.add_argument(
        "--voice",
        default=os.environ.get("EDGE_TTS_VOICE", DEFAULT_VOICE),
        help="Edge voice id (e.g. zh-CN-yunxi)",
    )
    p.add_argument(
        "--rate",
        default=os.environ.get("EDGE_TTS_RATE", "-2%"),
        help="speech rate, e.g. '-2%%' (slower) or '+5%%'",
    )
    p.add_argument(
        "--volume", default=os.environ.get("EDGE_TTS_VOLUME", "+0%"), help="volume, e.g. '+0%%'"
    )
    p.add_argument("--json", action="store_true", help="emit a json result instead of plain")
    args = p.parse_args()

    # allow --text to be a file path
    if os.path.isfile(args.text):
        with open(args.text, encoding="utf-8") as f:
            text = f.read().strip()
    else:
        text = args.text

    if not text:
        die("empty text")

    out = synth_one(text, args.out, args.voice, args.rate, args.volume)

    if args.json:
        sys.stdout.write(json.dumps({"out": out, "voice": args.voice}) + "\n")


if __name__ == "__main__":
    main()
