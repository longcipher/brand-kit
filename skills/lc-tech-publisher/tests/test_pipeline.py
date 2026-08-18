"""Smoke tests for the offline-safe parts of the lc-tech-publisher pipeline.

These exercise the real CLI via `uv run python scripts/<name>.py` against
temp dirs, covering the paths that need no network, ffmpeg, or hyperframes:
  - parse_article.py --validate (dialogue + panels schema gate + default filling)
  - build_cover.py (4-ratio template injection + logo bundling)
  - build_composition.py (dark dashboard HTML/GSAP generation, duration math)
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

SKILL = Path(__file__).resolve().parent.parent
SCRIPTS = SKILL / "scripts"


def run_script(name: str, *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    cmd = [sys.executable, str(SCRIPTS / name), *args]
    # Use the skill's own venv python if present, else current interpreter.
    venv_py = SKILL / ".venv" / "bin" / "python"
    if venv_py.exists():
        cmd[0] = str(venv_py)
    return subprocess.run(cmd, capture_output=True, text=True, cwd=str(cwd) if cwd else None)


VALID_SCRIPT = {
    "meta": {
        "title": "测试标题",
        "subtitle": "副标题",
        "enVoice": "en-US-AndrewNeural",
        "enRoles": {"male": "Host", "female": "Co-host"},
    },
    "cover": {"title": "封面标题"},
    "coverEn": {"title": "Cover Title", "kicker": "EN BRIEF", "subtitle": "EN subtitle"},
    "ticker": [
        {"label": "BTC", "value": "64,210", "change": "+2.4%", "dir": "up"},
        {"label": "ETH", "value": "3,420", "change": "-1.1%", "dir": "down"},
    ],
    "tickerEn": [
        {"label": "BTC", "value": "64,210", "change": "+2.4%", "dir": "up"},
    ],
    "slides": [
        {
            "type": "keypoint",
            "eyebrow": "核心观点",
            "icon": "spark",
            "statement": "市场进入横盘,但结构性信号在累积。",
            "analysis": "价格只是表层,真正的变化在结构与机制。",
            "callback": ["呼应开场:宏观压力是今天的暗线"],
            "bullets": ["事实一", "事实二"],
        },
        {
            "type": "three_points",
            "title": "今日三条主线",
            "points": [
                {"no": "01", "title": "算力", "body": "矿企把算力迁向 AI。"},
                {"no": "02", "title": "机构", "body": "ETF 与储备纳入资产负债表。"},
                {"no": "03", "title": "利率", "body": "代币化美债锚定无风险利率。"},
            ],
        },
    ],
    "slidesEn": [
        {
            "type": "keypoint",
            "eyebrow": "Core Point",
            "icon": "rocket",
            "statement": "Market chops sideways, but structural signals build.",
            "analysis": "Price is the surface; structure is the story.",
            "bullets": ["Fact one", "Fact two"],
        },
    ],
    "podcast": [
        {"id": "01", "speaker": "male", "text": "今天我们来聊一个话题。"},
        {"id": "02", "speaker": "female", "text": "那这个到底是什么意思呢？"},
        {"id": "03", "speaker": "male", "text": "简单来说就是这样的。"},
    ],
    "podcastEn": [
        {"id": "01", "speaker": "male", "text": "Let's talk about a topic."},
        {"id": "02", "speaker": "female", "text": "What does that mean?"},
        {"id": "03", "speaker": "male", "text": "Simply put, it is this."},
    ],
}


@pytest.fixture
def work(tmp_path: Path) -> Path:
    (tmp_path / "script.json").write_text(
        json.dumps(VALID_SCRIPT, ensure_ascii=False), encoding="utf-8"
    )
    return tmp_path


def test_validate_ok(work: Path) -> None:
    res = run_script("parse_article.py", "--validate", str(work / "script.json"))
    assert res.returncode == 0, res.stderr
    data = json.loads((work / "script.json").read_text(encoding="utf-8"))
    assert data["meta"]["lang"] == "zh"
    assert data["meta"]["kicker"] == "TECH BRIEF"
    assert data["meta"]["target_seconds"] > 0
    assert data["meta"]["roles"]["male"] == "主讲"


def test_validate_rejects_empty_podcast(tmp_path: Path) -> None:
    bad = dict(VALID_SCRIPT)
    bad["podcast"] = []
    p = tmp_path / "bad.json"
    p.write_text(json.dumps(bad, ensure_ascii=False), encoding="utf-8")
    res = run_script("parse_article.py", "--validate", str(p))
    assert res.returncode == 1
    assert "podcast" in res.stderr


def test_validate_rejects_bad_speaker(tmp_path: Path) -> None:
    bad = dict(VALID_SCRIPT)
    bad["podcast"] = [{"id": "01", "speaker": "robot", "text": "hi"}]
    p = tmp_path / "bad.json"
    p.write_text(json.dumps(bad, ensure_ascii=False), encoding="utf-8")
    res = run_script("parse_article.py", "--validate", str(p))
    assert res.returncode == 1
    assert "speaker" in res.stderr


def test_build_cover_four_ratios(work: Path) -> None:
    out = work / "cover"
    res = run_script("build_cover.py", "--script", str(work / "script.json"), "--out", str(out))
    assert res.returncode == 0, res.stderr
    for name in ("16x9", "9x16", "4x3", "3x4"):
        html = (out / f"cover_{name}.html").read_text(encoding="utf-8")
        assert "封面标题" in html
    assert (out / "logos" / "lc.svg").exists()
    manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
    assert set(manifest["ratios"].keys()) == {"16x9", "9x16", "4x3", "3x4"}


def test_build_composition(work: Path) -> None:
    ts = {
        "total": 12.0,
        "engine": "edge-tts",
        "voices": {"male": "zh-CN-YunxiNeural", "female": "zh-CN-XiaoxiaoNeural"},
        "turns": [
            {
                "id": f"{i + 1:02d}",
                "speaker": "male" if i % 2 == 0 else "female",
                "voice": "zh-CN-YunxiNeural",
                "text": "x",
                "file": f"audio/turn-{i + 1:02d}.wav",
                "start": i * 4.0,
                "end": (i + 1) * 4.0,
                "duration": 4.0,
            }
            for i in range(3)
        ],
    }
    (work / "ts.json").write_text(json.dumps(ts, ensure_ascii=False), encoding="utf-8")
    out = work / "video"
    res = run_script(
        "build_composition.py",
        "--script",
        str(work / "script.json"),
        "--timings",
        str(work / "ts.json"),
        "--out",
        str(out),
    )
    assert res.returncode == 0, res.stderr
    html = (out / "index.html").read_text(encoding="utf-8")
    # Captions + audio clips are injected at runtime from window.LC_DATA, so
    # assert on the data payload markers instead of static DOM nodes.
    assert "window.LC_DATA" in html
    # three dialogue turns => each turn (and each of its cues) carries speaker
    assert html.count('"speaker"') >= 3
    assert '"female"' in html
    assert '"male"' in html
    assert 'data-duration="12.5"' in html  # total + 0.5s tail
    assert 'id="stage"' in html


def test_build_composition_visualizers(work: Path) -> None:
    """The five content-aware visualizer slide types + the keypoint `visual`
    field must survive into the LC_DATA payload and render their data."""
    script = json.loads((work / "script.json").read_text(encoding="utf-8"))
    script["slides"] = [
        {
            "type": "keypoint",
            "eyebrow": "行情",
            "statement": "链上余额累积。",
            "visual": "metric_chart",
            "chart": {
                "title": "BTC 余额",
                "unit": "万 BTC",
                "points": [62, 64, 70],
                "labels": ["M1", "M2", "M3"],
            },
        },
        {
            "type": "pipeline",
            "title": "MEV",
            "pipeline": {"nodes": ["Sequencer", "Builder", "Proposer"]},
        },
        {
            "type": "benchmark",
            "title": "吞吐",
            "benchmark": {"bars": [{"label": "Qwen", "value": 140, "suffix": " tok/s"}]},
        },
        {"type": "security", "title": "告警", "security": {"cvss": 9.8, "ports": ["445", "22"]}},
        {
            "type": "terminal",
            "title": "代码",
            "terminal": {"lines": ["$ cargo install mev-rs", "> v0.4.2 released"]},
        },
    ]
    (work / "script.json").write_text(json.dumps(script, ensure_ascii=False), encoding="utf-8")
    ts = {
        "total": 12.0,
        "engine": "edge-tts",
        "turns": [
            {
                "id": f"{i + 1:02d}",
                "speaker": "male" if i % 2 == 0 else "female",
                "voice": "zh-CN-YunxiNeural",
                "text": "x",
                "file": f"audio/turn-{i + 1:02d}.wav",
                "start": i * 4.0,
                "end": (i + 1) * 4.0,
                "duration": 4.0,
            }
            for i in range(3)
        ],
    }
    (work / "ts.json").write_text(json.dumps(ts, ensure_ascii=False), encoding="utf-8")
    out = work / "video"
    res = run_script(
        "build_composition.py",
        "--script",
        str(work / "script.json"),
        "--timings",
        str(work / "ts.json"),
        "--out",
        str(out),
    )
    assert res.returncode == 0, res.stderr
    html = (out / "index.html").read_text(encoding="utf-8")
    # each visualizer key + its data survives into the payload
    for key in ("metric_chart", "pipeline", "benchmark", "security", "terminal"):
        assert f'"{key}"' in html
    assert "Sequencer" in html
    assert "cargo install mev-rs" in html
    assert "9.8" in html


def test_build_composition_missing_timings(work: Path) -> None:
    out = work / "video"
    res = run_script(
        "build_composition.py",
        "--script",
        str(work / "script.json"),
        "--out",
        str(out),
        cwd=work,  # isolate: no dist/speaker_timestamps.json inside the tmp dir
    )
    assert res.returncode == 1
    assert "timings" in res.stderr


def test_build_cover_english(work: Path) -> None:
    out = work / "cover_en"
    res = run_script(
        "build_cover.py", "--script", str(work / "script.json"), "--lang", "en", "--out", str(out)
    )
    assert res.returncode == 0, res.stderr
    for name in ("16x9", "9x16", "4x3", "3x4"):
        html = (out / f"cover_{name}.html").read_text(encoding="utf-8")
        # English cover text, not the zh cover title
        assert "Cover Title" in html
        assert "封面标题" not in html
        assert 'lang="en"' in html


def test_build_composition_english(work: Path) -> None:
    ts = {
        "total": 12.0,
        "engine": "edge-tts",
        "lang": "en",
        "voices": {"male": "en-US-AndrewNeural", "female": "en-US-AndrewNeural"},
        "turns": [
            {
                "id": f"{i + 1:02d}",
                "speaker": "male" if i % 2 == 0 else "female",
                "voice": "en-US-AndrewNeural",
                "text": "English line",
                "file": f"audio/turn-{i + 1:02d}.wav",
                "start": i * 4.0,
                "end": (i + 1) * 4.0,
                "duration": 4.0,
            }
            for i in range(3)
        ],
    }
    (work / "ts.json").write_text(json.dumps(ts, ensure_ascii=False), encoding="utf-8")
    out = work / "video_en"
    res = run_script(
        "build_composition.py",
        "--script",
        str(work / "script.json"),
        "--timings",
        str(work / "ts.json"),
        "--lang",
        "en",
        "--out",
        str(out),
    )
    assert res.returncode == 0, res.stderr
    html = (out / "index.html").read_text(encoding="utf-8")
    assert '"lang": "en"' in html
    assert "en-US-AndrewNeural" in html  # EN voice carried on turns payload
    # English slide text + its icon survive into the LC_DATA payload (the
    # template's zh fallback string is static template source, not data).
    assert "Core Point" in html
    assert "Market chops sideways" in html
    assert "rocket" in html  # slidesEn[0].icon survives into the payload
