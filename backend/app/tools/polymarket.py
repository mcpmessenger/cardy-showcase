"""Polymarket prediction market helpers exposed as LLM tools."""
from __future__ import annotations

import json
import logging
import time
from typing import Any, Callable, Dict, List, Optional, Tuple

import requests

from app.config import settings

logger = logging.getLogger(__name__)

GAMMA_API_BASE_URL = "https://gamma-api.polymarket.com"
CLOB_API_BASE_URL = "https://clob.polymarket.com"
DEFAULT_TIMEOUT = 20
SEARCH_CACHE_TTL = 30
DETAIL_CACHE_TTL = 60
MAX_FALLBACK_RESULTS = 200

CacheValue = Tuple[float, Any]
_cache: Dict[str, CacheValue] = {}


def _http_get(
    base_url: str,
    path: str,
    params: Optional[Dict[str, Any]] = None,
    extra_headers: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    url = f"{base_url.rstrip('/')}/{path.lstrip('/')}"
    headers: Dict[str, str] = {}

    if extra_headers:
        headers.update(extra_headers)

    api_key = settings.polymarket_api_key
    if api_key:
        headers.setdefault("X-API-Key", api_key)

    timeout = getattr(settings, "polymarket_timeout", DEFAULT_TIMEOUT)

    try:
        response = requests.get(url, params=params, headers=headers, timeout=timeout)
        response.raise_for_status()

        if "application/json" in response.headers.get("Content-Type", ""):
            return response.json()

        return {"raw": response.text}
    except requests.HTTPError as exc:  # pragma: no cover - network call
        status = exc.response.status_code if exc.response else "unknown"
        message = exc.response.text if exc.response else str(exc)
        logger.error("Polymarket HTTP %s error for %s: %s", status, url, message)
        return {"error": f"Polymarket HTTP {status} error: {message}"}
    except Exception as exc:  # pragma: no cover - network call
        logger.error("Polymarket HTTP call failed for %s: %s", url, exc)
        return {"error": f"Polymarket HTTP call failed: {exc}"}


def _gamma_get(path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return _http_get(GAMMA_API_BASE_URL, path, params=params)


def _clob_get(path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return _http_get(CLOB_API_BASE_URL, path, params=params)


def _cached_fetch(cache_key: str, ttl: int, fetcher: Callable[[], Any]) -> Tuple[Any, bool]:
    now = time.time()
    cached = _cache.get(cache_key)

    if cached:
        timestamp, payload = cached
        if now - timestamp < ttl:
            return payload, True

    payload = fetcher()
    if not _is_api_error(payload):
        _cache[cache_key] = (now, payload)
    return payload, False


def _is_api_error(payload: Any) -> bool:
    if isinstance(payload, dict):
        if "error" in payload:
            return True
        if payload.get("type") == "validation error":
            return True
    return False


def _parse_float(value: Any) -> Optional[float]:
    if value in (None, "", "null"):
        return None
    if isinstance(value, (int, float)):
        try:
            return float(value)
        except (TypeError, ValueError):
            return None
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return None
    return None


def _parse_json_list(value: Any) -> List[Any]:
    if isinstance(value, list):
        return value

    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return parsed
        except json.JSONDecodeError:
            return []

    return []


def _compute_status(entity: Dict[str, Any]) -> str:
    if entity.get("closed"):
        return "closed"
    if entity.get("active"):
        return "active"
    if entity.get("archived"):
        return "archived"
    return "unknown"


def _normalize_market(market: Dict[str, Any]) -> Dict[str, Any]:
    slug = market.get("slug") or market.get("market_slug")
    question = market.get("question") or market.get("title")
    description = market.get("description")

    outcomes = _parse_json_list(market.get("outcomes"))
    prices = _parse_json_list(market.get("outcomePrices"))
    token_ids = _parse_json_list(market.get("clobTokenIds"))

    normalized_outcomes: List[Dict[str, Any]] = []

    for idx, name in enumerate(outcomes):
        price = _parse_float(prices[idx]) if idx < len(prices) else None
        token_id = token_ids[idx] if idx < len(token_ids) else None
        normalized_outcomes.append(
            {
                "id": token_id,
                "name": name,
                "probability": price,
                "last_price": _parse_float(market.get("lastTradePrice")),
                "best_bid": _parse_float(market.get("bestBid")),
                "best_ask": _parse_float(market.get("bestAsk")),
            }
        )

    if not normalized_outcomes and isinstance(market.get("tokens"), list):
        for token in market["tokens"]:
            normalized_outcomes.append(
                {
                    "id": token.get("token_id") or token.get("tokenId"),
                    "name": token.get("outcome"),
                    "probability": _parse_float(token.get("price")),
                    "last_price": _parse_float(token.get("price")),
                    "best_bid": None,
                    "best_ask": None,
                }
            )

    return {
        "type": "market",
        "id": slug or market.get("id") or market.get("question_id"),
        "market_id": market.get("id"),
        "slug": slug,
        "question": question,
        "description": description,
        "status": _compute_status(market),
        "liquidity": _parse_float(
            market.get("liquidity")
            or market.get("liquidityNum")
            or market.get("liquidity_num")
        ),
        "volume": _parse_float(
            market.get("volume")
            or market.get("volumeNum")
            or market.get("volume_num")
        ),
        "last_trade_price": _parse_float(market.get("lastTradePrice")),
        "best_bid": _parse_float(market.get("bestBid")),
        "best_ask": _parse_float(market.get("bestAsk")),
        "close_time": market.get("endDate") or market.get("end_date_iso"),
        "neg_risk": market.get("negRisk"),
        "group": market.get("groupItemTitle"),
        "outcomes": normalized_outcomes,
        "raw": market,
    }


def _normalize_event(event: Dict[str, Any], limit_markets: Optional[int] = None) -> Dict[str, Any]:
    markets = event.get("markets") or []

    if limit_markets is not None:
        markets = markets[:limit_markets]

    normalized_markets = [_normalize_market(market) for market in markets]

    default_outcomes: List[Dict[str, Any]] = []
    for market in normalized_markets:
        if market["outcomes"]:
            default_outcomes = market["outcomes"]
            break

    return {
        "type": "event",
        "id": event.get("slug") or event.get("id"),
        "event_id": event.get("id"),
        "slug": event.get("slug"),
        "title": event.get("title"),
        "question": event.get("title") or event.get("question"),
        "description": event.get("description"),
        "status": _compute_status(event),
        "liquidity": _parse_float(event.get("liquidity")),
        "volume": _parse_float(event.get("volume")),
        "open_interest": _parse_float(event.get("openInterest")),
        "close_time": event.get("endDate"),
        "tags": event.get("tags"),
        "outcomes": default_outcomes,
        "markets": normalized_markets,
        "raw": event,
    }


def _gamma_search(query: str, limit: int) -> Tuple[List[Dict[str, Any]], bool, Dict[str, Any]]:
    params = {
        "q": query,
        "type": "events",
        "limit_per_type": max(1, min(limit, 20)),
        "optimized": "true",
        "search_tags": "true",
        "search_profiles": "true",
        "cache": "true",
    }

    cache_key = f"gamma-search:{query}:{params['limit_per_type']}"

    payload, cached = _cached_fetch(cache_key, SEARCH_CACHE_TTL, lambda: _gamma_get("public-search", params))

    if _is_api_error(payload):
        return [], cached, payload if isinstance(payload, dict) else {"error": "Unknown gamma error"}

    events = []
    if isinstance(payload, dict):
        events = payload.get("events") or []

    normalized = [_normalize_event(event, limit_markets=limit) for event in events]
    return normalized, cached, payload


def _fallback_clob_search(query: str, limit: int) -> Tuple[List[Dict[str, Any]], bool, Dict[str, Any]]:
    cache_key = "clob:markets:index"
    payload, cached = _cached_fetch(cache_key, DETAIL_CACHE_TTL, lambda: _clob_get("markets"))

    if _is_api_error(payload):
        return [], cached, payload if isinstance(payload, dict) else {"error": "Unknown CLOB error"}

    markets: List[Dict[str, Any]] = []

    if isinstance(payload, dict):
        markets = payload.get("data") or []
    elif isinstance(payload, list):
        markets = payload

    query_lower = query.lower()
    filtered: List[Dict[str, Any]] = []

    for market in markets:
        haystack = " ".join(
            part
            for part in [
                str(market.get("question") or ""),
                str(market.get("description") or ""),
                str(market.get("market_slug") or ""),
            ]
        ).lower()

        if query_lower in haystack:
            filtered.append(market)
            if len(filtered) >= MAX_FALLBACK_RESULTS:
                break

    normalized = [_normalize_market(market) for market in filtered[:limit]]
    return normalized, cached, payload


def _search_markets(query: str, limit: int) -> Dict[str, Any]:
    gamma_results, gamma_cached, gamma_raw = _gamma_search(query, limit)

    if gamma_results:
        return {
            "source": "polymarket_gamma",
            "query": query,
            "results": gamma_results,
            "cache_hit": gamma_cached,
            "raw": gamma_raw,
        }

    logger.warning("Polymarket gamma search returned no results; falling back to CLOB search for '%s'", query)
    clob_results, clob_cached, clob_raw = _fallback_clob_search(query, limit)

    if clob_results:
        return {
            "source": "polymarket_clob",
            "query": query,
            "results": clob_results,
            "cache_hit": clob_cached,
            "raw": clob_raw,
        }

    return {
        "source": "polymarket_gamma",
        "query": query,
        "results": [],
        "cache_hit": gamma_cached,
        "raw": gamma_raw,
        "error": "No Polymarket markets matched the query.",
    }


def _event_detail_response(event_payload: Dict[str, Any], cache_hit: bool, source: str) -> Dict[str, Any]:
    normalized = _normalize_event(event_payload)
    return {
        "source": source,
        "type": "event",
        "cache_hit": cache_hit,
        **normalized,
    }


def _market_detail_response(market_payload: Dict[str, Any], cache_hit: bool, source: str) -> Dict[str, Any]:
    normalized = _normalize_market(market_payload)
    return {
        "source": source,
        "type": "market",
        "cache_hit": cache_hit,
        **normalized,
    }


def _gamma_detail_attempts(identifier: str) -> List[Tuple[str, str]]:
    attempts: List[Tuple[str, str]] = []

    # Prefer event slugs/ids for richer context
    attempts.append(("event_slug", f"events/slug/{identifier}"))
    if identifier.isdigit():
        attempts.append(("event_id", f"events/{identifier}"))

    attempts.append(("market_slug", f"markets/slug/{identifier}"))
    if identifier.isdigit():
        attempts.append(("market_id", f"markets/{identifier}"))

    return attempts


def _fallback_detail_from_clob(identifier: str) -> Optional[Dict[str, Any]]:
    cache_key = "clob:markets:index"
    payload, cached = _cached_fetch(cache_key, DETAIL_CACHE_TTL, lambda: _clob_get("markets"))

    if _is_api_error(payload):
        return None

    markets: List[Dict[str, Any]] = []
    if isinstance(payload, dict):
        markets = payload.get("data") or []
    elif isinstance(payload, list):
        markets = payload

    for market in markets:
        if identifier in {
            str(market.get("market_slug") or ""),
            str(market.get("question_id") or ""),
            str(market.get("condition_id") or ""),
        }:
            normalized = _normalize_market(market)
            return {
                "source": "polymarket_clob",
                "type": "market",
                "cache_hit": cached,
                **normalized,
            }

    return None


def _fetch_market_details(identifier: str) -> Dict[str, Any]:
    identifier = identifier.strip()
    if not identifier:
        return {"error": "market_id cannot be empty"}

    attempts = _gamma_detail_attempts(identifier)
    tried_paths: set[str] = set()

    for label, path in attempts:
        if path in tried_paths:
            continue
        tried_paths.add(path)

        cache_key = f"gamma-detail:{label}:{identifier}"
        payload, cached = _cached_fetch(cache_key, DETAIL_CACHE_TTL, lambda path=path: _gamma_get(path))

        if _is_api_error(payload):
            continue

        if label.startswith("event"):
            return _event_detail_response(payload, cached, "polymarket_gamma")

        if label.startswith("market"):
            return _market_detail_response(payload, cached, "polymarket_gamma")

    fallback = _fallback_detail_from_clob(identifier)
    if fallback:
        return fallback

    return {
        "error": "Polymarket market not found",
        "note": (
            "Tried accessing Polymarket gamma (events/markets) and CLOB indexes but "
            "did not find a matching identifier."
        ),
        "identifier": identifier,
    }


def polymarket_market_data(
    query: Optional[str] = None,
    market_id: Optional[str] = None,
    limit: int = 5,
) -> Dict[str, Any]:
    """Fetch prediction market data from Polymarket via gamma API with CLOB fallback."""
    if not query and not market_id:
        return {"error": "Provide either a query or market_id"}

    limit = max(1, min(limit, 20))

    if market_id:
        return _fetch_market_details(str(market_id))

    search_response = _search_markets(query, limit)

    if search_response.get("results"):
        return search_response

    return {
        "error": search_response.get("error") or "No Polymarket markets matched the query.",
        "query": query,
        "source": search_response.get("source"),
        "cache_hit": search_response.get("cache_hit"),
        "raw": search_response.get("raw"),
    }

