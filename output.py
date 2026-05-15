"""
phase3_integration.output
--------------------------
IntegrationOutput bundles the candidate list and prompt payload into
a single object consumed by Phase 4.
"""
from __future__ import annotations

from dataclasses import dataclass

from milestone1.phase1_ingestion.models import Restaurant
from milestone1.phase2_preferences.models import UserPreferences
from milestone1.phase3_integration.filter import filter_and_rank
from milestone1.phase3_integration.prompt import build_prompt_payload


@dataclass
class IntegrationOutput:
    candidates: list[Restaurant]
    prompt_payload: dict          # {"has_candidates": bool, "messages": [...]}
    filter_count: int             # total restaurants before cap
    candidate_count: int          # after cap

    @property
    def has_candidates(self) -> bool:
        return bool(self.candidates)


def build_integration_output(
    restaurants: list[Restaurant],
    prefs: UserPreferences,
    candidate_cap: int = 20,
) -> IntegrationOutput:
    """
    Run filter → rank → prompt-build in one call.
    The single entry point used by Phase 4 and Phase 6 API.
    """
    candidates = filter_and_rank(restaurants, prefs, candidate_cap)
    prompt_payload = build_prompt_payload(candidates, prefs)

    return IntegrationOutput(
        candidates=candidates,
        prompt_payload=prompt_payload,
        filter_count=len(restaurants),
        candidate_count=len(candidates),
    )
