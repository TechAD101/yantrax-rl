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
import numpy as np
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class DataProvider(Enum):
    """Available market data providers"""
    FMP = "fmp"
    YFINANCE = "yfinance"
    FINNHUB = "finnhub"

@dataclass
class MarketDataConfig:
    """Configuration for market data service (FMP-only)"""
    # Read FMP API key from env by default but allow override in tests/config
    fmp_api_key: str = os.getenv("FMP_API_KEY")
    # Updated to 60s as per user requirement for 1-minute updates
    cache_ttl_seconds: int = 60  # seconds
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
        # Rate limiters for providers
        self.rate_limiters = {
            DataProvider.FMP: RateLimiter(self.config.rate_limit_calls, self.config.rate_limit_period),
            DataProvider.YFINANCE: RateLimiter(2000, 3600), # yfinance is more generous for testing
            DataProvider.FINNHUB: RateLimiter(60, 60) # Finnhub free tier: 60 calls/min
        }

        # Determine available providers
        self.providers = self._get_available_providers()
        logger.info(f"🚀 MarketDataService initialized with providers: {[p.value for p in self.providers]}")
        
    def _get_available_providers(self) -> List[DataProvider]:
        """Determine which providers are configured and available."""
        providers: List[DataProvider] = []
        
        # FMP Check
        fmp_key = getattr(self.config, "fmp_api_key", None)
        if fmp_key:
            providers.append(DataProvider.FMP)
            logger.info("✅ FinancialModelingPrep (FMP) configured")
        else:
            logger.warning("⚠️ FMP API key not configured. FMP provider disabled.")

        # yfinance is always available as a fallback
        providers.append(DataProvider.YFINANCE)
        logger.info("✅ yfinance (Yahoo Finance) fallback enabled")

        # Finnhub Check
        finnhub_key = os.getenv("FINNHUB_API_KEY")
        if finnhub_key:
            providers.append(DataProvider.FINNHUB)
            logger.info("✅ Finnhub configured")
        
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
        """Get a single symbol price with intelligent fallback."""
        symbol = symbol.upper()

        # Check cache first
        cached = self._check_cache(symbol)
        if cached:
            return cached

        # 1. Try FMP if available
        if DataProvider.FMP in self.providers:
            try:
                result = self._fetch_fmp_single(symbol)
                if result and result.get('price', 0) > 0:
                    self.cache[symbol] = (datetime.now(), result)
                    logger.info(f"✅ SUCCESS with FMP for {symbol}: ${result['price']}")
                    return result
            except Exception as e:
                logger.error(f"❌ FMP provider failed for {symbol}: {e}")

        # 2. Fallback to Finnhub if available
        if DataProvider.FINNHUB in self.providers:
            try:
                result = self._fetch_finnhub_single(symbol)
                if result and result.get('price', 0) > 0:
                    self.cache[symbol] = (datetime.now(), result)
                    logger.info(f"✅ SUCCESS with Finnhub for {symbol}: ${result['price']}")
                    return result
            except Exception as e:
                logger.error(f"❌ Finnhub provider failed for {symbol}: {e}")

        # 3. Fallback to yfinance
        if DataProvider.YFINANCE in self.providers:
            try:
                result = self._fetch_yfinance_single(symbol)
                if result and result.get('price', 0) > 0:
                    self.cache[symbol] = (datetime.now(), result)
                    logger.info(f"✅ SUCCESS with yfinance for {symbol}: ${result['price']}")
                    return result
            except Exception as e:
                logger.error(f"❌ yfinance provider failed for {symbol}: {e}")

        return self._generate_error_response(symbol)

    def _fetch_finnhub_single(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch data from Finnhub API."""
        api_key = os.getenv("FINNHUB_API_KEY")
        if not api_key:
            return None
            
        try:
            url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={api_key}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                price = data.get('c') # Current price
                if price and price > 0:
                    return {
                        'symbol': symbol,
                        'price': round(float(price), 2),
                        'change': round(float(data.get('d', 0)), 2),
                        'changePercent': round(float(data.get('dp', 0)), 2),
                        'timestamp': datetime.now().isoformat(),
                        'source': 'finnhub'
                    }
        except Exception as e:
            logger.error(f"Finnhub error for {symbol}: {e}")
        return None

    def _fetch_yfinance_single(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch data from Yahoo Finance via yfinance library."""
        import yfinance as yf
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.fast_info
            
            # Get current price
            price = info.get('last_price') or info.get('regular_market_price')
            if not price:
                # Fallback to history if fast_info fails
                hist = ticker.history(period="1d")
                if not hist.empty:
                    price = hist['Close'].iloc[-1]

            if price:
                # Calculate change if possible
                prev_close = info.get('previous_close')
                change = price - prev_close if prev_close else 0
                change_pct = (change / prev_close * 100) if prev_close else 0

                return {
                    'symbol': symbol,
                    'price': round(float(price), 2),
                    'change': round(float(change), 2),
                    'changePercent': round(float(change_pct), 2),
                    'timestamp': datetime.now().isoformat(),
                    'source': 'yfinance'
                }
        except Exception as e:
            logger.error(f"yfinance error for {symbol}: {e}")
        return None

    # Backwards-compatible alias used by some callers
    def get_price(self, symbol: str) -> Dict[str, Any]:
        """Alias for get_stock_price for backwards compatibility."""
        return self.get_stock_price(symbol)

    def get_fundamentals(self, symbol: str) -> Dict[str, Any]:
        """Shim for fundamental data (v2 currently only supports price)."""
        return {}

    def get_verification_stats(self) -> Dict[str, Any]:
        """Shim for verification statistics."""
        return {}

    def get_price_verified(self, symbol: str) -> Dict[str, Any]:
        """Shim for triple-source verification (v2 currently is single-source)."""
        return {
            'verified': False,
            'price': self.get_price(symbol).get('price', 0),
            'source': 'fmp'
        }

    def get_recent_audit_logs(self, limit: int = 10) -> List[Any]:
        """Shim for audit trail logs."""
        return []
        
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
            # Default to v4 to avoid legacy 403 warnings seen in logs
            url = f"https://financialmodelingprep.com/api/v4/quote/{symbols_csv}"
            params = { 'apikey': self.config.fmp_api_key }

            try:
                resp = requests.get(url, params=params, timeout=self.config.request_timeout)

                # If v4 fails (e.g. not authorized for v4), try v3 as fallback
                if not resp.ok:
                    logger.debug(f"ℹ️ FMP v4 failed for {symbols_csv}, attempting v3 endpoint as fallback")
                    alt_url = f"https://financialmodelingprep.com/api/v3/quote/{symbols_csv}"
                    resp = requests.get(alt_url, params=params, timeout=self.config.request_timeout)

                # If still not OK, try the 'quote-short' endpoint which some keys allow
                if not resp.ok:
                    logger.info(f"ℹ️ Trying FMP quote-short endpoint as secondary fallback for {symbols_csv}")
                    alt_url = f"https://financialmodelingprep.com/api/v3/quote-short/{symbols_csv}"
                    resp = requests.get(alt_url, params=params, timeout=self.config.request_timeout)

                # Final fallback for single-symbol requests: stock real-time price
                if not resp.ok and len(chunk) == 1:
                    single = chunk[0]
                    rt_url = f"https://financialmodelingprep.com/api/v3/stock/real-time-price/{single}"
                    resp = requests.get(rt_url, params=params, timeout=self.config.request_timeout)

                resp.raise_for_status()
                data = resp.json()

                # Normalize responses which might be single-object or list
                payload_rows = data if isinstance(data, list) else (data.get('symbol') and [data]) or data.get('quote') or []

                if not isinstance(payload_rows, list):
                    logger.warning(f"⚠️ Unexpected FMP payload for {symbols_csv}: {type(data)}")
                    continue

                for row in payload_rows:
                    sym = row.get('symbol', '').upper()
                    if not sym:
                        # real-time-price endpoint returns {symbol, price}
                        sym = row.get('ticker', '') or row.get('symbol', '')
                        sym = sym.upper() if sym else ''
                    if not sym:
                        continue
                    price = row.get('price') or row.get('realTimePrice') or row.get('close')
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
        """Get prices for multiple symbols with intelligent fallback."""
        symbols_norm = [s.upper() for s in symbols]
        results: Dict[str, Dict[str, Any]] = {}
        remaining_symbols = []

        # 1. Try FMP for all symbols if available
        if DataProvider.FMP in self.providers:
            try:
                fetched = self._fetch_fmp_batch(symbols_norm)
                for s in symbols_norm:
                    data = fetched.get(s)
                    if data and data.get('price', 0) > 0:
                        self.cache[s] = (datetime.now(), data)
                        results[s] = data
                    else:
                        remaining_symbols.append(s)
            except Exception as e:
                logger.error(f"FMP batch failed: {e}")
                remaining_symbols = symbols_norm
        else:
            remaining_symbols = symbols_norm

        # 2. Try yfinance for remaining symbols
        if remaining_symbols and DataProvider.YFINANCE in self.providers:
            try:
                import yfinance as yf
                # yfinance download is efficient for batches
                tickers_str = " ".join(remaining_symbols)
                data = yf.download(tickers_str, period="1d", interval="1m", progress=False)
                
                for s in remaining_symbols:
                    try:
                        # Handle both single and multi-ticker dataframes
                        if len(remaining_symbols) > 1:
                            if s in data['Close']:
                                price = data['Close'][s].iloc[-1]
                            else:
                                price = None
                        else:
                            price = data['Close'].iloc[-1] if not data.empty else None

                        if price and not np.isnan(price):
                            res = {
                                'symbol': s,
                                'price': round(float(price), 2),
                                'timestamp': datetime.now().isoformat(),
                                'source': 'yfinance'
                            }
                            self.cache[s] = (datetime.now(), res)
                            results[s] = res
                        else:
                            results[s] = self._generate_error_response(s)
                    except Exception as e:
                        logger.error(f"yfinance batch error for {s}: {e}")
                        results[s] = self._generate_error_response(s)
            except Exception as e:
                logger.error(f"yfinance batch download failed: {e}")
                for s in remaining_symbols:
                    if s not in results:
                        results[s] = self._generate_error_response(s)
        else:
            for s in remaining_symbols:
                if s not in results:
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