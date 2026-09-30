"""
YantraX Real-time Market Data Pipeline v1.0
============================================
Unified, low-latency Alpaca market data pipeline with caching and rate-limit awareness.

Source:
  1. Alpaca Markets (live quotes)
  2. In-memory cache (last-known-good)

Design principles:
  - Never block: every call returns within timeout or falls back
  - Budget-friendly: Perplexity calls NEVER happen here (only in DebateEngine)
  - Aggressive caching: 15s for quotes, 5m for fundamentals, 1h for sector data
  - Structured output: consistent schema regardless of provider
"""

import os
import logging
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import requests


logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────
# Cache
# ─────────────────────────────────────────────────────────────
class _TTLCache:
    """Thread-safe TTL cache"""
    def __init__(self):
        self._store: Dict[str, Tuple[Any, float]] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            entry = self._store.get(key)
            if entry and time.time() < entry[1]:
                return entry[0]
            return None

    def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        with self._lock:
            self._store[key] = (value, time.time() + ttl_seconds)

    def clear_expired(self) -> None:
        now = time.time()
        with self._lock:
            expired = [k for k, (_, exp) in self._store.items() if now >= exp]
            for k in expired:
                del self._store[k]


# ─────────────────────────────────────────────────────────────
# Pipeline
# ─────────────────────────────────────────────────────────────
class RealtimeMarketPipeline:
    """
    Real-time market data pipeline using Alpaca and smart caching.
    All methods are synchronous and safe to call from Flask routes.
    """

    QUOTE_TTL       = 15    # seconds — live price cache
    SNAPSHOT_TTL    = 60    # seconds — multi-symbol snapshot
    FUNDAMENTAL_TTL = 300   # 5 minutes — fundamentals
    SECTOR_TTL      = 3600  # 1 hour — sector data
    NEWS_TTL        = 600   # 10 minutes — headlines (NO Perplexity here)

    DEFAULT_SYMBOLS = ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA", "SPY", "QQQ"]

    def __init__(self):
        self._cache = _TTLCache()
        self._config = {
            "alpaca_key":     os.getenv("ALPACA_API_KEY", ""),
            "alpaca_secret":  os.getenv("ALPACA_SECRET_KEY", ""),
        }
        self._timeout = int(os.getenv("MARKET_DATA_REQUEST_TIMEOUT", "5"))
        self._alpaca_base  = "https://data.alpaca.markets/v2"
        self._alpaca_cbase = "https://api.alpaca.markets/v2"

        logger.info("🚀 RealtimeMarketPipeline initialized")

    # ─────────────────────────────────────────────────────────────
    # Public API
    # ─────────────────────────────────────────────────────────────

    def get_quote(self, symbol: str) -> Dict[str, Any]:
        """Get latest quote for a single symbol (cached 15s)"""
        key = f"quote:{symbol.upper()}"
        cached = self._cache.get(key)
        if cached:
            cached["_cached"] = True
            return cached

        result = self._alpaca_quote(symbol) or self._stale_fallback(symbol)
        if result and not result.get("error"):
            self._cache.set(key, result, self.QUOTE_TTL)
        return result

    def get_snapshot(self, symbols: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Get live quotes for multiple symbols in one call.
        Returns {symbol: quote_dict, ...}
        """
        symbols = [s.upper() for s in (symbols or self.DEFAULT_SYMBOLS)]
        key = f"snapshot:{'_'.join(sorted(symbols))}"
        cached = self._cache.get(key)
        if cached:
            return cached

        result = {}
        # Try batch Alpaca first
        batch = self._alpaca_snapshot(symbols)
        if batch:
            result = batch
        else:
            for sym in symbols:
                result[sym] = self.get_quote(sym)

        out = {
            "quotes": result,
            "symbols": symbols,
            "provider": "alpaca",
            "timestamp": datetime.now().isoformat(),
            "count": len(result),
        }
        self._cache.set(key, out, self.SNAPSHOT_TTL)
        return out

    def get_sector_performance(self) -> Dict[str, Any]:
        """Return a neutral sector scaffold until a supported sector feed is added."""
        return {
            "sectors": [],
            "timestamp": datetime.now().isoformat(),
            "_fallback": True,
            "provider": "alpaca",
        }

    def get_market_summary(self) -> Dict[str, Any]:
        """
        Single call that combines snapshot + sector data — optimised for
        the frontend dashboard refresh cycle.
        """
        snapshot = self.get_snapshot()
        sectors = self.get_sector_performance()

        # Derive simple market mood from SPY price change
        spy_quote = snapshot.get("quotes", {}).get("SPY", {})
        spy_change = spy_quote.get("change_pct", 0.0)

        if spy_change > 1.0:
            mood = "euphoria"
        elif spy_change > 0.3:
            mood = "greed"
        elif spy_change < -1.0:
            mood = "despair"
        elif spy_change < -0.3:
            mood = "fear"
        else:
            mood = "neutral"

        return {
            "snapshot": snapshot,
            "sectors": sectors,
            "market_mood": mood,
            "spy_change_pct": spy_change,
            "timestamp": datetime.now().isoformat(),
        }

    def get_fundamentals(self, symbol: str) -> Dict[str, Any]:
        return {
            "symbol": symbol.upper(),
            "error": "Fundamentals unavailable from configured market-data provider",
            "timestamp": datetime.now().isoformat(),
        }

    # ─────────────────────────────────────────────────────────────
    # Provider Implementations
    # ─────────────────────────────────────────────────────────────

    def _alpaca_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        if not self._config["alpaca_key"]:
            return None
        try:
            headers = {
                "APCA-API-KEY-ID":     self._config["alpaca_key"],
                "APCA-API-SECRET-KEY": self._config["alpaca_secret"],
            }
            url = f"{self._alpaca_base}/stocks/{symbol.upper()}/quotes/latest"
            resp = requests.get(url, headers=headers, timeout=self._timeout)
            if resp.ok:
                data = resp.json().get("quote", {})
                return self._normalise_alpaca_quote(symbol, data)
        except Exception as e:
            logger.debug(f"Alpaca quote failed for {symbol}: {e}")
        return None

    def _alpaca_snapshot(self, symbols: List[str]) -> Optional[Dict[str, Any]]:
        if not self._config["alpaca_key"]:
            return None
        try:
            headers = {
                "APCA-API-KEY-ID":     self._config["alpaca_key"],
                "APCA-API-SECRET-KEY": self._config["alpaca_secret"],
            }
            url = f"{self._alpaca_base}/stocks/snapshots?symbols={','.join(symbols)}"
            resp = requests.get(url, headers=headers, timeout=self._timeout)
            if resp.ok:
                raw = resp.json()
                return {
                    sym: self._normalise_alpaca_snapshot(sym, data)
                    for sym, data in raw.items()
                }
        except Exception as e:
            logger.debug(f"Alpaca snapshot failed: {e}")
        return None

    def _stale_fallback(self, symbol: str) -> Dict[str, Any]:
        """Return last cached value (even if expired) or error scaffold"""
        # Try to get stale value directly from cache internal store
        stale = self._cache._store.get(f"quote:{symbol.upper()}")
        if stale:
            val = stale[0].copy()
            val["_stale"] = True
            return val
        return {
            "symbol": symbol.upper(),
            "price": None,
            "change": None,
            "change_pct": None,
            "error": "Alpaca provider failed",
            "timestamp": datetime.now().isoformat(),
        }

    # ─────────────────────────────────────────────────────────────
    # Normalisers — unified output schema
    # ─────────────────────────────────────────────────────────────

    def _normalise_alpaca_quote(self, symbol: str, q: Dict) -> Dict[str, Any]:
        price = q.get("ap") or q.get("bp") or 0.0
        return {
            "symbol": symbol.upper(),
            "price": round(float(price), 4),
            "bid": round(float(q.get("bp", price)), 4),
            "ask": round(float(q.get("ap", price)), 4),
            "change": None,
            "change_pct": None,
            "volume": None,
            "provider": "alpaca",
            "timestamp": datetime.now().isoformat(),
        }

    def _normalise_alpaca_snapshot(self, symbol: str, d: Dict) -> Dict[str, Any]:
        lq = d.get("latestQuote", {})
        prev = d.get("prevDailyBar", {})
        curr = d.get("dailyBar", {})
        price = curr.get("c") or lq.get("ap") or 0.0
        prev_close = prev.get("c", price) or price
        change = float(price) - float(prev_close) if prev_close else 0
        change_pct = (change / float(prev_close) * 100) if prev_close else 0
        return {
            "symbol": symbol.upper(),
            "price": round(float(price), 4),
            "change": round(change, 4),
            "change_pct": round(change_pct, 4),
            "volume": curr.get("v"),
            "open": curr.get("o"),
            "high": curr.get("h"),
            "low": curr.get("l"),
            "prev_close": round(float(prev_close), 4),
            "provider": "alpaca",
            "timestamp": datetime.now().isoformat(),
        }




# ─────────────────────────────────────────────────────────────
# Global singleton
# ─────────────────────────────────────────────────────────────
_pipeline: Optional[RealtimeMarketPipeline] = None

def get_realtime_pipeline() -> RealtimeMarketPipeline:
    """Get or create the global RealtimeMarketPipeline singleton"""
    global _pipeline
    if _pipeline is None:
        _pipeline = RealtimeMarketPipeline()
    return _pipeline
