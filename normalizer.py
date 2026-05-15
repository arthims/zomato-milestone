"""
phase1_ingestion.normalizer
---------------------------
Pure functions that turn a raw HuggingFace dataset row (dict) into a
canonical Restaurant.  All edge-case handling lives here.

Edge cases handled:
  EC-1.1  Missing / null fields → sentinels
  EC-1.2  Rating out of range   → clamped to [0.0, 5.0]
  EC-1.6  load_limit cap        → enforced in loader, not here
  EC-1.7  Non-UTF-8 names       → preserved as-is (Python str is Unicode)
"""
from __future__ import annotations

import re
import unicodedata
import warnings
from typing import Any

from milestone1.phase1_ingestion.models import (
    Restaurant,
    BUDGET_LOW,
    BUDGET_MEDIUM,
    BUDGET_HIGH,
    BUDGET_UNKNOWN,
)


# ── helpers ────────────────────────────────────────────────────────────────

def _slugify(text: str) -> str:
    """Create a stable ASCII ID from arbitrary Unicode text."""
    nfkd = unicodedata.normalize("NFKD", text)
    ascii_text = nfkd.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^\w\s-]", "", ascii_text).strip().lower()
    return re.sub(r"[\s-]+", "_", slug)


def _parse_rating(raw: Any) -> float:
    """
    Parse rating from various formats:
      "4.1/5" → 4.1
      "4.1"   → 4.1
      "NEW"   → 0.0   (sentinel)
      "-"     → 0.0
      NaN     → 0.0
    Clamp result to [0.0, 5.0] (EC-1.2).
    """
    if raw is None:
        return 0.0
    s = str(raw).strip()
    if not s or s in ("-", "NEW", "nan", "NaN", "None"):
        return 0.0
    # strip trailing "/5" or "/10"
    s = re.sub(r"/\d+$", "", s).strip()
    try:
        value = float(s)
    except ValueError:
        return 0.0
    return max(0.0, min(5.0, value))  # EC-1.2 clamp


def _parse_cuisines(raw: Any) -> tuple[str, ...]:
    """
    Split comma-separated cuisine string into a tuple.
    Handles trailing commas and whitespace (EC-1.1, dataset-contract).
    """
    if not raw:
        return ()
    parts = [c.strip() for c in str(raw).split(",")]
    return tuple(c for c in parts if c)  # drop empty strings


def _parse_votes(raw: Any) -> int:
    if raw is None:
        return 0
    try:
        return max(0, int(float(str(raw))))
    except (ValueError, TypeError):
        return 0


def _parse_cost(raw: Any) -> tuple[str, str]:
    """
    Return (cost_raw, budget_band).
    Strips currency symbols for numeric comparison but preserves original
    string as cost_raw.

    Budget bands (dataset-contract.md):
      ≤ 300  → low
      301–700 → medium
      > 700  → high
    """
    if not raw:
        return "unknown", BUDGET_UNKNOWN
    s = str(raw).strip()
    if not s:
        return "unknown", BUDGET_UNKNOWN

    # extract numeric portion (handles "₹500", "500", "500.00")
    numeric = re.sub(r"[^\d.]", "", s)
    try:
        value = float(numeric)
    except ValueError:
        return s, BUDGET_UNKNOWN

    if value <= 300:
        band = BUDGET_LOW
    elif value <= 700:
        band = BUDGET_MEDIUM
    else:
        band = BUDGET_HIGH

    return s, band


def _make_id(name: str, location: str) -> str:
    return _slugify(f"{name}_{location}")


# ── public API ─────────────────────────────────────────────────────────────

def normalize_row(row: dict[str, Any]) -> Restaurant | None:
    """
    Convert one raw HuggingFace row to a Restaurant.
    Returns None if the row is so malformed it cannot be used at all
    (e.g. missing name).  Logs warnings for recoverable issues.
    """
    name = str(row.get("name") or "").strip()
    if not name:
        warnings.warn("Skipping row with missing name", stacklevel=2)
        return None

    location = str(row.get("location") or "").strip().title() or "Unknown"

    rating = _parse_rating(
        row.get("rate") or row.get("rating")
    )

    cuisines = _parse_cuisines(row.get("cuisines") or row.get("cuisine"))

    cost_raw_key = next(
        (k for k in row if "cost" in k.lower()), None
    )
    cost_raw_val = row.get(cost_raw_key, "") if cost_raw_key else ""
    cost_raw, budget = _parse_cost(cost_raw_val)

    votes = _parse_votes(row.get("votes"))

    restaurant_id = _make_id(name, location)

    return Restaurant(
        restaurant_id=restaurant_id,
        name=name,
        location=location,
        cuisines=cuisines,
        cost_raw=cost_raw,
        budget=budget,
        rating=rating,
        votes=votes,
        restaurant_type=str(row.get("rest_type") or "").strip(),
        listed_type=str(row.get("listed_in(type)") or "").strip(),
    )
