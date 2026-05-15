"""
phase0.doctor
-------------
Health checks for the local development environment.
Called by `milestone1 doctor` CLI command.
Returns a list of CheckResult objects for rendering.
"""
from __future__ import annotations

import importlib
import shutil
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from milestone1.phase0.paths import ENV_FILE, ENV_EXAMPLE_FILE, REPO_ROOT
from milestone1.phase0.settings import load_settings


class Status(str, Enum):
    OK = "ok"
    WARN = "warn"
    FAIL = "fail"


@dataclass
class CheckResult:
    name: str
    status: Status
    message: str
    hint: str = ""


def _check_python_version() -> CheckResult:
    major, minor = sys.version_info[:2]
    if major == 3 and minor >= 11:
        return CheckResult("Python version", Status.OK, f"Python {major}.{minor}")
    return CheckResult(
        "Python version",
        Status.FAIL,
        f"Python {major}.{minor} detected",
        hint="Upgrade to Python 3.11 or later.",
    )


def _check_env_file() -> CheckResult:
    if ENV_FILE.exists():
        return CheckResult(".env file", Status.OK, f"Found at {ENV_FILE}")
    return CheckResult(
        ".env file",
        Status.WARN,
        ".env not found — using environment variables only",
        hint=f"Copy {ENV_EXAMPLE_FILE} to {ENV_FILE} and fill in your keys.",
    )


def _check_groq_key() -> CheckResult:
    settings = load_settings()
    if settings.groq_configured:
        # Show only first 8 chars for safety
        masked = settings.groq_api_key[:8] + "…"
        return CheckResult("GROQ_API_KEY", Status.OK, f"Set ({masked})")
    return CheckResult(
        "GROQ_API_KEY",
        Status.WARN,
        "Not set — AI ranking will be unavailable",
        hint="Add GROQ_API_KEY to .env. Get a key at https://console.groq.com/keys",
    )


def _check_hf_token() -> CheckResult:
    settings = load_settings()
    if settings.hf_configured:
        return CheckResult("HF_TOKEN", Status.OK, "Set (Hub rate limits increased)")
    return CheckResult(
        "HF_TOKEN",
        Status.WARN,
        "Not set — using anonymous HuggingFace access",
        hint="Add HF_TOKEN to .env if you hit rate limit errors during data load.",
    )


def _check_package(name: str, import_name: str | None = None) -> CheckResult:
    mod = import_name or name
    try:
        importlib.import_module(mod)
        return CheckResult(f"Package: {name}", Status.OK, "Installed")
    except ImportError:
        return CheckResult(
            f"Package: {name}",
            Status.FAIL,
            "Not installed",
            hint=f"Run: pip install {name}",
        )


def _check_data_dir() -> CheckResult:
    data_dir = REPO_ROOT / "data"
    if data_dir.exists():
        return CheckResult("data/ directory", Status.OK, f"Exists at {data_dir}")
    return CheckResult(
        "data/ directory",
        Status.WARN,
        "Not created yet",
        hint="Run `milestone1 doctor` again after first ingest — it will be created automatically.",
    )


def run_all_checks() -> list[CheckResult]:
    """Run all environment checks and return results."""
    checks: list[CheckResult] = []

    checks.append(_check_python_version())
    checks.append(_check_env_file())
    checks.append(_check_groq_key())
    checks.append(_check_hf_token())

    # Required packages
    for pkg, mod in [
        ("datasets", "datasets"),
        ("httpx", "httpx"),
        ("typer", "typer"),
        ("rich", "rich"),
        ("dotenv", "dotenv"),
    ]:
        checks.append(_check_package(pkg, mod))

    checks.append(_check_data_dir())

    return checks


def has_failures(results: list[CheckResult]) -> bool:
    return any(r.status == Status.FAIL for r in results)
