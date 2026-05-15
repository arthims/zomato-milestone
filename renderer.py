"""
phase5_output.renderer
-----------------------
Render a RecommendationResult into human-readable strings.
All display-logic edge cases live here.

Edge cases handled:
  EC-5.1  Missing cost field     → "Cost: Not available"
  EC-5.2  Rating = 0.0           → "No reviews yet"
  EC-5.3  source = "fallback"    → notice banner
  EC-5.4  Very long name         → truncated at display only (80 chars)
"""
from __future__ import annotations

from milestone1.phase4_llm.models import RankedItem, RecommendationResult

_MAX_DISPLAY_NAME = 80


def _truncate(text: str, max_len: int = _MAX_DISPLAY_NAME) -> str:
    """EC-5.4: truncate long names for terminal display."""
    return text if len(text) <= max_len else text[:max_len - 1] + "…"


def _fallback_notice(source: str) -> str:
    """EC-5.3: show notice when AI ranking was unavailable."""
    if source == "fallback":
        return "⚠  AI ranking unavailable — showing top matches by rating.\n"
    return ""


def _render_item_markdown(item: RankedItem) -> str:
    r = item.restaurant
    name = _truncate(r.name)
    cuisines = ", ".join(r.cuisines) if r.cuisines else "N/A"
    return (
        f"### {item.rank}. {name}\n"
        f"- **Cuisine:** {cuisines}\n"
        f"- **Rating:** {r.display_rating}\n"
        f"- **Estimated Cost:** {r.display_cost}\n"
        f"- **Location:** {r.location}\n"
        f"\n> {item.explanation}\n"
    )


def _render_item_plain(item: RankedItem) -> str:
    r = item.restaurant
    name = _truncate(r.name)
    cuisines = ", ".join(r.cuisines) if r.cuisines else "N/A"
    sep = "-" * 50
    return (
        f"{sep}\n"
        f"#{item.rank}  {name}\n"
        f"    Cuisine : {cuisines}\n"
        f"    Rating  : {r.display_rating}\n"
        f"    Cost    : {r.display_cost}\n"
        f"    Location: {r.location}\n"
        f"\n    {item.explanation}\n"
    )


def render_markdown(result: RecommendationResult) -> str:
    """Render result as Markdown (used by Streamlit / API docs)."""
    if result.is_empty:
        from milestone1.phase5_output.empty_states import empty_state_message, EmptyStateKind
        kind = (
            EmptyStateKind.NO_CANDIDATES
            if result.source == "no_candidates"
            else EmptyStateKind.LLM_NO_PICKS
        )
        return empty_state_message(kind)

    lines = ["## 🍽  Restaurant Recommendations\n"]
    notice = _fallback_notice(result.source)
    if notice:
        lines.append(f"_{notice}_\n")

    for item in result.items:
        lines.append(_render_item_markdown(item))

    lines.append(
        f"\n---\n_Source: `{result.source}` · "
        f"{result.candidate_count} candidates · "
        f"{result.latency_ms:.0f} ms_\n"
    )
    return "\n".join(lines)


def render_plain(result: RecommendationResult) -> str:
    """Render result as plain text (used by CLI recommend-run)."""
    if result.is_empty:
        from milestone1.phase5_output.empty_states import empty_state_message, EmptyStateKind
        kind = (
            EmptyStateKind.NO_CANDIDATES
            if result.source == "no_candidates"
            else EmptyStateKind.LLM_NO_PICKS
        )
        return empty_state_message(kind)

    lines = ["=" * 50, "  RESTAURANT RECOMMENDATIONS", "=" * 50]

    notice = _fallback_notice(result.source)
    if notice:
        lines.append(notice)

    for item in result.items:
        lines.append(_render_item_plain(item))

    lines.append("=" * 50)
    lines.append(
        f"Source: {result.source} | "
        f"Candidates: {result.candidate_count} | "
        f"Latency: {result.latency_ms:.0f}ms"
    )
    return "\n".join(lines)
