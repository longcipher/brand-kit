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
    "panels": [
        {
            "type": "market",
            "title": "市场概览",
            "start": 4.0,
            "end": 18.0,
            "stats": [
                {"label": "总市值", "value": 2.31, "decimals": 2, "change": "+3.2%", "dir": "up"}
            ],
            "chart": {
                "type": "line",
                "categories": ["Mon", "Tue", "Wed"],
                "series": [{"name": "Idx", "data": [10, 12, 11]}],
            },
        },
        {
            "type": "news",
            "title": "今日要点",
            "start": 18.0,
            "end": 34.0,
            "cards": [
                {"tag": "INFO", "title": "标题一", "body": "摘要", "warn": False},
                {"tag": "WARN", "title": "标题二", "body": "摘要", "warn": True},
                {"tag": "INFO", "title": "标题三", "body": "摘要", "warn": False},
            ],
        },
        {
            "type": "quote",
            "title": "观点",
            "start": 34.0,
            "end": 50.0,
            "author": "KOL",
            "text": "一句**重点**引用",
        },
    ],
    "panelsEn": [
        {
            "type": "news",
            "title": "Today",
            "start": 4.0,
            "end": 18.0,
            "cards": [
                {"tag": "INFO", "title": "Headline", "body": "Body", "warn": False},
            ],
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
    # three dialogue turns => three "speaker" keys in the embedded payload
    assert html.count('"speaker"') == 3
    assert '"female"' in html
    assert '"male"' in html
    assert 'data-duration="12.5"' in html  # total + 0.5s tail
    assert 'id="panels"' in html


def test_build_composition_missing_timings(work: Path) -> None:
    out = work / "video"
    res = run_script(
        "build_composition.py",
        "--script",
        str(work / "script.json"),
        "--out",
        str(out),
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
    assert "en-US-AndrewNeural" in html  # EN voice used for both speakers
    # English panel text, not the zh panel text
    assert "Today" in html
    assert "今日要点" not in html
    assert '"Host"' in html  # enRoles.male
