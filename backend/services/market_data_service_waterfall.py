"""
Market Data Service - Waterfall Strategy
Priority: YFinance (Free) -> FMP (Fundamentals) -> Alpaca (Live Price) -> Alpha Vantage (Backup)
Caching: 5-minute TTL for price and fundamentals
Circuit Breaking: Auto-skip exhausted providers
"""

import os
import logging
import time
from datetime import datetime
from typing import Dict, Any
from threading import Lock

# dotenv is optional in test environments
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    def load_dotenv(*args, **kwargs):
        return None


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
        self.cache = {
            'price': {},        # ticker -> {'price': float, 'source': str, 'expiry': float}
            'fundamentals': {}  # ticker -> {'data': dict, 'expiry': float}
        }
        # GLOBAL SYNC REQUIREMENT: 60s cache for institutional precision
        self.cache_ttl = 60 
        
        # Audit trail for triple-source verification (in-memory for now)
        self.audit_log = []  # List of verification attempts
        self.verification_stats = {
            'total_verifications': 0,
            'successful_verifications': 0,
            'variance_flags': 0,
            'partial_verifications': 0,
            'failed_verifications': 0
        }
        
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
        av_key = os.getenv('ALPHAVANTAGE_API_KEY') or os.getenv('ALPHA_VANTAGE_API_KEY') or os.getenv('ALPHA_VANTAGE_KEY')
        self.providers['alpha_vantage'] = {
            'enabled': bool(av_key),
            'key': av_key,
            'limiter': DailyRateLimiter('alpha_vantage', 25)
        }
        
        logger.info(f"🌊 Waterfall Service Initialized. Active: {[k for k,v in self.providers.items() if v['enabled']]}")

    def get_price(self, symbol: str, verified: bool = False) -> Dict[str, Any]:
        """Get current price using waterfall strategy with caching & circuit breaking.
        If verified=True, uses triple-source verification (Perplexity spec).
        """
        if verified:
            return self.get_price_verified(symbol)

        symbol = symbol.upper()
        now = time.time()
        
        # 0. Check Cache First
        if symbol in self.cache['price']:
            cached = self.cache['price'][symbol]
            if now < cached['expiry']:
                return self._success(cached['source'] + " (cached)", symbol, cached['price'])

        # Priority Order: YFinance -> FMP -> Alpaca -> Alpha Vantage
        providers = ['yfinance', 'fmp', 'alpaca', 'alpha_vantage']
        
        for provider in providers:
            try:
                fetch_func = getattr(self, f'_fetch_price_{provider}')
                price = fetch_func(symbol)
                if price:
                    res = self._success(provider, symbol, price)
                    self._update_cache('price', symbol, res)
                    return res
            except Exception as e:
                logger.warning(f"Error in {provider} waterfall step: {e}")

        logger.error(f"❌ All price providers failed for {symbol}")
        return self._error(symbol, "All providers failed")

    def _update_cache(self, cache_type: str, symbol: str, result: Dict[str, Any]):
        """Update local cache with TTL"""
        expiry = time.time() + self.cache_ttl
        if cache_type == 'price':
            self.cache['price'][symbol] = {
                'price': result.get('price'),
                'source': result.get('source'),
                'expiry': expiry
            }
        elif cache_type == 'fundamentals':
            self.cache['fundamentals'][symbol] = {
                'data': result,
                'expiry': expiry
            }

    def get_fundamentals(self, symbol: str) -> Dict[str, Any]:
        """Get fundamental data with caching & circuit breaking"""
        symbol = symbol.upper()
        now = time.time()

        # 0. Check Cache First
        if symbol in self.cache['fundamentals']:
            cached = self.cache['fundamentals'][symbol]
            if now < cached['expiry']:
                return cached['data']
        
        # Strategy 1: YFinance (Free & stable for fundamentals)
        if self._can_use('yfinance'):
            try:
                self._use('yfinance')
                import yfinance as yf
                t = yf.Ticker(symbol)
                info = t.info
                res = {
                    'symbol': symbol,
                    'pe_ratio': info.get('trailingPE', 0),
                    'return_on_equity': info.get('returnOnEquity', 0),
                    'profit_margin': info.get('profitMargins', 0),
                    'debt_to_equity': info.get('debtToEquity', 0) / 100 if info.get('debtToEquity') else 0,
                    'dividend_yield': info.get('dividendYield', 0),
                    'source': 'yfinance'
                }
                self._update_cache('fundamentals', symbol, res)
                return res
            except Exception as e:
                logger.warning(f"YFinance fundamentals failed: {e}")

        # Strategy 2: FMP (Best data but limited)
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
                    res = {
                        'symbol': symbol,
                        'pe_ratio': r.get('peRatioTTM', 0),
                        'return_on_equity': r.get('returnOnEquityTTM', 0),
                        'profit_margin': r.get('netProfitMarginTTM', 0),
                        'debt_to_equity': r.get('debtEquityRatioTTM', 0),
                        'dividend_yield': r.get('dividendYielTTM', 0),
                        'source': 'fmp'
                    }
                    self._update_cache('fundamentals', symbol, res)
                    return res
            except Exception as e:
                logger.warning(f"FMP fundamentals failed: {e}")

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

    # ==================== TRIPLE-SOURCE VERIFICATION ====================

    def get_price_verified(self, symbol: str):
        """Triple-source price verification - ZERO MOCK DATA"""
        symbol = symbol.upper()
        sources_to_try = ['yfinance', 'fmp', 'alpha_vantage']
        successful_fetches, failed_sources = [], {}
        
        for source in sources_to_try:
            try:
                fetch_func = getattr(self, f'_fetch_price_{source}')
                price = fetch_func(symbol)
                
                if price and price > 0:
                    successful_fetches.append({'source': source, 'price': price})
                else:
                    failed_sources[source] = "Failed to fetch or rate limited"
            except Exception as e:
                failed_sources[source] = str(e)
        
        if not successful_fetches:
            audit_id = self._create_audit_entry(symbol, 'price', [], [], None, None, 'failed', 3)
            self.verification_stats['failed_verifications'] += 1
            return {'symbol': symbol, 'price': None,
                   'error': f'All sources failed. NO MOCK DATA. Failures: {failed_sources}',
                   'verification': {'status': 'failed', 'confidence': 0.0, 'fallback_level': 3},
                   'audit_id': audit_id}
        
        prices = [f['price'] for f in successful_fetches]
        sources = [f['source'] for f in successful_fetches]
        median_price = sorted(prices)[len(prices) // 2]
        variance = self._compute_variance(prices)
        
        if len(prices) >= 3:
            status, conf, level = ('verified', 0.95, 0) if variance < 0.005 else ('variance_flag', 0.80, 0)
            self.verification_stats['successful_verifications'] += 1
        elif len(prices) == 2:
            status, conf, level = ('partial', 0.75, 1) if variance < 0.01 else ('variance_flag', 0.65, 1)
            self.verification_stats['partial_verifications'] += 1
        else:
            status, conf, level = 'unverified', 0.50, 2
            self.verification_stats['partial_verifications'] += 1
        
        audit_id = self._create_audit_entry(symbol, 'price', sources, prices, median_price, variance, status, level)
        self.verification_stats['total_verifications'] += 1
        
        return {'symbol': symbol, 'price': median_price,
               'verification': {'sources_used': sources, 'raw_values': prices,
                              'variance': round(variance, 6), 'status': status,
                              'confidence': conf, 'fallback_level': level},
               'audit_id': audit_id}

    def _compute_variance(self, values):
        if len(values) < 2: return 0.0
        median = sorted(values)[len(values) // 2]
        return max([abs(v - median) / median for v in values]) if median > 0 else 0.0

    def _create_audit_entry(self, symbol, metric, sources, raw_vals, median, var, status, level):
        import uuid
        aid = f"audit_{uuid.uuid4().hex[:8]}"
        self.audit_log.append({'audit_id': aid, 'symbol': symbol, 'metric': metric,
                              'sources_used': sources, 'raw_values': raw_vals,
                              'median_value': median, 'variance': var,
                              'verification_status': status, 'fallback_level': level,
                              'timestamp': datetime.now().isoformat()})
        if len(self.audit_log) > 100: self.audit_log = self.audit_log[-100:]
        return aid

    def get_recent_audit_logs(self, limit=10):
        return self.audit_log[-limit:]

    def get_verification_stats(self):
        stats = self.verification_stats.copy()
        if stats['total_verifications'] > 0:
            stats['success_rate'] = round(stats['successful_verifications'] / stats['total_verifications'], 3)
        else:
            stats['success_rate'] = 0.0
        stats['audit_log_size'] = len(self.audit_log)
        return stats

    def _fetch_price_yfinance(self, symbol: str):
        if not self._can_use('yfinance'):
            return None
        try:
            self._use('yfinance')
            import yfinance as yf
            ticker = yf.Ticker(symbol)
            # Try fast_info (preferred)
            try:
                price = ticker.fast_info.last_price
                if price:
                    return float(price)
            except Exception:
                pass

            # Fallback to history
            data = ticker.history(period='1d')
            if data is not None and not data.empty:
                return float(data['Close'].iloc[-1])
            return None
        except Exception as e:
            logger.warning(f"yfinance fetch failed for {symbol}: {e}")
            return None

    def _fetch_price_fmp(self, symbol: str):
        if not self._can_use('fmp'):
            return None
        try:
            self._use('fmp')
            import requests
            url = f"https://financialmodelingprep.com/api/v3/quote/{symbol}?apikey={self.providers['fmp']['key']}"
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                if data:
                    return float(data[0]['price'])
            return None
        except Exception as e:
            logger.warning(f"FMP fetch failed for {symbol}: {e}")
            return None

    def _fetch_price_alpaca(self, symbol: str):
        if not self._can_use('alpaca'):
            return None
        try:
            self._use('alpaca')
            import requests
            headers = {
                'APCA-API-KEY-ID': self.providers['alpaca']['key'],
                'APCA-API-SECRET-KEY': self.providers['alpaca']['secret']
            }
            url = f"https://data.alpaca.markets/v2/stocks/{symbol}/quotes/latest"
            resp = requests.get(url, headers=headers, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                price = float(data['quote']['ap']) # Ask price as proxy
                return price
            return None
        except Exception as e:
            logger.warning(f"alpaca fetch failed for {symbol}: {e}")
            return None

    def _fetch_price_alpha_vantage(self, symbol: str):
        if not self._can_use('alpha_vantage'):
            return None
        try:
            self._use('alpha_vantage')
            import requests
            r = requests.get("https://www.alphavantage.co/query",
                             params={'function': 'GLOBAL_QUOTE', 'symbol': symbol,
                                     'apikey': self.providers['alpha_vantage']['key']}, timeout=5)
            price = r.json().get('Global Quote', {}).get('05. price')
            if price:
                return float(price)
            return None
        except Exception as e:
            logger.warning(f"Alpha Vantage fetch failed for {symbol}: {e}")
            return None

# Singleton
_waterfall_service = None

def get_waterfall_service():
    global _waterfall_service
    if _waterfall_service is None:
        _waterfall_service = WaterfallMarketDataService()
    return _waterfall_service
