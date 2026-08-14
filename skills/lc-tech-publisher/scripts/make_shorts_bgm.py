#!/usr/bin/env python3
"""make_shorts_bgm.py — synthesize a light, upbeat electronic loop for the
vertical shorts (assets/audio/shorts_bgm.mp3).

Pure-python (no numpy) sample generator -> 16-bit WAV -> ffmpeg -> mp3.
The track is ~10s, loopable (phase-aligned), bright major-key, four-on-the-floor
kick + offbeat hats + bouncy bass + plucky pentatonic arpeggio + warm pad.

Usage:
  uv run python scripts/make_shorts_bgm.py --out assets/audio/shorts_bgm.mp3
"""

from __future__ import annotations

import argparse
import math
import struct
import subprocess
import sys
from pathlib import Path

SR = 44100
DEFAULT_DUR = 60.0
LOOP_DUR = 10.0
BPM = 120.0
BEAT = 60.0 / BPM          # 0.5s
BARS = 5                   # 5 bars of 2s each == 10s, loopable progression
BAR = 4 * BEAT             # 2.0s

# C major-ish, uplifting progression: C  G  Am  F  C  (last bar returns to C)
# Each entry: (bass_root, [chord tones for pad], [arp pool])
PROG = [
    (130.81, [261.63, 329.63, 392.00], [261.63, 329.63, 392.00, 523.25]),  # C
    (196.00, [392.00, 493.88, 587.33], [392.00, 493.88, 587.33, 783.99]),  # G
    (220.00, [440.00, 523.25, 659.25], [440.00, 523.25, 659.25, 880.00]),  # Am
    (174.61, [349.23, 440.00, 523.25], [349.23, 440.00, 523.25, 698.46]),  # F
    (130.81, [261.63, 329.63, 392.00], [261.63, 329.63, 392.00, 523.25]),  # C
]


def env(phase: float, a: float, d: float, s: float, r: float, sus: float = 0.7) -> float:
    """Simple ADSR-ish gain given a 0..1 progress within a note."""
    if phase < a:
        return phase / max(a, 1e-6)
    if phase < a + d:
        return 1.0 - (1.0 - sus) * ((phase - a) / max(d, 1e-6))
    return sus


def kick(t: float) -> float:
    """Punchy four-on-the-floor kick: pitch-dropping sine with fast decay."""
    if t < 0 or t > 0.16:
        return 0.0
    p = t / 0.16
    freq = 55.0 * (1.0 - 0.6 * p) + 28.0 * p
    decay = math.exp(-22.0 * t)
    return 0.9 * math.sin(2 * math.pi * freq * t) * decay


def hat(t: float) -> float:
    """Short bright noise burst (hi-hat) with fast decay."""
    if t < 0 or t > 0.05:
        return 0.0
    decay = math.exp(-90.0 * t)
    # deterministic pseudo-noise
    n = math.sin(2 * math.pi * 7123.0 * t) * math.sin(2 * math.pi * 511.0 * t)
    n = (n - int(n)) if False else (math.sin(2 * math.pi * 1307 * t) * 0.5
                                    + math.sin(2 * math.pi * 2701 * t) * 0.3
                                    + math.sin(2 * math.pi * 5503 * t) * 0.2)
    return 0.25 * n * decay


def osc(freq: float, t: float, kind: str = "sine") -> float:
    ph = 2 * math.pi * freq * t
    if kind == "sine":
        return math.sin(ph)
    if kind == "tri":
        return 2.0 * abs(2.0 * (t * freq - math.floor(t * freq + 0.5))) - 1.0
    if kind == "sq":
        return 1.0 if math.sin(ph) >= 0 else -1.0
    return math.sin(ph)


def tone(freq: float, t0: float, t: float, dur: float, kind: str, peak: float) -> float:
    """A plucked/sustained tone relative to its own start time t0."""
    local = t - t0
    if local < 0 or local > dur:
        return 0.0
    p = local / dur
    # plucky attack, smooth exponential decay
    a = 0.008
    if p < a:
        g = p / a
    else:
        g = math.exp(-3.2 * (local - a))
    # subtle detune shimmer
    detune = 1.0 + 0.0025 * math.sin(2 * math.pi * 5.5 * local)
    return peak * g * osc(freq * detune, local, kind)


def main() -> None:
    p = argparse.ArgumentParser(description="Synth a light electronic BGM loop")
    p.add_argument("--out", default="assets/audio/shorts_bgm.mp3")
    p.add_argument("--wav", default=None, help="intermediate wav path")
    p.add_argument("--duration", type=float, default=DEFAULT_DUR,
                   help=f"BGM duration in seconds (default {DEFAULT_DUR}, max 60)")
    args = p.parse_args()

    DUR = max(2.0, min(60.0, args.duration))
    N = int(SR * DUR)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    wav_path = Path(args.wav) if args.wav else (out_path.parent / "_bgm_tmp.wav")

    samples = [0.0] * N

    for i in range(N):
        t = i / SR
        # Loop the 5-bar progression so any video length reuses the same motifs.
        bar_idx = int(t // BAR) % BARS
        bar_t = t - (int(t // BAR)) * BAR
        bass_f, pad, arp_pool = PROG[bar_idx]

        # --- bass: root on beats 1 and 3 (0 and 1.0s within bar) ---
        for boff in (0.0, 1.0):
            local = bar_t - boff
            if 0 <= local < 0.92:
                # triangle bass with mild decay
                p2 = local / 0.92
                g = math.exp(-2.2 * p2)
                samples[i] += 0.32 * g * osc(bass_f, local, "tri")
                # octave shimmer
                samples[i] += 0.10 * g * osc(bass_f * 2, local, "tri")

        # --- pad: sustained chord triad for the whole bar ---
        pad_g = 0.10
        for cf in pad:
            samples[i] += pad_g * osc(cf, t, "sine")

        # --- arpeggio: 8th notes (0.25s) plucky triangle, pentatonic ---
        step = BEAT / 2.0  # 0.25s
        k = int(bar_t // step)
        note_t0 = bar_idx * BAR + k * step
        note_freq = arp_pool[k % len(arp_pool)]
        samples[i] += tone(note_freq, note_t0, t, step * 0.96, "tri", 0.22)

        # --- drums ---
        beat_in_bar = bar_t % BEAT
        if beat_in_bar < 0.16:
            samples[i] += kick(beat_in_bar)
        # hats on every 8th offbeat
        off = (bar_t + step) % step  # position within the offbeat grid
        hat_local = bar_t - (math.floor(bar_t / step) + 0.5) * step
        if -0.001 < hat_local < 0.05:
            samples[i] += hat(hat_local if hat_local >= 0 else hat_local + step)

    # global gentle fade in/out and soft limiter (tanh) for glue
    for i in range(N):
        t = i / SR
        fade = min(1.0, t / 0.25, (DUR - t) / 0.35)
        fade = max(0.0, fade)
        s = samples[i] * fade
        samples[i] = math.tanh(s * 1.35) * 0.82

    # interleave to 16-bit stereo
    frames = bytearray()
    for i in range(N):
        v = int(max(-1.0, min(1.0, samples[i])) * 32767)
        frames += struct.pack("<hh", v, v)

    with open(wav_path, "wb") as f:
        f.write(b"RIFF")
        f.write(struct.pack("<I", 36 + len(frames)))
        f.write(b"WAVE")
        f.write(b"fmt ")
        f.write(struct.pack("<IHHIIHH", 16, 1, 2, SR, SR * 4, 4, 16))
        f.write(b"data")
        f.write(struct.pack("<I", len(frames)))
        f.write(frames)

    # encode to mp3
    res = subprocess.run(
        ["ffmpeg", "-y", "-i", str(wav_path), "-codec:a", "libmp3lame",
         "-qscale:a", "2", "-ar", "44100", str(out_path)],
        capture_output=True, text=True,
    )
    try:
        wav_path.unlink(missing_ok=True)
    except BaseException:
        pass
    if res.returncode != 0:
        sys.stderr.write(f"! ffmpeg failed: {res.stderr}\n")
        sys.exit(1)
    sys.stdout.write(f"✓ BGM written: {out_path} ({DUR}s, loopable C-G-Am-F-C)\n")


if __name__ == "__main__":
    main()
