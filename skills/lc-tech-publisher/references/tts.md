# TTS Reference — Edge Neural TTS (Default) & CosyVoice3 (Optional)

Narration is produced by one of two backends, selected with `--tts` on
`scripts/generate_audio.py`:

| Backend | `--tts` | Voice | Needs internet? | Needs reference voice? | Python deps |
|---------|---------|-------|-----------------|------------------------|-------------|
| **Edge Neural TTS** (default) | `edge` | `zh-CN-yunxi` (built-in voices) | yes | no | `edge-tts` (in pyproject, `uv sync`) |
| **CosyVoice3** (optional) | `cosyvoice` | your brand voice (cloned) | no | yes (`--prompt-wav`) | torch + CosyVoice repo + model |

The whole pipeline is Python (managed with `uv`); the two TTS backends are thin
Python shims (`scripts/edge_tts.py`, `scripts/cosyvoice_tts.py`) invoked by
`generate_audio.py` — the same subprocess pattern as calling `ffmpeg` or
`hyperframes`.

---

## 1. Edge Neural TTS (default)

Microsoft Edge Neural TTS streams high-quality neural voices **for free, with
no API key and no model download**. The only requirement is `edge_tts` plus an
internet connection at synth time. It is the default backend precisely because
it needs **no reference recording** — you can publish immediately.

### Setup (one-time)

```bash
uv sync          # installs edge-tts into the project .venv
```

### Usage

```bash
uv run python scripts/generate_audio.py --script dist/script.json --out dist
# equivalent to: --tts edge --voice zh-CN-yunxi --rate "-2%" --volume "+0%"
```

Overridable env vars: `EDGE_TTS_VOICE`, `EDGE_TTS_RATE`, `EDGE_TTS_VOLUME`,
`TTS_PY` (interpreter with `edge_tts`).

### Common voices

| Voice | Speaker |
|-------|---------|
| `zh-CN-yunxi` (default) | Male, calm teacher |
| `zh-CN-XiaoxiaoNeural` | Female, warm |
| `zh-CN-YunyangNeural` | Male, newscaster |

### The shim

`scripts/edge_tts.py` calls `edge_tts.Communicate(text, voice, rate=, volume=).save()`
to MP3, then transcodes to 16-bit PCM WAV via ffmpeg so the TS side can measure
duration uniformly with ffprobe. Flags mirror the HyperFrames reference script:

```bash
python3 scripts/edge_tts.py --text scene-01.txt --out scene-01.wav \
    --voice zh-CN-yunxi --rate "-2%" --volume "+0%"
```

---

## 2. CosyVoice3 (optional brand-voice clone)

Switch to CosyVoice3 when you want a **consistent house narrator** via zero-shot
voice cloning. It is local (no API key, no internet) but requires a one-time
reference recording and the CosyVoice environment.

### Setup (one-time)

```bash
# 1. Clone CosyVoice (with Matcha-TTS submodule)
git clone --recursive https://github.com/FunAudioLLM/CosyVoice.git
cd CosyVoice && git submodule update --init --recursive

# 2. Create its conda env (recommended) and install deps
conda create -n cosyvoice -y python=3.10
conda activate cosyvoice
pip install -r requirements.txt

# 3. Download the model
python -c "from modelscope import snapshot_download; \
  snapshot_download('FunAudioLLM/Fun-CosyVoice3-0.5B-2512', \
  local_dir='pretrained_models/Fun-CosyVoice3-0.5B')"
```

### Configuration (env vars)

| Env | Meaning |
|-----|---------|
| `COSYVOICE_HOME` | path to the cloned CosyVoice repo |
| `COSYVOICE_MODEL` | path to `Fun-CosyVoice3-0.5B` (defaults to `$COSYVOICE_HOME/pretrained_models/Fun-CosyVoice3-0.5B`) |
| `COSYVOICE_PY` | interpreter with torch + cosyvoice (default `python3`; point at your conda env) |
| `COSYVOICE_PROMPT_WAV` | **your brand voice** reference WAV (clean, ~5–10s, single speaker) |
| `COSYVOICE_PROMPT_TEXT` | transcript of that reference WAV |

### Usage

```bash
uv run python scripts/generate_audio.py --script dist/script.json --tts cosyvoice \
    --prompt-wav "$COSYVOICE_PROMPT_WAV" --prompt-text "$COSYVOICE_PROMPT_TEXT" \
    --speed 1.0 --lang zh --out dist
```

`scripts/cosyvoice_tts.py` loads the model once per process and synthesizes one
WAV via `inference_zero_shot`. Output WAV sample rate follows the model
(24k/25k); the TS side transcodes / measures duration upstream.

---

## 3. Speed / Rate Guidance

| Backend | Param | Slower (tutorial) | Natural | Faster (intro) |
|---------|-------|-------------------|---------|----------------|
| Edge | `--rate` | `-10%` | `-2%` | `+5%` |
| CosyVoice3 | `--speed` | `0.8–0.9` | `1.0` | `1.1–1.2` |

## 4. Timestamps

Neither backend returns word timestamps; scene-level timing is derived
deterministically:

1. Synthesize one WAV per scene: `audio/scene-NN.wav`.
2. Measure each WAV's duration with ffprobe.
3. Build cumulative `start`/`end` in `dist/timestamps.json`:

```json
{
  "total": 62.4,
  "engine": "edge-tts",
  "voice": "zh-CN-yunxi",
  "scenes": [
    { "id": "01", "start": 0.0,  "end": 11.2, "duration": 11.2 },
    { "id": "02", "start": 11.2, "end": 23.9, "duration": 12.7 }
  ]
}
```

If word-level karaoke highlighting is ever required, run
`npx --yes hyperframes transcribe <wav> --model small` per scene.

## 5. Podcast Assembly

`generate-audio.mjs` concatenates the per-scene WAVs into `dist/podcast_full.wav`
with ffmpeg, then transcodes to MP3:

```bash
ffmpeg -y -f concat -safe 0 -i list.txt -c copy dist/podcast_full.wav
ffmpeg -y -i dist/podcast_full.wav -codec:a libmp3lame -qscale:a 2 dist/podcast_full.mp3
```
