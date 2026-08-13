#!/usr/bin/env python3
"""check_env.py — verify the toolchain for the LongCipher publisher pipeline.

Checks (in order): Node >= 22, ffmpeg, ffprobe, hyperframes CLI, and the
selected TTS backend:
  • edge (DEFAULT)     — python3 + the `edge_tts` package (needs internet)
  • cosyvoice          — CosyVoice Python env + model + brand reference voice

Pass `--tts edge|cosyvoice` to scope the check (default: edge); omit to check
both backends and report each. Exits 0 when mandatory prerequisites are
available, 1 otherwise.

Usage:
  uv run python scripts/check_env.py
  uv run python scripts/check_env.py --tts cosyvoice
  uv run python scripts/check_env.py --json     # machine-readable report
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, encoding="utf-8", capture_output=True, timeout=120)


def has_command(cmd: str) -> bool:
    return run(["sh", "-c", f"command -v {cmd}"]).returncode == 0


def py_has_module(py_bin: str, mod: str) -> bool:
    return run([py_bin, "-c", f"import {mod}"]).returncode == 0


def cosyvoice_home() -> str | None:
    if os.environ.get("COSYVOICE_HOME"):
        return os.environ["COSYVOICE_HOME"]
    candidates = [
        SKILL_ROOT / ".." / ".." / "CosyVoice",
        Path("/Volumes/akext/tmp/CosyVoice"),
        Path.home() / "CosyVoice",
        Path.home() / "code" / "CosyVoice",
    ]
    for c in candidates:
        if (c / "cosyvoice").is_dir():
            return str(c.resolve())
    return None


def main() -> None:
    p = argparse.ArgumentParser(description="Check the LongCipher publisher toolchain")
    p.add_argument("--json", action="store_true", help="machine-readable report")
    p.add_argument("--tts", choices=["edge", "cosyvoice"], default=None)
    args = p.parse_args()

    report: dict = {"checks": {}, "ok": True}

    # 1. Node version
    node_ok = False
    node_detail = "missing"
    node_res = run(["node", "--version"])
    if node_res.returncode == 0:
        try:
            major = int(node_res.stdout.strip().lstrip("v").split(".")[0])
            node_ok = major >= 22
            node_detail = f"{node_res.stdout.strip()} (need >= 22)"
        except ValueError:
            node_detail = "unparseable version"
    report["checks"]["node"] = {"ok": node_ok, "detail": node_detail}

    # 2. ffmpeg / ffprobe
    report["checks"]["ffmpeg"] = {
        "ok": has_command("ffmpeg"),
        "detail": "found" if has_command("ffmpeg") else "missing",
    }
    report["checks"]["ffprobe"] = {
        "ok": has_command("ffprobe"),
        "detail": "found" if has_command("ffprobe") else "missing",
    }

    # 3. hyperframes CLI
    hf = run(["npx", "--yes", "hyperframes", "--version"])
    report["checks"]["hyperframes"] = {
        "ok": hf.returncode == 0,
        "detail": (hf.stdout or hf.stderr).strip()
        if hf.returncode == 0
        else f"npx failed: {hf.stderr or 'unknown'}",
    }

    # 4. TTS backend(s)
    check_edge = args.tts in (None, "edge")
    check_cosy = args.tts in (None, "cosyvoice")

    if check_edge:
        edge_py = os.environ.get("TTS_PY", "python3")
        report["checks"]["edgePython"] = {
            "ok": has_command(edge_py),
            "detail": f"{edge_py} on PATH" if has_command(edge_py) else f"missing ({edge_py})",
        }
        edge_mod = py_has_module(edge_py, "edge_tts")
        report["checks"]["edgeTts"] = {
            "ok": edge_mod,
            "detail": "edge_tts installed"
            if edge_mod
            else "pip install edge-tts (needs internet at synth time)",
        }

    if check_cosy:
        home = cosyvoice_home()
        report["checks"]["cosyvoiceHome"] = {
            "ok": bool(home),
            "detail": home or "not found (set COSYVOICE_HOME)",
        }
        py_bin = os.environ.get("COSYVOICE_PY", "python3")
        report["checks"]["cosyPython"] = {
            "ok": has_command(py_bin),
            "detail": f"{py_bin} on PATH" if has_command(py_bin) else f"missing ({py_bin})",
        }
        model_dir = os.environ.get("COSYVOICE_MODEL") or (
            f"{home}/pretrained_models/Fun-CosyVoice3-0.5B" if home else None
        )
        report["checks"]["cosyModel"] = {
            "ok": bool(model_dir) and os.path.isdir(model_dir),
            "detail": model_dir
            if model_dir and os.path.isdir(model_dir)
            else (model_dir or "no COSYVOICE_MODEL / COSYVOICE_HOME"),
        }
        prompt_wav = os.environ.get("COSYVOICE_PROMPT_WAV")
        if prompt_wav and os.path.isfile(prompt_wav):
            pw_detail = prompt_wav
        elif prompt_wav:
            pw_detail = "missing reference WAV"
        else:
            pw_detail = "no COSYVOICE_PROMPT_WAV (your brand voice)"
        report["checks"]["brandVoice"] = {
            "ok": bool(prompt_wav) and os.path.isfile(prompt_wav),
            "detail": pw_detail,
        }

    report["checks"]["logos"] = {
        "ok": (SKILL_ROOT / "assets" / "logos" / "lc.svg").exists(),
        "detail": "lc.svg",
    }

    report["ok"] = all(c["ok"] for c in report["checks"].values())

    if args.json:
        sys.stdout.write(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    else:
        for name, check in report["checks"].items():
            sys.stdout.write(f"{'✓' if check['ok'] else '✗'} {name}: {check['detail']}\n")
        sys.stdout.write(
            f"\n{'✓ Toolchain ready.' if report['ok'] else '✗ Missing prerequisites (see above).'}\n"
        )

    sys.exit(0 if report["ok"] else 1)


if __name__ == "__main__":
    main()
