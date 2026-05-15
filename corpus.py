"""phase6_api.corpus — lazy-loaded, cached restaurant corpus."""
from __future__ import annotations

import logging
import threading
from typing import Optional

from milestone1.phase0.settings import Settings
from milestone1.phase1_ingestion.loader import load_restaurants, get_unique_cities
from milestone1.phase1_ingestion.models import Restaurant

logger = logging.getLogger(__name__)

_lock = threading.Lock()
_restaurants: Optional[list[Restaurant]] = None
_cities: Optional[list[str]] = None


def get_corpus(settings: Settings) -> list[Restaurant]:
    """Return the cached corpus, loading it on first call (thread-safe)."""
    global _restaurants, _cities
    if _restaurants is not None:
        return _restaurants
    with _lock:
        if _restaurants is not None:
            return _restaurants
        logger.info("Loading corpus (limit=%d)…", settings.load_limit)
        _restaurants = load_restaurants(
            dataset_name=settings.hf_dataset_name,
            revision=settings.hf_dataset_revision,
            hf_token=settings.hf_token or None,
            load_limit=settings.load_limit,
        )
        _cities = get_unique_cities(_restaurants)
        logger.info("Corpus ready: %d restaurants, %d cities.", len(_restaurants), len(_cities))
    return _restaurants


def get_cities(settings: Settings) -> list[str]:
    """Return sorted city list, loading corpus if needed."""
    global _cities
    if _cities is None:
        get_corpus(settings)
    return _cities or []
