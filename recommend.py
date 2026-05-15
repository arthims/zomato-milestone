"""
phase4_llm.recommend
--------------------
Main orchestration: call LLM → parse → validate → fallback if needed.
"""
from __future__ import annotations

import logging
import time
from typing import Optional

from milestone1.phase1_ingestion.models import Restaurant
from milestone1.phase2_preferences.models import UserPreferences
from milestone1.phase3_integration.output import IntegrationOutput
from milestone1.phase4_llm.client import call_groq, _parse_rankings, HTTPStatusError, TimeoutError
from milestone1.phase4_llm.models import RankedItem, RecommendationResult

logger = logging.getLogger(__name__)

_TEMPLATE = "Matches your preferences for {cuisines} in {location} within your budget."


def _template_explanation(r: Restaurant, prefs: UserPreferences) -> str:
    cuisines = ", ".join(r.cuisines[:2]) if r.cuisines else "local cuisine"
    return _TEMPLATE.format(cuisines=cuisines, location=prefs.location)


def _deterministic_top_k(
    candidates: list[Restaurant],
    prefs: UserPreferences,
    k: int = 5,
) -> list[RankedItem]:
    top = sorted(candidates, key=lambda r: r.rating, reverse=True)[:k]
    return [
        RankedItem(rank=i + 1, restaurant=r, explanation=_template_explanation(r, prefs))
        for i, r in enumerate(top)
    ]


def recommend_with_groq(
    integration: IntegrationOutput,
    prefs: UserPreferences,
    api_key: str,
    model: str = "llama-3.3-70b-versatile",
    max_tokens: int = 1000,
    temperature: float = 0.3,
    timeout: float = 30.0,
) -> RecommendationResult:
    """Full recommendation pipeline. Falls back to deterministic top-k on any failure."""

    if not integration.has_candidates:            # EC-3.2
        return RecommendationResult(
            items=[], source="no_candidates",
            candidate_count=0, filter_count=integration.filter_count,
        )

    candidate_map: dict[str, Restaurant] = {
        r.restaurant_id: r for r in integration.candidates
    }

    t0 = time.monotonic()
    token_usage: dict | None = None

    try:
        raw_text, token_usage = call_groq(
            messages=integration.prompt_payload["messages"],
            api_key=api_key, model=model,
            max_tokens=max_tokens, temperature=temperature, timeout=timeout,
        )
        latency_ms = (time.monotonic() - t0) * 1000

        rankings = _parse_rankings(raw_text, candidate_map)
        if not rankings:
            raise ValueError("empty_rankings")

        items: list[RankedItem] = []
        used_ids: set[str] = set()

        for row in rankings:
            rid = row["restaurant_id"]
            restaurant = candidate_map[rid]
            used_ids.add(rid)
            explanation = row.get("explanation", "").strip()
            if not explanation:                    # EC-4.6
                explanation = _template_explanation(restaurant, prefs)
            items.append(RankedItem(rank=row["rank"], restaurant=restaurant, explanation=explanation))

        # EC-4.7: backfill missing slots
        desired = min(5, len(integration.candidates))
        for r in integration.candidates:
            if len(items) >= desired:
                break
            if r.restaurant_id not in used_ids:
                items.append(RankedItem(
                    rank=len(items) + 1, restaurant=r,
                    explanation=_template_explanation(r, prefs),
                ))
                used_ids.add(r.restaurant_id)

        items.sort(key=lambda x: x.rank)

        return RecommendationResult(
            items=items, source="llm",
            candidate_count=integration.candidate_count,
            filter_count=integration.filter_count,
            latency_ms=latency_ms, token_usage=token_usage,
        )

    except Exception as exc:
        latency_ms = (time.monotonic() - t0) * 1000
        logger.warning("LLM failed (%s: %s); using fallback.", type(exc).__name__, exc)
        return RecommendationResult(
            items=_deterministic_top_k(integration.candidates, prefs),
            source="fallback",
            candidate_count=integration.candidate_count,
            filter_count=integration.filter_count,
            latency_ms=latency_ms, token_usage=token_usage,
        )
