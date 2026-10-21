# LongCipher Brand Kit Agent Instructions

## Non-negotiables

- Surgical edits only: every changed line must trace to the request. No drive-by refactors, no reformatting untouched code, no deleting pre-existing dead code (mention it instead).
- Fix root causes. Never silence a warning, weaken a check, or patch a symptom to make a gate pass.
- Never report completion while any `just` gate below fails. Report the failure verbatim and stop.
- Stop and ask when a request is ambiguous, conflicts with existing conventions, or requires credentials, publishing, or destructive operations.
- When a correction reveals a missing rule, add one specific rule here ("always X for Y", never "be careful with Y"); delete rules that never catch real errors.

## Scope

- This repo is the LongCipher design system, not a running application: `DESIGN.md` is the source of truth for colour, typography, spacing, radius, components and accessibility; `README.md` is the short quick reference.
- `lc.svg` is the bare mark; `lc11.svg`, `lc31.svg`, `lc43.svg`, `lc169.svg` are the derived lockups (wordmark and slogan as DM Sans path outlines). `favicons/` holds the icon set.
- `scripts/rebuild_logos.py` regenerates every derived SVG from the mark geometry plus the bundled DM Sans faces — edit it, never hand-edit the lockup SVGs.
- `skills/lc-tech-publisher/` is a separate `uv` project (`pyproject.toml`, `uv.lock`, `package = false`): 13 Python scripts, the HTML templates and fonts in `assets/`, five reference guides in `references/`, and one Pytest suite in `tests/`.
- `skills/lc-tech-publisher/assets/templates/` (`cover.html`, `dashboard.html`, `shorts.html`) owns every visual decision; `dist/` holds intermediates and `output/` holds the deliverables.
- English only in code, comments, docs, and commit messages. The media pipeline's *content* is Chinese by design — that is copy, not source.

## Execution

- Parallelize aggressively: dispatch subagents for independent research, exploration, and implementation.
- Logo regeneration, the Python pipeline, and Markdown linting are independent tracks — run them concurrently, but never let two agents write the same generated file.
- NEVER use `git worktree`. Edit the current branch in place.
- TDD for behavior changes: add the failing Pytest case in `skills/lc-tech-publisher/tests/` first, make the smallest change that passes it, then run the whole `just test` suite.

## Verification loop

After each feature or bug fix, in order; any failure means the task is not done:

```bash
just format
just lint
just test
```

`format` runs `rumdl fmt` over the Markdown and `ruff format` over the skill's `scripts/` and `tests/`; `lint` runs `rumdl check`, `ruff check`, and `ruff format --check`; `test` runs the Pytest suite inside the skill's `uv` environment.

## Repository rules

- `DESIGN.md` wins over `README.md` wins over any template. If a token changes, update `DESIGN.md` first, then the templates, then the docs.
- Token discipline: canvas `#fafbfc`, surface `#ffffff`, ink `#171718`, hairline `#e0e2e8`, the single accent `#0a72ef` (body text uses `#0a63d0` for AA contrast), error `#ff5b4f` / `#c62d2d`, dark surfaces `#0a0a0c` → `#2a2d33`.
- Spacing is a 4 / 8 / 16 / 32 rhythm; UI radius is 2px maximum (illustration chips ≤16px, diagram primitives may be round); no pills, no second hue, no gradients.
- Type is DM Sans (display 700, body 400) plus JetBrains Mono for code, with `PingFang SC` / `Microsoft YaHei` / `Noto Sans SC` as the CJK fallback — the bundled faces are Latin subsets.
- Accessibility is a hard gate: body text ≥ 4.5:1, large text and UI ≥ 3:1, visible focus ring, keyboard-operable flows.
- The publisher skill writes JSON only. Never author CSS, HTML, or animations from the model — extend `assets/templates/` and the CSS variables instead, and re-run the builders rather than hand-editing generated HTML.
- Slide types are fixed: `keypoint`, `three_points`, `chart`, `counter`, `cards`, `steps`, `metric_chart`, `pipeline`, `benchmark`, `security`, `terminal`, `outro`. Adding a type means editing the template branch *and* `references/script-schema.md`.
- Every `keypoint` slide carries a `body` array of 2–4 substantive paragraphs; a one-line slide is a failed gate.
- Length gate: Chinese narration runs at roughly 5.5 characters per second, English at roughly 2.2 words per second. Author to `meta.target_seconds × 5.5` zh characters (or `× 2.2` en words) — never cut an article section to hit a duration.
- Content completeness gate: every H2/H3 of the source article must appear in the dialogue or the slides.
- Captions must be byte-identical to the spoken line, and caption/audio `data-duration` must equal the turn duration in `speaker_timestamps[_en].json`.
- Fonts and GSAP are vendored into every build tree — no CDN, no network at render time.

## Dependency choices

- Python 3.11+ managed by `uv`; `edge-tts` is the only runtime dependency and provides the default narration voices (`zh-CN-YunxiNeural`, `zh-CN-XiaoxiaoNeural`, `en-US-AndrewNeural`).
- `ruff` and `pytest` are the dev-group tools. `typos` is not wired in — the vendored GSAP bundle and the DESIGN.md copy trips it.
- The render step shells out to `npx --yes hyperframes` (Node ≥ 22) and uses `ffmpeg` / `ffprobe`; `scripts/check_env.py` is the gate that proves the toolchain before a run.
- The optional CosyVoice3 brand-voice clone lives in its own environment and is reached through `scripts/cosyvoice_tts.py`; never add it to `pyproject.toml` dependencies.

## Code conventions

- `ruff` settings live in `skills/lc-tech-publisher/pyproject.toml` (line length 100, target `py311`, rules `E,F,I,W,UP,B,C4,SIM`).
- Scripts are invoked as `uv run --project skills/lc-tech-publisher python scripts/<name>.py --help`; `scripts/` is a collection, not an importable package.
- `scripts/rebuild_logos.py` needs extra packages that are not project dependencies: `uv run --with fonttools --with brotli python scripts/rebuild_logos.py`.
- `ruff` and `pytest` are configured against the skill project only; `scripts/rebuild_logos.py` at the repo root sits outside that scope and is not linted by `just lint`.
- `ruff` and `pytest` caches land in the repo root (`.ruff_cache/`, `.pytest_cache/`) because the commands run from the repo root — they are gitignored, not stray files.
- Every build script takes `--lang zh|en` and writes to a language-specific tree (`dist/audio` vs `dist/audio_en`, `dist/video_zh` vs `dist/video_en`) so the two passes never collide.
