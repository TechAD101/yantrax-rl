"""
Market Data Service - Waterfall Strategy
Priority: YFinance (Free) -> FMP (Fundamentals) -> Alpaca (Live Price) -> Alpha Vantage (Backup)
"""

import os
import logging
import time
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from threading import Lock

# Third-party imports moved to lazy load inside methods to save memory
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class RateLimitExceeded(Exception):
    pass

class DailyRateLimiter:
    """Tracks daily API usage to prevent limit exhaustion"""
    def __init__(self, provider_name: str, daily_limit: int):
        self.provider_name = provider_name
        self.daily_limit = daily_limit
        self.calls_today = 0
        self.last_reset = datetime.now().date()
        self._lock = Lock()
    
    def check(self):
        with self._lock:
            today = datetime.now().date()
            if today != self.last_reset:
                self.calls_today = 0
                self.last_reset = today
            
            if self.daily_limit > 0 and self.calls_today >= self.daily_limit:
                logger.warning(f"🚫 {self.provider_name} daily limit reached ({self.daily_limit})")
                raise RateLimitExceeded(f"{self.provider_name} limit reached")
            
    def increment(self):
        with self._lock:
            self.calls_today += 1
            if self.calls_today % 10 == 0:
                logger.info(f"📊 {self.provider_name} usage: {self.calls_today}/{self.daily_limit}")

class WaterfallMarketDataService:
    def __init__(self):
        self.providers = {}
        self._init_providers()
        
    def _init_providers(self):
        # 1. FMP (Price & Fundamentals Primary - Lightweight & Fast)
        fmp_key = os.getenv('FMP_API_KEY') or os.getenv('FMP_KEY')
        self.providers['fmp'] = {
            'enabled': bool(fmp_key),
            'key': fmp_key,
            'limiter': DailyRateLimiter('fmp', int(os.getenv('FMP_DAILY_LIMIT', 250)))
        }

        # 2. Alpaca (Price Fallback - Live & Reliable)
        alpaca_key = os.getenv('ALPACA_API_KEY')
        self.providers['alpaca'] = {
            'enabled': bool(alpaca_key),
            'key': alpaca_key,
            'secret': os.getenv('ALPACA_SECRET_KEY'),
            'limiter': DailyRateLimiter('alpaca', 1000)
        }
        
        # 3. YFinance (Last Resort - Heavy on RAM)
        self.providers['yfinance'] = {
            'enabled': True,
            'limiter': DailyRateLimiter('yfinance', 2000)
        }
        
        # 4. Alpha Vantage (Deep Backup)
        av_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        self.providers['alpha_vantage'] = {
            'enabled': bool(av_key),
            'key': av_key,
            'limiter': DailyRateLimiter('alpha_vantage', 25)
        }
        
        logger.info(f"🌊 Waterfall Service Initialized. Active: {[k for k,v in self.providers.items() if v['enabled']]}")

    def get_price(self, symbol: str) -> Dict[str, Any]:
        """Get current price using waterfall strategy"""
        symbol = symbol.upper()
        errors = []
        
        # Strategy 1: FMP (Lightweight JSON)
        if self._can_use('fmp'):
            try:
                self._use('fmp')
                import requests
                url = f"https://financialmodelingprep.com/api/v3/quote/{symbol}?apikey={self.providers['fmp']['key']}"
                resp = requests.get(url, timeout=5)
                if resp.status_code == 200:
                    data = resp.json()
                    if data:
                        return self._success('fmp', symbol, data[0]['price'])
            except Exception as e:
                errors.append(f"fmp: {e}")

        # Strategy 2: Alpaca (Reliable)
        if self._can_use('alpaca'):
            try:
                import requests
                self._use('alpaca')
                headers = {
                    'APCA-API-KEY-ID': self.providers['alpaca']['key'],
                    'APCA-API-SECRET-KEY': self.providers['alpaca']['secret']
                }
                url = f"https://data.alpaca.markets/v2/stocks/{symbol}/quotes/latest"
                resp = requests.get(url, headers=headers, timeout=5)
                if resp.status_code == 200:
                    data = resp.json()
                    price = float(data['quote']['ap']) # Ask price as proxy
                    return self._success('alpaca', symbol, price)
            except Exception as e:
                errors.append(f"alpaca: {e}")

        # Strategy 3: YFinance (Heavy Fallback)
        if self._can_use('yfinance'):
            try:
                self._use('yfinance')
                import yfinance as yf
                ticker = yf.Ticker(symbol)
                # fast_info is faster than history
                price = ticker.fast_info.last_price
                if price:
                    return self._success('yfinance', symbol, price)
            except Exception as e:
                errors.append(f"yfinance: {e}")

        logger.error(f"❌ All price providers failed for {symbol}: {errors}")
        return self._error(symbol, "All providers failed")

    def get_fundamentals(self, symbol: str) -> Dict[str, Any]:
        """Get fundamental data (ROE, PE, etc) for agents"""
        symbol = symbol.upper()
        
        # Strategy 1: FMP (Best for fundamentals)
        if self._can_use('fmp'):
            try:
                self._use('fmp')
                import requests
                # Get Ratios
                url = f"https://financialmodelingprep.com/api/v3/ratios-ttm/{symbol}?apikey={self.providers['fmp']['key']}"
                resp = requests.get(url, timeout=5)
                data = resp.json()
                
                if data and isinstance(data, list):
                    r = data[0]
                    return {
                        'symbol': symbol,
                        'pe_ratio': r.get('peRatioTTM', 0),
                        'return_on_equity': r.get('returnOnEquityTTM', 0),
                        'profit_margin': r.get('netProfitMarginTTM', 0),
                        'debt_to_equity': r.get('debtEquityRatioTTM', 0),
                        'dividend_yield': r.get('dividendYielTTM', 0),
                        'source': 'fmp'
                    }
            except Exception as e:
                logger.warning(f"FMP fundamentals failed: {e}")

        # Strategy 2: YFinance (Backup, slower)
        if self._can_use('yfinance'):
            try:
                self._use('yfinance')
                import yfinance as yf
                t = yf.Ticker(symbol)
                info = t.info
                return {
                    'symbol': symbol,
                    'pe_ratio': info.get('trailingPE', 0),
                    'return_on_equity': info.get('returnOnEquity', 0),
                    'profit_margin': info.get('profitMargins', 0),
                    'debt_to_equity': info.get('debtToEquity', 0) / 100 if info.get('debtToEquity') else 0,
                    'dividend_yield': info.get('dividendYield', 0),
                    'source': 'yfinance'
                }
            except Exception as e:
                logger.warning(f"YFinance fundamentals failed: {e}")

        return {
            'symbol': symbol,
            'source': 'mock',
            'pe_ratio': 15.0,
            'return_on_equity': 0.2, # Mock healthy data so agents don't crash, but logged
            'note': 'Real data unavailable'
        }

    def _can_use(self, provider: str) -> bool:
        p = self.providers.get(provider)
        if not p or not p['enabled']:
            return False
        try:
            p['limiter'].check()
            return True
        except RateLimitExceeded:
            return False

    def _use(self, provider: str):
        self.providers[provider]['limiter'].increment()

    def _success(self, source: str, symbol: str, price: float) -> Dict[str, Any]:
        return {
            'symbol': symbol,
            'price': price,
            'source': source,
            'timestamp': datetime.now().isoformat()
        }

    def _error(self, symbol: str, msg: str) -> Dict[str, Any]:
        return {
            'symbol': symbol,
            'price': 0.0,
            'source': 'error',
            'error': msg,
            'timestamp': datetime.now().isoformat()
        }
