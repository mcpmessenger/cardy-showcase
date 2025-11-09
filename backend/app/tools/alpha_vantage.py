"""Alpha Vantage market data helpers exposed as LLM tools."""
from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional, Tuple

import requests

from app.config import settings

logger = logging.getLogger(__name__)

ALPHA_VANTAGE_BASE_URL = "https://www.alphavantage.co/query"
DEFAULT_TIMEOUT = 20
QUOTE_CACHE_TTL = 30  # seconds
INTRADAY_CACHE_TTL = 60  # seconds

_cache: Dict[str, Tuple[float, Dict[str, Any]]] = {}


def _call_alpha_vantage_http(function: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Call the Alpha Vantage REST API directly."""
    api_key = settings.alpha_vantage_api_key or "demo"
    query_params = {
        "function": function,
        "apikey": api_key,
        **params,
    }

    timeout = getattr(settings, "alpha_vantage_timeout", DEFAULT_TIMEOUT)

    try:
        response = requests.get(ALPHA_VANTAGE_BASE_URL, params=query_params, timeout=timeout)
        response.raise_for_status()
        payload = response.json()
        if "Error Message" in payload:
            raise ValueError(payload["Error Message"])
        if "Note" in payload:
            logger.warning("Alpha Vantage throttled request: %s", payload["Note"])
        return payload
    except Exception as exc:  # pragma: no cover - network call
        logger.error("Alpha Vantage HTTP call failed: %s", exc)
        return {"error": f"Alpha Vantage HTTP call failed: {exc}"}


def _normalize_quote(payload: Dict[str, Any], symbol: str) -> Optional[Dict[str, Any]]:
    quote = payload.get("Global Quote") if isinstance(payload, dict) else None
    if not quote:
        return None

    def _to_float(value: Any) -> Optional[float]:
        try:
            return float(str(value).replace(",", ""))
        except (TypeError, ValueError):
            return None

    return {
        "symbol": quote.get("01. symbol", symbol),
        "price": _to_float(quote.get("05. price")) or _to_float(quote.get("05. Price")),
        "open": _to_float(quote.get("02. open")),
        "high": _to_float(quote.get("03. high")),
        "low": _to_float(quote.get("04. low")),
        "previous_close": _to_float(quote.get("08. previous close")),
        "change": _to_float(quote.get("09. change")),
        "change_percent": quote.get("10. change percent"),
        "latest_trading_day": quote.get("07. latest trading day"),
        "volume": _to_float(quote.get("06. volume")),
    }


def _normalize_intraday(payload: Dict[str, Any], interval: str) -> Optional[Dict[str, Any]]:
    if not isinstance(payload, dict):
        return None

    metadata = payload.get("Meta Data", {})
    series_key = next((k for k in payload.keys() if k.lower().startswith("time series")), None)
    series_data = payload.get(series_key) if series_key else None
    if not series_data:
        return None

    def _to_float(value: Any) -> Optional[float]:
        try:
            return float(str(value).replace(",", ""))
        except (TypeError, ValueError):
            return None

    points: List[Dict[str, Any]] = []
    for timestamp, values in series_data.items():
        points.append(
            {
                "timestamp": timestamp,
                "open": _to_float(values.get("1. open")),
                "high": _to_float(values.get("2. high")),
                "low": _to_float(values.get("3. low")),
                "close": _to_float(values.get("4. close")),
                "volume": _to_float(values.get("5. volume")),
            }
        )

    points.sort(key=lambda item: item["timestamp"], reverse=True)

    return {
        "interval": metadata.get("4. Interval", interval),
        "last_refreshed": metadata.get("3. Last Refreshed"),
        "series": points,
    }


def _cached_fetch(cache_key: str, ttl: int, fetcher) -> Tuple[Dict[str, Any], bool]:
    """Fetch data with a simple in-memory cache."""
    now = time.time()
    cached = _cache.get(cache_key)

    if cached:
        timestamp, payload = cached
        if now - timestamp < ttl:
            return payload, True

    payload = fetcher()
    if isinstance(payload, dict) and "error" not in payload:
        _cache[cache_key] = (now, payload)
    return payload, False


def alpha_vantage_market_data(
    symbol: str,
    data_type: str = "quote",
    interval: str = "5min",
) -> Dict[str, Any]:
    """Fetch market data from Alpha Vantage via REST API with caching."""
    if not symbol:
        return {"error": "Symbol is required"}

    normalized_type = (data_type or "quote").strip().lower()
    if normalized_type not in {"quote", "intraday"}:
        return {"error": f"Unsupported data_type '{data_type}'. Use 'quote' or 'intraday'."}

    if normalized_type == "quote":
        cache_key = f"quote:{symbol.upper()}"
        params: Dict[str, Any] = {"symbol": symbol.upper()}
        result, cached = _cached_fetch(
            cache_key,
            QUOTE_CACHE_TTL,
            lambda: _call_alpha_vantage_http("GLOBAL_QUOTE", params),
        )
        intraday_info: Optional[Dict[str, Any]] = None
        intraday_cache_hit: Optional[bool] = None
        intraday_raw: Optional[Dict[str, Any]] = None
        if "error" not in result:
            intraday_result, intraday_cache_hit = _cached_fetch(
                f"intraday:{symbol.upper()}:{interval}",
                INTRADAY_CACHE_TTL,
                lambda: _call_alpha_vantage_http(
                    "TIME_SERIES_INTRADAY",
                    {"symbol": symbol.upper(), "interval": interval},
                ),
            )
            if "error" not in intraday_result:
                intraday_payload = intraday_result.get("data", intraday_result)
                intraday_raw = intraday_payload
                intraday_info = _normalize_intraday(intraday_payload, interval)
    else:
        cache_key = f"intraday:{symbol.upper()}:{interval}"
        params = {"symbol": symbol.upper(), "interval": interval}
        result, cached = _cached_fetch(
            cache_key,
            INTRADAY_CACHE_TTL,
            lambda: _call_alpha_vantage_http("TIME_SERIES_INTRADAY", params),
        )

    if "error" in result:
        return {
            "error": result["error"],
            "note": "Alpha Vantage API call failed. Check API key, quota, or network connectivity.",
        }

    payload = result.get("data", result)

    if normalized_type == "quote":
        quote = _normalize_quote(payload, symbol)
        if not quote:
            return {
                "error": "Could not parse Alpha Vantage quote response",
                "raw": payload,
            }
        response: Dict[str, Any] = {
            "source": "alpha_vantage_rest",
            "symbol": quote["symbol"],
            "data_type": "quote",
            "quote": quote,
            "cache_hit": cached,
            "raw": payload,
        }
        if intraday_info:
            response.update(
                {
                    "interval": intraday_info["interval"],
                    "last_refreshed": intraday_info["last_refreshed"],
                    "series": intraday_info["series"],
                    "intraday_cache_hit": intraday_cache_hit,
                    "intraday_raw": intraday_raw,
                }
            )
        return response

    intraday = _normalize_intraday(payload, interval)
    if not intraday:
        return {
            "error": "Could not parse Alpha Vantage intraday response",
            "raw": payload,
        }

    return {
        "source": "alpha_vantage_rest",
        "symbol": symbol,
        "data_type": "intraday",
        "interval": intraday["interval"],
        "last_refreshed": intraday["last_refreshed"],
        "series": intraday["series"],
        "cache_hit": cached,
        "raw": payload,
    }


