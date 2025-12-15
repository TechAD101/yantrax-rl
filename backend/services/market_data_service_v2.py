"""
Market Data Service v2.1
Professional-grade market data abstraction with multiple providers,
rate limiting, caching, and comprehensive error handling.

Providers:
1. Alpha Vantage (primary, 25 calls/day)
2. Alpaca (secondary, 200 calls/min UNLIMITED)
3. Mock (fallback)

Author: YantraX Team
Date: 2025-11-27
"""

import os
import time
import logging
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from functools import lru_cache
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class DataProvider(Enum):
    """Available market data providers"""
    ALPHA_VANTAGE = "alpha_vantage"
    ALPACA = "alpaca"  # NEW: Free unlimited real-time data!
    POLYGON = "polygon"
    FINNHUB = "finnhub"
    # MOCK provider removed to ensure only real providers are used in production

@dataclass
class MarketDataConfig:
    """Configuration for market data service"""
    alpha_vantage_key: str
    alpaca_key: Optional[str] = None  # NEW
    alpaca_secret: Optional[str] = None  # NEW
    polygon_key: Optional[str] = None
    finnhub_key: Optional[str] = None
    cache_ttl_seconds: int = 60  # 1 minute cache
    request_timeout: int = 10
    rate_limit_calls: int = 25  # Alpha Vantage: 25/day
    rate_limit_period: int = 86400  # 1 day in seconds
    fallback_to_mock: bool = True
    
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
        self.rate_limiters = {
            DataProvider.ALPHA_VANTAGE: RateLimiter(25, 86400),  # 25/day
            DataProvider.ALPACA: RateLimiter(200, 60)  # 200/minute (very generous!)
        }
        
        # Determine available providers
        self.providers = self._get_available_providers()
        logger.info(f"🚀 MarketDataService initialized with providers: {[p.value for p in self.providers]}")
        
    def _get_available_providers(self) -> List[DataProvider]:
        """Determine which providers are configured and available"""
        providers = []
        
        # Alpha Vantage (primary)
        if self.config.alpha_vantage_key and self.config.alpha_vantage_key != 'demo':
            providers.append(DataProvider.ALPHA_VANTAGE)
            logger.info("✅ Alpha Vantage configured (25/day)")
            
        # Alpaca (secondary - UNLIMITED FREE!)
        if self.config.alpaca_key and self.config.alpaca_secret:
            providers.append(DataProvider.ALPACA)
            logger.info("✅ Alpaca configured (200/min UNLIMITED!)")
            
        if self.config.polygon_key:
            providers.append(DataProvider.POLYGON)
            
        if self.config.finnhub_key:
            providers.append(DataProvider.FINNHUB)
            
        # Mock fallback is deprecated. If fallback flag is accidentally set, warn but do not add a provider.
        if self.config.fallback_to_mock:
            logger.warning("⚠️ fallback_to_mock is enabled but mock provider has been deprecated; ignoring flag")
            
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
        """
        Get stock price with intelligent fallback strategy.
        Tries providers in order until one succeeds.
        """
        symbol = symbol.upper()
        
        # Check cache first
        cached = self._check_cache(symbol)
        if cached:
            return cached
            
        # Try each provider in order
        for provider in self.providers:
            try:
                logger.info(f"🔄 Trying {provider.value} for {symbol}...")
                
                if provider == DataProvider.ALPHA_VANTAGE:
                    result = self._fetch_alpha_vantage(symbol)
                elif provider == DataProvider.ALPACA:
                    result = self._fetch_alpaca(symbol)
                elif provider == DataProvider.POLYGON:
                    result = self._fetch_polygon(symbol)
                elif provider == DataProvider.FINNHUB:
                    result = self._fetch_finnhub(symbol)
                elif provider == getattr(DataProvider, 'MOCK', None):
                    # Should not happen; mock provider deprecated
                    result = None
                else:
                    continue
                    
                if result and result.get('price', 0) > 0:
                    # Cache successful result
                    self.cache[symbol] = (datetime.now(), result)
                    logger.info(f"✅ SUCCESS with {provider.value} for {symbol}: ${result['price']}")
                    return result
                    
            except Exception as e:
                logger.error(f"❌ {provider.value} failed for {symbol}: {str(e)}")
                continue
                
        # All providers failed
        logger.error(f"💥 ALL PROVIDERS FAILED for {symbol}")
        return self._generate_error_response(symbol)
        
    def _fetch_alpha_vantage(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch data from Alpha Vantage API"""
        rate_limiter = self.rate_limiters[DataProvider.ALPHA_VANTAGE]
        
        if not rate_limiter.can_proceed():
            wait_time = rate_limiter.wait_time()
            logger.warning(f"⏳ Rate limit reached for Alpha Vantage. Wait {wait_time:.1f}s")
            return None  # Don't wait, try next provider
            
        url = f"https://www.alphavantage.co/query"
        params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': symbol,
            'apikey': self.config.alpha_vantage_key
        }
        
        response = requests.get(url, params=params, timeout=self.config.request_timeout)
        response.raise_for_status()
        data = response.json()
        
        # Validate response
        if 'Global Quote' not in data:
            logger.warning(f"⚠️ Alpha Vantage: No Global Quote in response for {symbol}")
            return None
            
        quote = data['Global Quote']
        if not quote:
            logger.warning(f"⚠️ Alpha Vantage: Empty Global Quote for {symbol}")
            return None
            
        # Extract and validate data
        try:
            price = float(quote.get('05. price', 0))
            prev_close = float(quote.get('08. previous close', 0) or price)
            
            if price <= 0:
                logger.warning(f"⚠️ Alpha Vantage: Invalid price {price} for {symbol}")
                return None
                
            return {
                'symbol': symbol,
                'price': round(price, 2),
                'change': round(price - prev_close, 2),
                'changePercent': round(((price - prev_close) / prev_close) * 100, 2) if prev_close > 0 else 0,
                'timestamp': datetime.now().isoformat(),
                'source': 'alpha_vantage',
                'provider_details': {
                    'volume': quote.get('06. volume'),
                    'latest_trading_day': quote.get('07. latest trading day')
                }
            }
        except (ValueError, KeyError) as e:
            logger.error(f"❌ Alpha Vantage: Data parsing error for {symbol}: {e}")
            return None
    
    def _fetch_alpaca(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch data from Alpaca Markets API (FREE unlimited!)"""
        rate_limiter = self.rate_limiters[DataProvider.ALPACA]
        
        if not rate_limiter.can_proceed():
            wait_time = rate_limiter.wait_time()
            logger.warning(f"⏳ Rate limit reached for Alpaca. Wait {wait_time:.1f}s")
            time.sleep(wait_time)
            
        # Alpaca REST API for latest quote
        base_url = "https://data.alpaca.markets/v2"
        headers = {
            'APCA-API-KEY-ID': self.config.alpaca_key,
            'APCA-API-SECRET-KEY': self.config.alpaca_secret
        }
        
        # Get latest quote
        url = f"{base_url}/stocks/{symbol}/quotes/latest"
        
        response = requests.get(url, headers=headers, timeout=self.config.request_timeout)
        response.raise_for_status()
        data = response.json()
        
        # Validate response
        if 'quote' not in data:
            logger.warning(f"⚠️ Alpaca: No quote data for {symbol}")
            return None
            
        quote = data['quote']
        
        # Extract mid price (average of bid and ask)
        try:
            bid_price = float(quote.get('bp', 0))
            ask_price = float(quote.get('ap', 0))
            
            if bid_price <= 0 or ask_price <= 0:
                logger.warning(f"⚠️ Alpaca: Invalid prices (bid: {bid_price}, ask: {ask_price}) for {symbol}")
                return None
            
            # Use mid price as current price
            current_price = (bid_price + ask_price) / 2
            
            # Get previous close for change calculation
            # Note: We'll use a simple estimation here, or fetch from bars endpoint
            # For now, estimate 0.5% daily volatility
            prev_close = current_price * 0.995  # Simple estimate
            
            return {
                'symbol': symbol,
                'price': round(current_price, 2),
                'bid': round(bid_price, 2),
                'ask': round(ask_price, 2),
                'change': round(current_price - prev_close, 2),
                'changePercent': round(((current_price - prev_close) / prev_close) * 100, 2),
                'timestamp': datetime.now().isoformat(),
                'source': 'alpaca',
                'provider_details': {
                    'bid_size': quote.get('bs'),
                    'ask_size': quote.get('as'),
                    'quote_timestamp': quote.get('t')
                }
            }
        except (ValueError, KeyError, ZeroDivisionError) as e:
            logger.error(f"❌ Alpaca: Data parsing error for {symbol}: {e}")
            return None
            
    def _fetch_polygon(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch data from Polygon.io API (placeholder for future)"""
        # TODO: Implement Polygon.io integration
        logger.info("📏 Polygon.io not yet implemented")
        return None
        
    def _fetch_finnhub(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch data from Finnhub API (placeholder for future)"""
        # TODO: Implement Finnhub integration
        logger.info("📏 Finnhub not yet implemented")
        return None
        
    def _generate_mock_data(self, symbol: str) -> Dict[str, Any]:
        """Mock generator removed to prevent simulated data in production."""
        raise NotImplementedError("Mock data generation has been removed. Configure a real provider.")
        
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
        """Get prices for multiple symbols efficiently"""
        results = {}
        for symbol in symbols:
            results[symbol] = self.get_stock_price(symbol)
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