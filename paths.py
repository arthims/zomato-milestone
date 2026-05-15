"""
phase0.paths
------------
Single source of truth for every filesystem path the project uses.
Import from here instead of constructing paths ad-hoc elsewhere.
"""
from __future__ import annotations

from pathlib import Path

# ── Repo root ──────────────────────────────────────────────────────────────
# Resolved from this file's location: src/milestone1/phase0/paths.py
#   → parent = phase0/
#   → parent.parent = milestone1/
#   → parent.parent.parent = src/
#   → parent.parent.parent.parent = repo root
REPO_ROOT: Path = Path(__file__).resolve().parents[3]

# ── Source tree ────────────────────────────────────────────────────────────
SRC_ROOT: Path = REPO_ROOT / "src"
PACKAGE_ROOT: Path = SRC_ROOT / "milestone1"

# ── Config / secrets ───────────────────────────────────────────────────────
ENV_FILE: Path = REPO_ROOT / ".env"
ENV_EXAMPLE_FILE: Path = REPO_ROOT / ".env.example"

# ── Data / cache ───────────────────────────────────────────────────────────
DATA_DIR: Path = REPO_ROOT / "data"
HF_CACHE_DIR: Path = DATA_DIR / ".hf_cache"

# ── Docs ───────────────────────────────────────────────────────────────────
DOCS_DIR: Path = REPO_ROOT / "docs"

# ── Tests ──────────────────────────────────────────────────────────────────
TESTS_DIR: Path = REPO_ROOT / "tests"
FIXTURES_DIR: Path = TESTS_DIR / "fixtures"


def ensure_dirs() -> None:
    """Create runtime directories that must exist before the app runs."""
    for d in (DATA_DIR, HF_CACHE_DIR, FIXTURES_DIR):
        d.mkdir(parents=True, exist_ok=True)
