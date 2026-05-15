"""
phase1_ingestion.models
-----------------------
Canonical Restaurant dataclass — the internal representation used by all
subsequent phases. Nothing outside this package should depend on raw
HuggingFace row dicts.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


# Budget bands aligned with dataset-contract.md
BUDGET_LOW = "low"
BUDGET_MEDIUM = "medium"
BUDGET_HIGH = "high"
BUDGET_UNKNOWN = "unknown"

VALID_BUDGETS = {BUDGET_LOW, BUDGET_MEDIUM, BUDGET_HIGH, BUDGET_UNKNOWN}


@dataclass(frozen=True)
class Restaurant:
    """
    Canonical representation of one restaurant row.

    Sentinel values for missing data (per dataset-contract.md):
      rating   → 0.0   (display as "No reviews yet")
      cuisines → []
      cost_raw → "unknown"
      votes    → 0
    """
    # Required identity fields
    restaurant_id: str          # derived: slugify(name + location)
    name: str

    # Location
    location: str               # city / area

    # Cuisine — always a list, never None
    cuisines: tuple[str, ...]   # immutable for hashing

    # Cost
    cost_raw: str               # original string e.g. "₹500"
    budget: str                 # low | medium | high | unknown

    # Quality signals
    rating: float               # 0.0–5.0; 0.0 = no reviews
    votes: int                  # 0 = unknown

    # Optional metadata
    restaurant_type: str = ""
    listed_type: str = ""

    def to_dict(self) -> dict:
        """Serialise to a plain dict for JSON / prompt use."""
        return {
            "restaurant_id": self.restaurant_id,
            "name": self.name,
            "location": self.location,
            "cuisines": list(self.cuisines),
            "cost_raw": self.cost_raw,
            "budget": self.budget,
            "rating": self.rating,
            "votes": self.votes,
            "restaurant_type": self.restaurant_type,
            "listed_type": self.listed_type,
        }

    @property
    def display_rating(self) -> str:
        """EC-5.2: zero rating shown as 'No reviews yet'."""
        if self.rating == 0.0:
            return "No reviews yet"
        return f"{self.rating:.1f} ★"

    @property
    def display_cost(self) -> str:
        """EC-5.1: unknown cost shown gracefully."""
        if self.cost_raw in ("", "unknown"):
            return "Cost: Not available"
        return self.cost_raw
