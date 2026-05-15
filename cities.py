"""
phase2_preferences.cities
--------------------------
Helpers for building and querying the allowed-cities corpus from the
loaded restaurant list.
"""
from __future__ import annotations

from milestone1.phase1_ingestion.models import Restaurant


def allowed_cities_from_restaurants(restaurants: list[Restaurant]) -> set[str]:
    """Return the set of all unique location strings in the corpus."""
    return {r.location for r in restaurants}
