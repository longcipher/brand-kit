# Justfile — format / lint / test for docs (Markdown) and the Python project.
#
# Layout:
#   - Docs (Markdown): formatted + linted with rumdl across the whole repo.
#   - Python project (skills/lc-tech-publisher): formatted + linted with ruff,
#     tested with pytest. All Python tooling runs inside the uv-managed venv.
#
# Run everything:  just            (same as `just all`)
# Dev setup:       just setup      (uv sync + dev group)

# ── Project paths ────────────────────────────────────────────────────────────
skill_dir := "skills/lc-tech-publisher"

# ── Dev setup ────────────────────────────────────────────────────────────────
setup:
    uv sync --group dev

# ── Docs (Markdown) ──────────────────────────────────────────────────────────
docs-format:
    rumdl fmt .

docs-lint:
    rumdl check .

docs: docs-format docs-lint

# ── Python: format ───────────────────────────────────────────────────────────
py-format:
    uv run --project {{skill_dir}} ruff format {{skill_dir}}/scripts {{skill_dir}}/tests

py-lint:
    uv run --project {{skill_dir}} ruff check {{skill_dir}}/scripts {{skill_dir}}/tests

py-test:
    uv run --project {{skill_dir}} pytest

py: py-format py-lint py-test

# ── Everything ───────────────────────────────────────────────────────────────
# Run from repo root so Markdown + Python are both covered.
all: docs py

# Default recipe.
default: all
