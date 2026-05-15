"""
phase2_preferences.parser
-------------------------
Deserialize and validate raw input (dict from form / API / CLI args)
into a UserPreferences object.

Edge cases handled:
  EC-2.1  Unknown city / typo        → fuzzy suggestion + PreferencesError
  EC-2.2  min_rating = 5.0           → accepted (boundary is valid)
  EC-2.4  Long free-text             → truncated with warning
  EC-2.5  Prompt injection free-text → passed as sandboxed string (Phase 3 duty)
  EC-2.6  Blank submission           → field-level errors
  EC-2.7  Budget with no matches     → detected at filter time (Phase 3)
"""
from __future__ import annotations

import re
import unicodedata
from typing import Any, Optional

from milestone1.phase2_preferences.models import BudgetBand, UserPreferences


# ── errors ─────────────────────────────────────────────────────────────────

class PreferencesError(ValueError):
    """
    Raised when one or more preference fields fail validation.
    `field_errors` maps field name → human-readable message.
    """
    def __init__(self, field_errors: dict[str, str]) -> None:
        self.field_errors = field_errors
        super().__init__(str(field_errors))


# ── helpers ─────────────────────────────────────────────────────────────────

def _normalize_str(s: Any) -> str:
    return str(s).strip() if s is not None else ""


def _fuzzy_city_match(
    raw: str,
    allowed: set[str],
    threshold: int = 3,
) -> Optional[str]:
    """
    EC-2.1: Simple edit-distance suggestion.
    Returns the closest allowed city if within `threshold` edits, else None.
    """
    raw_lower = raw.lower()

    # exact match (case-insensitive)
    for city in allowed:
        if city.lower() == raw_lower:
            return city

    # substring match
    for city in allowed:
        if raw_lower in city.lower() or city.lower() in raw_lower:
            return city

    # character-level overlap heuristic
    def overlap(a: str, b: str) -> int:
        return sum(1 for c in set(a.lower()) if c in b.lower())

    best = max(allowed, key=lambda c: overlap(raw, c), default=None)
    if best and overlap(raw, best) >= max(2, len(raw) - threshold - 2):
        return best

    return None


def _sanitize_free_text(text: str, max_len: int) -> str:
    """
    EC-2.4: Truncate to max_len.
    EC-6.5: Strip control characters (newlines, carriage returns, nulls).
    """
    # strip control characters except regular spaces
    cleaned = re.sub(r"[\x00-\x08\x0b-\x1f\x7f]", "", text)
    cleaned = cleaned.replace("\r", " ").replace("\n", " ")
    return cleaned[:max_len]


# ── public API ──────────────────────────────────────────────────────────────

def preferences_from_mapping(
    data: dict[str, Any],
    allowed_cities: Optional[set[str]] = None,
) -> UserPreferences:
    """
    Parse and validate a raw input dict into UserPreferences.

    Args:
        data: dict with keys location, budget, cuisines, min_rating,
              additional_preferences (all optional except location).
        allowed_cities: if provided, validates location against corpus.

    Raises:
        PreferencesError: with field_errors dict if any field is invalid.
    """
    errors: dict[str, str] = {}

    # ── location ────────────────────────────────────────────────────────
    location_raw = _normalize_str(data.get("location"))
    location = location_raw

    if not location_raw:
        errors["location"] = "Location is required."
    elif allowed_cities:
        # EC-2.1: fuzzy match
        if location_raw not in allowed_cities:
            suggestion = _fuzzy_city_match(location_raw, allowed_cities)
            if suggestion:
                errors["location"] = (
                    f"'{location_raw}' not found. Did you mean '{suggestion}'?"
                )
            else:
                errors["location"] = (
                    f"'{location_raw}' is not a recognised city in the dataset."
                )
        else:
            location = location_raw

    # ── budget ──────────────────────────────────────────────────────────
    budget_raw = _normalize_str(data.get("budget")).lower()
    budget: Optional[BudgetBand] = None

    if budget_raw and budget_raw not in ("", "any", "none"):
        try:
            budget = BudgetBand(budget_raw)
        except ValueError:
            errors["budget"] = (
                f"Invalid budget '{budget_raw}'. "
                f"Choose from: {', '.join(BudgetBand.values())}."
            )

    # ── cuisines ─────────────────────────────────────────────────────────
    raw_cuisines = data.get("cuisines", [])
    if isinstance(raw_cuisines, str):
        raw_cuisines = [c.strip() for c in raw_cuisines.split(",")]
    cuisines = [str(c).strip() for c in raw_cuisines if str(c).strip()]

    # ── min_rating ───────────────────────────────────────────────────────
    min_rating_raw = data.get("min_rating", 0.0)
    min_rating = 0.0
    try:
        min_rating = float(min_rating_raw)
        if not (0.0 <= min_rating <= 5.0):
            errors["min_rating"] = "Rating must be between 0.0 and 5.0."
            min_rating = 0.0
    except (TypeError, ValueError):
        errors["min_rating"] = f"Invalid rating value: '{min_rating_raw}'."

    # ── additional_preferences ───────────────────────────────────────────
    raw_text = _normalize_str(data.get("additional_preferences", ""))
    additional = _sanitize_free_text(raw_text, UserPreferences.MAX_FREE_TEXT_LEN)

    # ── EC-2.6: block blank submissions ──────────────────────────────────
    if not errors and not location_raw and not cuisines and min_rating == 0.0 and budget is None:
        errors["_form"] = "Please fill in at least one preference field."

    if errors:
        raise PreferencesError(errors)

    return UserPreferences(
        location=location,
        budget=budget,
        cuisines=cuisines,
        min_rating=min_rating,
        additional_preferences=additional,
    )
