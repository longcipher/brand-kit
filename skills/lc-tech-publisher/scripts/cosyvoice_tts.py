#!/usr/bin/env python3
"""cosyvoice_tts.py — thin TTS backend wrapping Fun-CosyVoice3-0.5B.

This is the ONLY Python file in the LongCipher publisher skill. The TS
pipeline calls it once per scene via subprocess (same pattern as calling
ffmpeg or hyperframes). CosyVoice3 itself is a pure-Python PyTorch library,
so a thin Python shim is unavoidable; everything else stays Node.

Usage:
  python3 scripts/cosyvoice_tts.py \
      --text "你好，世界" \
      --out scene-01.wav \
      --prompt-wav asset/zero_shot_prompt.wav \
      --prompt-text "希望你以后能够做的比我还好呦。" \
      --speed 1.0 --lang zh

Environment:
  COSYVOICE_HOME   path to the cloned CosyVoice repo (default: auto-detect
                   a few common locations)
  COSYVOICE_MODEL  path to Fun-CosyVoice3-0.5B (default:
                   $COSYVOICE_HOME/pretrained_models/Fun-CosyVoice3-0.5B)
  COSYVOICE_PY     interpreter with torch + cosyvoice on its path
                   (default: sys.executable)

Notes:
  - CosyVoice3 zero-shot needs a reference voice (prompt_wav + prompt_text).
    This is your "brand voice". Point --prompt-wav / --prompt-text at your
    own recording once, or set COSYVOICE_PROMPT_WAV / COSYVOICE_PROMPT_TEXT.
  - output WAV sample rate is whatever the model reports (24k/25k). The TS
    side re-encodes / measures duration with ffmpeg, so rate mismatch is fine.
"""

import argparse
import json
import os
import sys

DEFAULT_PROMPT_TEXT = "希望你以后能够做的比我还好呦。"


def detect_cosyvoice_home():
    if os.environ.get("COSYVOICE_HOME"):
        return os.environ["COSYVOICE_HOME"]
    here = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(here, "..", "..", "CosyVoice"),
        "/Volumes/akext/tmp/CosyVoice",
        os.path.expanduser("~/CosyVoice"),
        os.path.expanduser("~/code/CosyVoice"),
    ]
    for c in candidates:
        if os.path.isdir(c) and os.path.isdir(os.path.join(c, "cosyvoice")):
            return os.path.abspath(c)
    return None


def load_model(model_dir):
    """Import CosyVoice3 and return a ready AutoModel."""
    home = detect_cosyvoice_home()
    if not home:
        die("Cannot find CosyVoice repo. Set COSYVOICE_HOME.")
    sys.path.insert(0, home)
    sys.path.insert(0, os.path.join(home, "third_party", "Matcha-TTS"))
    try:
        from cosyvoice.cli.cosyvoice import AutoModel  # noqa: E402
    except Exception as e:  # pragma: no cover
        die(f"Failed to import CosyVoice (is torch installed in this env?): {e}")
    if not os.path.isdir(model_dir):
        die(f"Model dir not found: {model_dir}")
    print(f"· loading CosyVoice3 from {model_dir}", file=sys.stderr)
    return AutoModel(model_dir=model_dir)


_MODEL = None
_MODEL_DIR = None


def get_model():
    global _MODEL, _MODEL_DIR
    if _MODEL is None:
        _MODEL_DIR = os.environ.get("COSYVOICE_MODEL") or os.path.join(
            detect_cosyvoice_home(), "pretrained_models", "Fun-CosyVoice3-0.5B"
        )
        _MODEL = load_model(_MODEL_DIR)
    return _MODEL


def die(msg):
    sys.stderr.write(f"✗ cosyvoice_tts: {msg}\n")
    sys.exit(1)


def synth_one(text, out_path, prompt_wav, prompt_text, speed, lang):
    cosyvoice = get_model()
    sr = cosyvoice.sample_rate

    # CosyVoice3 zero-shot: tts_text, prompt_text, prompt_wav, speed.
    # `lang` is informational — CosyVoice3 auto-detects / uses instruct for dialects.
    try:
        import torchaudio  # noqa: E402
    except Exception as e:
        die(f"torchaudio not available: {e}")

    chunks = []
    try:
        for i, item in enumerate(
            cosyvoice.inference_zero_shot(
                text, prompt_text, prompt_wav, stream=False, speed=float(speed)
            )
        ):
            speech = item["tts_speech"]
            chunks.append(speech)
            if i > 0:
                die("CosyVoice returned multiple chunks; unexpected for stream=False")
    except Exception as e:
        die(f"inference failed: {e}")

    if not chunks:
        die("inference produced no audio")

    audio = chunks[0]
    try:
        torchaudio.save(out_path, audio, sr)
    except Exception as e:
        die(f"torchaudio.save failed: {e}")
    print(f"✓ {out_path} ({sr} Hz)", file=sys.stderr)
    return sr


def main():
    p = argparse.ArgumentParser(description="CosyVoice3 TTS shim for lc-tech-publisher")
    p.add_argument("--text", required=True, help="text to synthesize, or a .txt file path")
    p.add_argument("--out", required=True, help="output WAV path")
    p.add_argument(
        "--prompt-wav",
        default=os.environ.get("COSYVOICE_PROMPT_WAV"),
        help="reference voice WAV (brand voice)",
    )
    p.add_argument(
        "--prompt-text",
        default=os.environ.get("COSYVOICE_PROMPT_TEXT", DEFAULT_PROMPT_TEXT),
        help="reference voice transcript",
    )
    p.add_argument("--speed", default="1.0", help="speech speed multiplier")
    p.add_argument("--lang", default="zh", help="language hint (informational)")
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
    if not args.prompt_wav or not os.path.isfile(args.prompt_wav):
        die(
            "missing --prompt-wav (reference voice). Set COSYVOICE_PROMPT_WAV or pass --prompt-wav."
        )

    sr = synth_one(text, args.out, args.prompt_wav, args.prompt_text, args.speed, args.lang)

    if args.json:
        sys.stdout.write(json.dumps({"out": args.out, "sample_rate": sr}) + "\n")


if __name__ == "__main__":
    main()
