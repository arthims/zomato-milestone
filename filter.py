"""
phase3_integration.filter
--------------------------
Deterministic hard-filter + pre-rank that reduces the full corpus to a
manageable candidate list before the LLM is called.

Edge cases handled:
  EC-2.3  No cuisine overlap          → returns []
  EC-2.7  Budget with no matches      → returns []
  EC-3.1  Too many candidates         → capped at candidate_cap
  EC-3.2  Zero candidates             → returns [] (caller skips LLM)
  EC-3.3  Single candidate            → returned as-is
  EC-3.5  Location special chars      → title-cased match is forgiving
"""
from __future__ import annotations

import logging

from milestone1.phase1_ingestion.models import Restaurant
from milestone1.phase2_preferences.models import UserPreferences

logger = logging.getLogger(__name__)


def filter_and_rank(
    restaurants: list[Restaurant],
    prefs: UserPreferences,
    candidate_cap: int = 20,
) -> list[Restaurant]:
    """
    Apply hard filters then pre-sort by rating.

    Filters applied in order:
      1. Location  — case-insensitive substring match
      2. Min rating
      3. Budget    — if specified
      4. Cuisines  — if specified, at least one must overlap

    Returns up to `candidate_cap` restaurants sorted by rating desc.
    """
    candidates = restaurants

    # 1. Location filter (case-insensitive, partial match tolerated)
    loc = prefs.location.lower().strip()
    candidates = [
        r for r in candidates
        if loc in r.location.lower() or r.location.lower() in loc
    ]
    logger.debug("After location filter ('%s'): %d", prefs.location, len(candidates))

    # 2. Min-rating filter
    if prefs.min_rating > 0.0:
        candidates = [r for r in candidates if r.rating >= prefs.min_rating]
        logger.debug("After rating filter (>=%s): %d", prefs.min_rating, len(candidates))

    # 3. Budget filter
    if prefs.budget is not None:
        candidates = [r for r in candidates if r.budget == prefs.budget.value]
        logger.debug("After budget filter ('%s'): %d", prefs.budget.value, len(candidates))

    # 4. Cuisine filter — at least one cuisine must overlap (EC-2.3)
    if prefs.cuisines:
        pref_cuisines = {c.lower() for c in prefs.cuisines}
        candidates = [
            r for r in candidates
            if any(rc.lower() in pref_cuisines for rc in r.cuisines)
            or any(pc in rc.lower() for rc in r.cuisines for pc in pref_cuisines)
        ]
        logger.debug(
            "After cuisine filter (%s): %d", prefs.cuisines, len(candidates)
        )

    # Pre-sort by rating descending (EC-3.1 ranking hint)
    candidates.sort(key=lambda r: r.rating, reverse=True)

    # Cap (EC-3.1)
    if len(candidates) > candidate_cap:
        logger.info(
            "Candidate cap hit: %d → %d (cap=%d)",
            len(candidates), candidate_cap, candidate_cap,
        )
        candidates = candidates[:candidate_cap]

    return candidates
