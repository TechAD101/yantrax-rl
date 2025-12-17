"""
Market Data Service v2.1
Professional-grade market data abstraction with multiple providers,
rate limiting, caching, and comprehensive error handling.

Providers:
- FinancialModelingPrep (FMP) - batch quote API (primary and only providey")

Author: YantraX Team
Date: 2025-11-27
"""

import os
import time
import logging
import requests  # type: ignore[import]
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from functools import lru_cache
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class DataProvider(Enum):
    """Available market data providers"""
    FMP = "fmp"

@dataclass
class MarketDataConfig:
    """Configuration for market data service (FMP-only)"""
    # Read FMP API key from env by default but allow override in tests/config
    fmp_api_key: str = os.getenv("FMP_API_KEY", "14uTc09TMyUVJEuFKriHayCTnLcyGhyy")
    # Very short TTL for live data to keep UI responsive
    cache_ttl_seconds: int = 5  # seconds
    request_timeout: int = 10
    # Soft rate limiting for FMP (calls per period)
    rate_limit_calls: int = 300
    rate_limit_period: int = 60  # 60 seconds
    # Maximum symbols per batch request to keep URL lengths small
    batch_size: int = 50
    
class RateLimiter:
    """Simple rate limiter to avoid hitting API limits"""
    
    def __init__(self, max_calls: int, period: int):
        self.max_calls = max_calls
        self.period = period
        self.calls: List[float] = []
        
    def can_proceed(self) -> bool:
        """Check if we can make another API call"""
        now = time.time()
        # Remove old calls outside the period
        self.calls = [call_time for call_time in self.calls if now - call_time < self.period]
        
        if len(self.calls) < self.max_calls:
            self.calls.append(now)
            return True
        return False
        
    def wait_time(self) -> float:
        """Get seconds to wait before next call is allowed"""
        if not self.calls:
            return 0
        oldest_call = min(self.calls)
        return max(0, self.period - (time.time() - oldest_call))

class MarketDataService:
    """
    Professional market data service with multiple providers,
    intelligent fallback, caching, and rate limiting.
    """
    
    def __init__(self, config: MarketDataConfig):
        self.config = config
        self.cache: Dict[str, tuple[datetime, Dict]] = {}
        # Only FMP in production
        self.rate_limiters = {
            DataProvider.FMP: RateLimiter(self.config.rate_limit_calls, self.config.rate_limit_period)
        }

        # Determine available providers
        self.providers = self._get_available_providers()
        logger.info(f"🚀 MarketDataService initialized with providers: {[p.value for p in self.providers]}")
        
    def _get_available_providers(self) -> List[DataProvider]:
        """Determine which providers are configured and available (FMP-only)."""
        providers: List[DataProvider] = []
        fmp_key = getattr(self.config, "fmp_api_key", None)
        if fmp_key:
            providers.append(DataProvider.FMP)
            logger.info("✅ FinancialModelingPrep (FMP) configured")
        else:
            logger.error("❌ FMP API key not configured. Set FMP_API_KEY in environment or pass via MarketDataConfig.fmp_api_key")
        return providers
        
    def _check_cache(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Check if we have valid cached data"""
        if symbol in self.cache:
            timestamp, data = self.cache[symbol]
            age = (datetime.now() - timestamp).total_seconds()
            if age < self.config.cache_ttl_seconds:
                logger.info(f"✅ Cache HIT for {symbol} (age: {age:.1f}s)")
                data['cached'] = True
                data['cache_age'] = round(age, 1)
                return data
            else:
                logger.info(f"❌ Cache EXPIRED for {symbol} (age: {age:.1f}s)")
        return None
        
    def get_stock_price(self, symbol: str) -> Dict[str, Any]:
        """Get a single symbol price using FMP batch endpoint (production ready)."""
        symbol = symbol.upper()

        # Check cache first
        cached = self._check_cache(symbol)
        if cached:
            return cached

        # Ensure FMP provider is available
        if DataProvider.FMP not in self.providers:
            logger.error("❌ No configured provider available for market data")
            return self._generate_error_response(symbol)

        # Attempt to fetch from FMP (single symbol via batch endpoint)
        try:
            result = self._fetch_fmp_single(symbol)
            if result and result.get('price', 0) > 0:
                self.cache[symbol] = (datetime.now(), result)
                logger.info(f"✅ SUCCESS with fmp for {symbol}: ${result['price']}")
                return result
            else:
                logger.error(f"❌ FMP returned no price for {symbol}")
        except Exception as e:
            logger.error(f"❌ FMP provider failed for {symbol}: {e}")

        return self._generate_error_response(symbol)

    # Backwards-compatible alias used by some callers
    def get_price(self, symbol: str) -> Dict[str, Any]:
        """Alias for get_stock_price for backwards compatibility."""
        return self.get_stock_price(symbol)
        
    def _fetch_fmp_batch(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        """Fetch a batch of symbols from FinancialModelingPrep in one HTTP call.
        Returns a mapping of symbol -> data dict for found symbols.
        """
        results: Dict[str, Dict[str, Any]] = {}

        if not symbols:
            return results

        # Rate limit check
        rate_limiter = self.rate_limiters.get(DataProvider.FMP)
        if rate_limiter and not rate_limiter.can_proceed():
            logger.warning("⏳ Rate limit reached for FMP; skipping request")
            return results

        # Respect batch size
        chunks: List[List[str]] = []
        current = []
        for sym in symbols:
            current.append(sym.upper())
            if len(current) >= self.config.batch_size:
                chunks.append(current)
                current = []
        if current:
            chunks.append(current)

        for chunk in chunks:
            symbols_csv = ",".join(chunk)
            url = f"https://financialmodelingprep.com/api/v3/quote/{symbols_csv}"
            params = { 'apikey': self.config.fmp_api_key }

            try:
                resp = requests.get(url, params=params, timeout=self.config.request_timeout)
                resp.raise_for_status()
                data = resp.json()

                if not isinstance(data, list):
                    logger.warning(f"⚠️ Unexpected FMP payload for {symbols_csv}: {type(data)}")
                    continue

                for row in data:
                    sym = row.get('symbol', '').upper()
                    if not sym:
                        continue
                    price = row.get('price')
                    try:
                        price_val = None if price is None else round(float(price), 2)
                    except (ValueError, TypeError):
                        price_val = None

                    results[sym] = {
                        'symbol': sym,
                        'price': price_val if price_val is not None else 0,
                        'bid': row.get('bid'),
                        'ask': row.get('ask'),
                        'change': row.get('change'),
                        'changePercent': row.get('changesPercentage'),
                        'timestamp': datetime.now().isoformat(),
                        'source': 'fmp',
                        'provider_details': row
                    }
            except Exception as e:
                logger.error(f"❌ FMP batch request failed for {symbols_csv}: {e}")
                continue

        return results

    def _fetch_fmp_single(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Helper to fetch a single symbol using the batch endpoint."""
        res = self._fetch_fmp_batch([symbol])
        return res.get(symbol.upper())

        
    def _generate_error_response(self, symbol: str) -> Dict[str, Any]:
        """Generate error response when all providers fail"""
        return {
            'symbol': symbol,
            'price': 0,
            'change': 0,
            'changePercent': 0,
            'timestamp': datetime.now().isoformat(),
            'source': 'error',
            'error': 'Unable to fetch market data from any provider'
        }
        
    def get_batch_prices(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        """Get prices for multiple symbols in a single FMP batch request where possible."""
        symbols_norm = [s.upper() for s in symbols]
        results: Dict[str, Dict[str, Any]] = {}

        if DataProvider.FMP not in self.providers:
            for s in symbols_norm:
                results[s] = self._generate_error_response(s)
            return results

        fetched = self._fetch_fmp_batch(symbols_norm)
        now_ts = datetime.now().isoformat()
        for s in symbols_norm:
            data = fetched.get(s)
            if data and data.get('price', 0) > 0:
                # cache and return
                self.cache[s] = (datetime.now(), data)
                results[s] = data
            else:
                results[s] = self._generate_error_response(s)
        return results
        
    def clear_cache(self):
        """Clear all cached data"""
        self.cache.clear()
        logger.info("🗑️ Cache cleared")
        
    def get_health(self) -> Dict[str, Any]:
        """Get service health information"""
        return {
            'healthy': True,
            'providers': [p.value for p in self.providers],
            'cache_size': len(self.cache),
            'rate_limits': {
                provider.value: {
                    'calls_remaining': limiter.max_calls - len(limiter.calls),
                    'wait_time': limiter.wait_time()
                }
                for provider, limiter in self.rate_limiters.items()
            }
        }