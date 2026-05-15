"""
phase5_output.empty_states
---------------------------
Distinct copy for each empty-state kind (EC-5.3, EC-7.4).
The UI and CLI both import from here so messaging stays consistent.
"""
from __future__ import annotations

from enum import Enum


class EmptyStateKind(str, Enum):
    NO_CANDIDATES = "no_candidates"   # hard filters matched nothing
    LLM_NO_PICKS  = "llm_no_picks"   # LLM returned empty rankings
    LLM_FALLBACK  = "llm_fallback"   # LLM failed; fallback used


_MESSAGES: dict[EmptyStateKind, str] = {
    EmptyStateKind.NO_CANDIDATES: (
        "No restaurants match your filters.\n"
        "Try broadening your search — widen the budget, lower the minimum rating, "
        "or select fewer cuisines."
    ),
    EmptyStateKind.LLM_NO_PICKS: (
        "The AI could not find a strong match from the available restaurants.\n"
        "Try adjusting your preferences or adding more cuisines."
    ),
    EmptyStateKind.LLM_FALLBACK: (
        "AI ranking is temporarily unavailable — showing top matches by rating instead."
    ),
}


def empty_state_message(kind: EmptyStateKind) -> str:
    """Return the user-facing empty-state copy for a given kind."""
    return _MESSAGES.get(kind, "No results found.")
