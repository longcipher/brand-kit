# Justfile — docs (Markdown) plus the lc-tech-publisher Python project.
#
# The Python project lives in skills/lc-tech-publisher (its own pyproject.toml
# and uv.lock), so every Python recipe targets that project explicitly.
# Run everything:  just all

# ── Project paths ────────────────────────────────────────────────────────────
skill_dir := "skills/lc-tech-publisher"
py_scope := skill_dir + "/scripts " + skill_dir + "/tests"

# Default recipe to display help
default:
  @just --list

# Sync the skill project's dev dependencies
setup:
  uv sync --project {{skill_dir}} --group dev

# ── Docs (Markdown) ──────────────────────────────────────────────────────────

# Format the Markdown docs
docs-format:
  rumdl fmt .

# Lint the Markdown docs
docs-lint:
  rumdl check .

# Format and lint the Markdown docs
docs: docs-format docs-lint

# ── Python (skills/lc-tech-publisher) ────────────────────────────────────────

# Format the skill's Python sources
py-format:
  uv run --project {{skill_dir}} ruff format {{py_scope}}

# Lint the skill's Python sources
py-lint:
  uv run --project {{skill_dir}} ruff check {{py_scope}}

# Run the skill's Pytest suite
py-test:
  uv run --project {{skill_dir}} pytest

# Format, lint, and test the skill's Python sources
py: py-format py-lint py-test

# ── Canonical gates ──────────────────────────────────────────────────────────

# Format Markdown and Python
format: docs-format py-format

# Auto-fix what format cannot
fix:
  rumdl check --fix .
  uv run --project {{skill_dir}} ruff check --fix {{py_scope}}

# Run all lints
lint:
  rumdl check .
  uv run --project {{skill_dir}} ruff check {{py_scope}}
  uv run --project {{skill_dir}} ruff format --check {{py_scope}}

# Run the test suite
test: py-test

# Rebuild the derived logo SVGs from the mark and the bundled DM Sans faces
build:
  uv run --with fonttools --with brotli python scripts/rebuild_logos.py

# Check the publisher toolchain (ffmpeg, hyperframes, TTS backend)
check-env:
  uv run --project {{skill_dir}} python {{skill_dir}}/scripts/check_env.py

# Fail if Chinese characters appear in the English-facing docs
check-cn:
  #!/usr/bin/env bash
  set -uo pipefail
  if rg --line-number --column "\p{Han}" AGENTS.md Justfile DESIGN.md scripts/; then
    echo "error: Chinese characters found above" >&2
    exit 1
  fi
  echo "ok: no Chinese characters found"

# Full CI check
ci: lint test

# ── Maintenance & Tools ─────────────────────────────────────────────────────

# Remove caches
clean:
  rm -rf .pytest_cache/ .ruff_cache/ {{skill_dir}}/.pytest_cache/ {{skill_dir}}/.ruff_cache/
  find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

# Install the tools this Justfile needs
setup-tools:
  cargo install rumdl

# Run format, lint, and test
all: format lint test
