"""
phase4_llm.client
-----------------
Thin Groq HTTP client (OpenAI-compatible API) using stdlib urllib.
In the real project, httpx is available via pyproject.toml.

Edge cases handled:
  EC-4.1  Malformed JSON        → strip fences, retry parse, fallback
  EC-4.2  Hallucinated IDs      → validated against candidate set
  EC-4.3  Fewer items than asked → accepted as partial list
  EC-4.4  Rate limit (429)      → exponential backoff, 2 retries
  EC-4.5  Timeout               → fallback triggered
  EC-4.6  Empty explanation     → template substitution
  EC-4.7  Duplicate IDs         → deduplicated, backfilled
"""
from __future__ import annotations

import json
import logging
import re
import time
import urllib.error
import urllib.request
from typing import Optional

from milestone1.phase1_ingestion.models import Restaurant

logger = logging.getLogger(__name__)

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
_MAX_RETRIES = 2
_BACKOFF_BASE = 1.5


class TimeoutError(OSError):
    """Raised when an HTTP request times out."""


class HTTPStatusError(OSError):
    """Raised on non-2xx HTTP responses."""
    def __init__(self, status: int, message: str):
        self.status_code = status
        super().__init__(f"HTTP {status}: {message}")


def _strip_fences(text: str) -> str:
    """EC-4.1: Remove markdown code fences that wrap JSON."""
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def _parse_rankings(
    raw_text: str,
    candidate_map: dict[str, Restaurant],
) -> list[dict]:
    """Parse and validate LLM JSON response. Handles EC-4.1, EC-4.2, EC-4.3, EC-4.7."""
    text = _strip_fences(raw_text)

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group())
            except json.JSONDecodeError:
                logger.warning("LLM returned unparseable JSON; using fallback.")
                return []
        else:
            logger.warning("No JSON object found in LLM response; using fallback.")
            return []

    rankings_raw = data.get("rankings", [])
    if not isinstance(rankings_raw, list):
        return []

    seen_ids: set[str] = set()
    clean: list[dict] = []

    for item in rankings_raw:
        if not isinstance(item, dict):
            continue
        rid = str(item.get("restaurant_id", "")).strip()
        if rid not in candidate_map:           # EC-4.2
            logger.warning("Hallucinated restaurant_id '%s' discarded.", rid)
            continue
        if rid in seen_ids:                    # EC-4.7
            logger.warning("Duplicate restaurant_id '%s' discarded.", rid)
            continue
        seen_ids.add(rid)
        clean.append({
            "restaurant_id": rid,
            "rank": int(item.get("rank", len(clean) + 1)),
            "explanation": str(item.get("explanation", "")).strip(),
        })

    return clean


def call_groq(
    messages: list[dict],
    api_key: str,
    model: str,
    max_tokens: int = 1000,
    temperature: float = 0.3,
    timeout: float = 30.0,
) -> tuple[str, dict]:
    """Call Groq chat completions. Returns (response_text, usage_dict)."""
    payload = json.dumps({
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }).encode("utf-8")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    for attempt in range(_MAX_RETRIES + 1):
        try:
            req = urllib.request.Request(
                GROQ_API_URL, data=payload, headers=headers, method="POST"
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                body = json.loads(resp.read().decode("utf-8"))
                text = body["choices"][0]["message"]["content"]
                usage = body.get("usage", {})
                return text, usage

        except urllib.error.HTTPError as exc:
            if exc.code == 429:                # EC-4.4 rate limit
                wait = _BACKOFF_BASE ** (attempt + 1)
                logger.warning("Rate limit (attempt %d). Waiting %.1fs.", attempt + 1, wait)
                if attempt < _MAX_RETRIES:
                    time.sleep(wait)
                    continue
            raise HTTPStatusError(exc.code, str(exc.reason)) from exc

        except TimeoutError:
            logger.warning("Groq timeout on attempt %d.", attempt + 1)
            if attempt >= _MAX_RETRIES:
                raise
            time.sleep(_BACKOFF_BASE ** attempt)

    raise RuntimeError("Unreachable")
