"""
phase5_output.telemetry
-----------------------
Lightweight stderr telemetry — logs counts, latency, token usage.
Never logs raw user input or PII (EC-9.3).
"""
from __future__ import annotations

import json
import logging
import sys
import time

from milestone1.phase4_llm.models import RecommendationResult

logger = logging.getLogger(__name__)


def emit_telemetry(result: RecommendationResult) -> None:
    """
    Write a single-line JSON telemetry record to stderr.
    Fields: source, candidate_count, filter_count, item_count,
            latency_ms, tokens_prompt, tokens_completion.
    No user preferences or restaurant names are logged (EC-9.3).
    """
    usage = result.token_usage or {}
    record = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "source": result.source,
        "filter_count": result.filter_count,
        "candidate_count": result.candidate_count,
        "item_count": len(result.items),
        "latency_ms": round(result.latency_ms, 1),
        "tokens_prompt": usage.get("prompt_tokens"),
        "tokens_completion": usage.get("completion_tokens"),
    }
    print(json.dumps(record), file=sys.stderr)
    logger.debug("Telemetry: %s", record)
