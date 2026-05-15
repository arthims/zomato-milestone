"""
phase0.settings
---------------
Typed, validated settings loaded from environment variables (and .env).
All other modules import from here — never call os.environ directly.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

from milestone1.phase0.paths import ENV_FILE


def _load_env(env_file: Path = ENV_FILE) -> None:
    """Load .env if it exists. No-op if the file is missing."""
    if env_file.exists():
        load_dotenv(env_file, override=False)


@dataclass(frozen=True)
class Settings:
    # ── LLM ───────────────────────────────────────────────────────────────
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"

    # ── HuggingFace ───────────────────────────────────────────────────────
    hf_token: str = ""
    hf_dataset_name: str = "ManikaSaini/zomato-restaurant-recommendation"
    hf_dataset_revision: str = "main"  # pin to a commit SHA in production

    # ── Dataset loading ───────────────────────────────────────────────────
    load_limit: int = 5_000          # max rows to load; 0 = no limit
    candidate_cap: int = 20          # max candidates sent to LLM

    # ── API ───────────────────────────────────────────────────────────────
    cors_origins: list[str] = field(default_factory=lambda: ["http://localhost:5173"])
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # ── LLM call ──────────────────────────────────────────────────────────
    llm_timeout_seconds: float = 30.0
    llm_max_tokens: int = 1_000
    llm_temperature: float = 0.3

    # ── Preferences validation ────────────────────────────────────────────
    max_free_text_length: int = 500  # EC-2.4: truncate long free-text

    @property
    def groq_configured(self) -> bool:
        return bool(self.groq_api_key)

    @property
    def hf_configured(self) -> bool:
        return bool(self.hf_token)


def _parse_cors(raw: str) -> list[str]:
    return [o.strip().rstrip("/") for o in raw.split(",") if o.strip()]


def load_settings(env_file: Path = ENV_FILE) -> Settings:
    """
    Load settings from environment (and optionally .env).
    Call once at app startup; store the result; pass it around.
    """
    _load_env(env_file)

    raw_load_limit = os.getenv("LOAD_LIMIT", "5000")
    raw_candidate_cap = os.getenv("CANDIDATE_CAP", "20")

    try:
        load_limit = int(raw_load_limit)
    except ValueError:
        load_limit = 5_000

    try:
        candidate_cap = int(raw_candidate_cap)
    except ValueError:
        candidate_cap = 20

    cors_raw = os.getenv("CORS_ORIGINS", "http://localhost:5173")

    return Settings(
        groq_api_key=os.getenv("GROQ_API_KEY", ""),
        groq_model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
        hf_token=os.getenv("HF_TOKEN", ""),
        load_limit=load_limit,
        candidate_cap=candidate_cap,
        cors_origins=_parse_cors(cors_raw),
    )
