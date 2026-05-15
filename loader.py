"""
phase1_ingestion.loader
-----------------------
Load the Zomato HuggingFace dataset, normalize rows, deduplicate, and
return a typed in-memory list of Restaurant objects.

Edge cases handled:
  EC-1.3  Duplicate (name, location) → keep highest rating
  EC-1.4  Hub unavailable            → DatasetUnavailableError
  EC-1.5  Empty corpus               → EmptyCorpusError
  EC-1.6  load_limit cap             → honoured via iter_restaurants
"""
from __future__ import annotations

import logging
import warnings
from collections.abc import Iterator
from typing import Optional

from milestone1.phase1_ingestion.models import Restaurant
from milestone1.phase1_ingestion.normalizer import normalize_row

logger = logging.getLogger(__name__)


# ── custom errors ──────────────────────────────────────────────────────────

class DatasetUnavailableError(RuntimeError):
    """Raised when the HuggingFace dataset cannot be loaded."""


class EmptyCorpusError(RuntimeError):
    """Raised when normalization produces zero usable rows."""


# ── internal helpers ───────────────────────────────────────────────────────

def _dedup(restaurants: list[Restaurant]) -> list[Restaurant]:
    """
    EC-1.3: deduplicate on (name, location), keep highest rating.
    Preserves insertion order of first-seen keys (Python 3.7+ dict).
    """
    best: dict[tuple[str, str], Restaurant] = {}
    for r in restaurants:
        key = (r.name.lower(), r.location.lower())
        if key not in best or r.rating > best[key].rating:
            best[key] = r
    removed = len(restaurants) - len(best)
    if removed:
        logger.info("Deduplication removed %d duplicate rows.", removed)
    return list(best.values())


def _stream_raw_rows(
    dataset_name: str,
    revision: str,
    hf_token: Optional[str],
    load_limit: int,
) -> Iterator[dict]:
    """
    Stream raw rows from HuggingFace Hub.
    Raises DatasetUnavailableError on network or auth errors (EC-1.4).
    """
    try:
        from datasets import load_dataset  # type: ignore
    except ImportError as exc:
        raise DatasetUnavailableError(
            "The 'datasets' package is not installed. "
            "Run: pip install datasets"
        ) from exc

    try:
        kwargs: dict = {
            "split": "train",
            "streaming": True,
        }
        if hf_token:
            kwargs["token"] = hf_token

        ds = load_dataset(dataset_name, revision=revision, **kwargs)

        count = 0
        for row in ds:
            yield dict(row)
            count += 1
            if load_limit > 0 and count >= load_limit:
                logger.info("load_limit=%d reached, stopping stream.", load_limit)
                break

    except DatasetUnavailableError:
        raise
    except Exception as exc:
        raise DatasetUnavailableError(
            f"Failed to load dataset '{dataset_name}': {exc}\n"
            "Check your internet connection and HF_TOKEN if the dataset is private."
        ) from exc


# ── public API ─────────────────────────────────────────────────────────────

def iter_restaurants(
    dataset_name: str = "ManikaSaini/zomato-restaurant-recommendation",
    revision: str = "main",
    hf_token: Optional[str] = None,
    load_limit: int = 5_000,
) -> Iterator[Restaurant]:
    """
    Yield normalized Restaurant objects one at a time (streaming, low memory).
    Skips malformed rows with a warning.
    Does NOT deduplicate — use load_restaurants() for that.
    """
    skipped = 0
    yielded = 0
    for raw in _stream_raw_rows(dataset_name, revision, hf_token, load_limit):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            restaurant = normalize_row(raw)
        for w in caught:
            logger.debug("Row warning: %s", w.message)

        if restaurant is None:
            skipped += 1
            continue

        yielded += 1
        yield restaurant

    logger.info(
        "iter_restaurants: yielded=%d skipped=%d", yielded, skipped
    )


def load_restaurants(
    dataset_name: str = "ManikaSaini/zomato-restaurant-recommendation",
    revision: str = "main",
    hf_token: Optional[str] = None,
    load_limit: int = 5_000,
) -> list[Restaurant]:
    """
    Load, normalize, and deduplicate the full dataset into memory.

    Raises:
        DatasetUnavailableError  — EC-1.4: Hub unreachable
        EmptyCorpusError         — EC-1.5: all rows failed normalization
    """
    raw_list = list(
        iter_restaurants(dataset_name, revision, hf_token, load_limit)
    )

    if not raw_list:
        raise EmptyCorpusError(
            "Dataset loaded but produced zero valid restaurants after normalization. "
            "Check the dataset schema and normalizer mappings."
        )

    deduped = _dedup(raw_list)
    logger.info(
        "load_restaurants: total=%d after_dedup=%d", len(raw_list), len(deduped)
    )
    return deduped


def get_unique_cities(restaurants: list[Restaurant]) -> list[str]:
    """Return sorted list of unique city/location names in the corpus."""
    return sorted({r.location for r in restaurants})
