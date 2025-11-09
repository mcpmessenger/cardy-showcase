"""Grokipedia RAG tool for research queries."""
import logging
from typing import Any, Dict, List, Optional

import requests

from app.config import settings

logger = logging.getLogger(__name__)

DEFAULT_GROKIPEDIA_URL = "https://api.x.ai/v1/grokipedia/search"
DEFAULT_TIMEOUT = 20


def _request_grokipedia(query: str, limit: int = 5) -> Dict[str, Any]:
    """Call the Grokipedia REST endpoint."""
    if not settings.grokipedia_api_key:
        return {
            "error": "Missing Grokipedia API key",
            "note": "Set GROKIPEDIA_API_KEY in the backend environment.",
        }

    base_url = getattr(settings, "grokipedia_api_base_url", DEFAULT_GROKIPEDIA_URL)
    timeout = getattr(settings, "grokipedia_timeout", DEFAULT_TIMEOUT)

    headers = {
        "Authorization": f"Bearer {settings.grokipedia_api_key}",
        "Content-Type": "application/json",
    }

    payload = {"query": query, "limit": limit}

    try:
        response = requests.post(base_url, json=payload, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except requests.HTTPError as http_exc:
        status = http_exc.response.status_code if http_exc.response else "unknown"
        logger.error("Grokipedia API returned HTTP %s: %s", status, http_exc)
        message = http_exc.response.text if http_exc.response else str(http_exc)
        return {
            "error": f"Grokipedia API HTTP {status} error",
            "note": message,
        }
    except Exception as exc:  # pragma: no cover - network call
        logger.error("Grokipedia API request failed: %s", exc)
        return {"error": f"Grokipedia API request failed: {exc}"}


def _extract_sources(data: Any) -> List[Dict[str, Any]]:
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    return []


def grokipedia_search(query: str, limit: int = 5) -> Dict[str, Any]:
    """Search Grokipedia for research information."""
    logger.info("Searching Grokipedia for: %s", query)

    result = _request_grokipedia(query=query, limit=limit)

    if "error" in result:
        return {
            "error": result["error"],
            "content": (
                "Sorry, I couldn't access Grokipedia at this time. "
                "I can still try to answer based on general knowledge if you'd like."
            ),
            "sources": [],
            "note": result.get("note"),
        }

    payload = result.get("data", result)

    # Common Grokipedia response pattern: { "results": [ ... ] }
    results: Optional[List[Dict[str, Any]]] = None
    if isinstance(payload, dict):
        results = payload.get("results") or payload.get("items") or payload.get("data")
        if isinstance(results, dict):
            results = results.get("items")

    entries: List[Dict[str, Any]] = []
    if isinstance(results, list):
        for item in results:
            if not isinstance(item, dict):
                continue
            entries.append(
                {
                    "title": item.get("title") or item.get("heading") or "",
                    "content": item.get("content") or item.get("summary") or item.get("text", ""),
                    "url": item.get("url") or item.get("source"),
                    "score": item.get("score"),
                }
            )

    sources: List[Dict[str, Any]] = []
    if isinstance(payload, dict):
        sources = _extract_sources(payload.get("sources"))

    return {
        "content": entries or payload,
        "sources": sources,
        "query": query,
        "raw": payload,
    }

