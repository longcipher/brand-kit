"""Smoke tests for the offline-safe parts of the lc-tech-publisher pipeline.

These exercise the real CLI via `uv run python scripts/<name>.py` against
temp dirs, covering the paths that need no network, ffmpeg, or hyperframes:
  - parse_article.py --validate (schema gate + default filling)
  - build_cover.py (template injection + logo bundling)
  - build_composition.py (HTML/GSAP generation, duration math)
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
    "meta": {"title": "测试标题", "subtitle": "副标题"},
    "cover": {"title": "封面标题"},
    "scenes": [
        {"id": "01", "title": "场景1", "narration": "这是第一句旁白。"},
        {
            "id": "02",
            "title": "场景2",
            "narration": "这是第二句旁白。",
            "points": ["要点一", "要点二"],
        },
        {"id": "03", "title": "场景3", "narration": "这是第三句旁白。", "code": "const x = 1;"},
        {"id": "04", "title": "场景4", "narration": "这是第四句旁白。"},
        {"id": "05", "title": "场景5", "narration": "这是第五句旁白。"},
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
    assert data["meta"]["kicker"] == "TECH EXPLAINER"
    assert data["meta"]["target_seconds"] > 0


def test_validate_rejects_too_few_scenes(tmp_path: Path) -> None:
    bad = dict(VALID_SCRIPT)
    bad["scenes"] = bad["scenes"][:3]
    p = tmp_path / "bad.json"
    p.write_text(json.dumps(bad, ensure_ascii=False), encoding="utf-8")
    res = run_script("parse_article.py", "--validate", str(p))
    assert res.returncode == 1
    assert "5" in res.stderr


def test_build_cover(work: Path) -> None:
    out = work / "cover"
    res = run_script("build_cover.py", "--script", str(work / "script.json"), "--out", str(out))
    assert res.returncode == 0, res.stderr
    html = (out / "cover.html").read_text(encoding="utf-8")
    assert "封面标题" in html
    assert (out / "logos" / "lc.svg").exists()
    assert (out / "hyperframes.json").exists()


def test_build_composition(work: Path) -> None:
    ts = {
        "total": 12.0,
        "engine": "edge-tts",
        "voice": "zh-CN-yunxi",
        "scenes": [
            {"id": f"{i + 1:02d}", "start": i * 2.4, "end": (i + 1) * 2.4, "duration": 2.4}
            for i in range(5)
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
    assert html.count('class="scene clip"') == 5
    assert html.count('class="cap clip"') == 5
    assert 'data-duration="12.5"' in html  # total + 0.5s tail


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
    assert "timestamps" in res.stderr
