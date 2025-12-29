"""
Massive Market Data Service wrapper

Provides a thin, robust client to the Massive Market Data API for equities, crypto,
indices and forex. Designed to be resilient and return normalized payloads.

This is intentionally minimal and defensive — it expects the real API to be
stable and to return JSON with at least a `symbol` and `price` field.
"""

import os
import requests
import logging
import time
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class MassiveMarketDataService:
    """Client for Massive Market Data API

    Configuration:
      MASSIVE_API_KEY - API key (required)
      MASSIVE_BASE_URL - optional base URL override
    """

    def __init__(self, api_key: str | None = None, base_url: str | None = None, timeout: int = 10):
        self.api_key = api_key or os.getenv('MASSIVE_API_KEY')
        # If user explicitly provided base_url, use it. Otherwise default to Polygon
        # because 'Massive' in your setup maps to polygon.io by your note.
        self.base_url = base_url or os.getenv('MASSIVE_BASE_URL')
        self.timeout = timeout

        if not self.api_key:
            raise ValueError('MASSIVE_API_KEY is not configured')

        # Determine provider: 'polygon' by default unless base_url indicates otherwise
        provider_env = os.getenv('MASSIVE_PROVIDER')
        if provider_env:
            self.provider = provider_env.lower()
        elif self.base_url and 'polygon' in (self.base_url or ''):
            self.provider = 'polygon'
        else:
            # default provider is polygon if no explicit base_url provided
            self.provider = 'polygon'

        # lightweight in-memory cache for last known prices (symbol -> dict)
        # used to return a graceful cached response on provider failure
        self._last_prices: Dict[str, Dict[str, Any]] = {}

        # retry config: number of retries for transient errors (timeouts/5xx)
        self._retries = int(os.getenv('MASSIVE_REQUEST_RETRIES', '2'))
        self._backoff = float(os.getenv('MASSIVE_REQUEST_BACKOFF', '0.5'))

    def _request_with_retries(self, method: str, url: str, params: dict | None = None, timeout: int | None = None):
        """Perform an HTTP GET with basic retries on timeouts and 5xx errors.

        Returns the Response object or raises the last exception.
        """
        timeout = timeout or self.timeout
        attempts = 0
        last_exc = None
        while attempts <= self._retries:
            try:
                resp = requests.request(method, url, params=params, timeout=timeout)
                # If server error, try again
                if 500 <= getattr(resp, 'status_code', 0) < 600:
                    last_exc = RuntimeError(f"Server error {resp.status_code}")
                    attempts += 1
                    time.sleep(self._backoff * (2 ** (attempts - 1)))
                    continue
                return resp
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                last_exc = e
                attempts += 1
                time.sleep(self._backoff * (2 ** (attempts - 1)))
                continue
        if last_exc:
            raise last_exc
        raise RuntimeError('Unreachable')

    def fetch_quote(self, symbol: str) -> Dict[str, Any]:
        symbol = (symbol or '').upper()
        if not symbol:
            raise ValueError('symbol is required')

        url = f"{self.base_url}/quote/{symbol}"
        params = {'apikey': self.api_key}

        try:
            # If provider is polygon (default), try polygon's /v1/last endpoints for stock/crypto/forex
            if self.provider == 'polygon':
                last_resp = None
                # 1) Try stock endpoint
                stock_url = f"https://api.polygon.io/v1/last/stocks/{symbol}"
                last_resp = self._request_with_retries('GET', stock_url, params={'apiKey': self.api_key}, timeout=self.timeout)
                if getattr(last_resp, 'ok', False):
                    data = last_resp.json()
                    last = data.get('last') or {}
                    price = last.get('price')
                    ts = last.get('timestamp') or data.get('last', {}).get('timestamp')
                    # Convert numeric timestamp (ms) to ISO if necessary
                    if isinstance(ts, (int, float)):
                        try:
                            ts_iso = datetime.fromtimestamp(ts / 1000.0).isoformat()
                        except Exception:
                            ts_iso = datetime.now().isoformat()
                    else:
                        ts_iso = ts or datetime.now().isoformat()

                    result = {
                        'symbol': symbol,
                        'price': round(float(price), 2) if price is not None else None,
                        'bid': None,
                        'ask': None,
                        'timestamp': ts_iso,
                        'source': 'polygon',
                        'raw': data
                    }
                    self._last_prices[symbol] = result
                    return result

                # 2) Try forex endpoint if symbol looks like EURUSD (6 chars)
                if len(symbol) == 6 and symbol.isalpha():
                    frm = symbol[:3]
                    to = symbol[3:]
                    forex_url = f"https://api.polygon.io/v1/last/forex/{frm}/{to}"
                    last_resp = self._request_with_retries('GET', forex_url, params={'apiKey': self.api_key}, timeout=self.timeout)
                    if getattr(last_resp, 'ok', False):
                        data = last_resp.json()
                        last = data.get('last') or {}
                        price = last.get('price')
                        ts = last.get('timestamp') or data.get('last', {}).get('timestamp')
                        if isinstance(ts, (int, float)):
                            try:
                                ts_iso = datetime.fromtimestamp(ts / 1000.0).isoformat()
                            except Exception:
                                ts_iso = datetime.now().isoformat()
                        else:
                            ts_iso = ts or datetime.now().isoformat()
                        result = {
                            'symbol': symbol,
                            'price': round(float(price), 6) if price is not None else None,
                            'bid': None,
                            'ask': None,
                            'timestamp': ts_iso,
                            'source': 'polygon',
                            'raw': data
                        }
                        self._last_prices[symbol] = result
                        return result

                # 3) Try crypto last (assume USD pair if simple symbol given)
                # If symbol like BTC or ETH, query BTC/USD
                crypto_pair = None
                if len(symbol) <= 4 and symbol.isalpha():
                    crypto_pair = (symbol, 'USD')
                elif len(symbol) >= 6 and symbol.endswith('USD'):
                    crypto_pair = (symbol[:-3], 'USD')

                if crypto_pair:
                    crypto_url = f"https://api.polygon.io/v1/last/crypto/{crypto_pair[0]}/{crypto_pair[1]}"
                    last_resp = self._request_with_retries('GET', crypto_url, params={'apiKey': self.api_key}, timeout=self.timeout)
                    if getattr(last_resp, 'ok', False):
                        data = last_resp.json()
                        last = data.get('last') or {}
                        price = last.get('price')
                        ts = last.get('timestamp') or data.get('last', {}).get('timestamp')
                        if isinstance(ts, (int, float)):
                            try:
                                ts_iso = datetime.fromtimestamp(ts / 1000.0).isoformat()
                            except Exception:
                                ts_iso = datetime.now().isoformat()
                        else:
                            ts_iso = ts or datetime.now().isoformat()
                        result = {
                            'symbol': symbol,
                            'price': round(float(price), 2) if price is not None else None,
                            'bid': None,
                            'ask': None,
                            'timestamp': ts_iso,
                            'source': 'polygon',
                            'raw': data
                        }
                        self._last_prices[symbol] = result
                        return result

                # If none of the above succeeded, raise with last response info
                if last_resp is not None and not last_resp.ok:
                    status = last_resp.status_code
                    text = (last_resp.text or '')[:200]
                    logger.error(f"Polygon requests failed: status={status}, body={text}")

                    # If 403 (NOT_AUTHORIZED), attempt fallbacks: alpha_vantage then yfinance
                    if status == 403:
                        logger.warning('Polygon returned 403 - attempting fallback providers')
                        # try alpha_vantage first
                        try:
                            av_price = self._try_alpha_vantage(symbol)
                            if av_price is not None:
                                result = {
                                    'symbol': symbol,
                                    'price': round(float(av_price), 2),
                                    'timestamp': datetime.now().isoformat(),
                                    'source': 'alpha_vantage',
                                    'fallback_from': 'polygon'
                                }
                                # cache
                                self._last_prices[symbol] = result
                                return result
                        except Exception:
                            logger.exception('Alpha Vantage fallback failed')

                        # try yfinance next
                        try:
                            yf_price = self._try_yfinance(symbol)
                            if yf_price is not None:
                                result = {
                                    'symbol': symbol,
                                    'price': round(float(yf_price), 2),
                                    'timestamp': datetime.now().isoformat(),
                                    'source': 'yfinance',
                                    'fallback_from': 'polygon'
                                }
                                self._last_prices[symbol] = result
                                return result
                        except Exception:
                            logger.exception('YFinance fallback failed')

                        # If we reach here, fallbacks failed. Return structured error dict instead of raising
                        err = {
                            'symbol': symbol,
                            'price': None,
                            'error': {
                                'message': f'Polygon API error: {status}: {text}',
                                'code': status
                            },
                            'timestamp': datetime.now().isoformat(),
                            'source': 'polygon'
                        }
                        # If we have a cached last price, include it in the returned dict as a graceful fallback
                        if symbol in self._last_prices:
                            cached = self._last_prices[symbol]
                            err['cached'] = cached
                        return err
                    else:
                        # For non-403 failures, attempt retries on transient errors
                        logger.warning('Polygon request failed (non-403); will attempt other providers/retries')
                        # fall through to generic fallback below
                        
                else:
                    # Generic unknown failure
                    logger.error("Polygon API: unknown failure for symbol {symbol}")
                    # fall through to fallback attempts below

                # If polygon hasn't returned a usable quote, attempt other providers as a generic fallback
                try:
                    av_price = self._try_alpha_vantage(symbol)
                    if av_price is not None:
                        result = {
                            'symbol': symbol,
                            'price': round(float(av_price), 2),
                            'timestamp': datetime.now().isoformat(),
                            'source': 'alpha_vantage',
                            'fallback_from': 'polygon'
                        }
                        self._last_prices[symbol] = result
                        return result
                except Exception:
                    logger.exception('Alpha Vantage fallback failed')

                try:
                    yf_price = self._try_yfinance(symbol)
                    if yf_price is not None:
                        result = {
                            'symbol': symbol,
                            'price': round(float(yf_price), 2),
                            'timestamp': datetime.now().isoformat(),
                            'source': 'yfinance',
                            'fallback_from': 'polygon'
                        }
                        self._last_prices[symbol] = result
                        return result
                except Exception:
                    logger.exception('YFinance fallback failed')

                # If we have a cached last price, return it
                if symbol in self._last_prices:
                    cached = self._last_prices[symbol]
                    return {
                        'symbol': symbol,
                        'price': cached.get('price'),
                        'timestamp': datetime.now().isoformat(),
                        'source': 'cache',
                        'cached': cached
                    }

                # Last resort: return structured error to caller
                return {
                    'symbol': symbol,
                    'price': None,
                    'error': {
                        'message': 'Polygon and fallback providers failed',
                        'code': last_resp.status_code if last_resp is not None else None
                    },
                    'timestamp': datetime.now().isoformat(),
                    'source': 'polygon'
                }
            else:
                # Provider with base_url: use generic quote endpoint
                resp = self._request_with_retries('GET', url, params=params, timeout=self.timeout)
                if hasattr(resp, 'raise_for_status'):
                    resp.raise_for_status()
                data = resp.json()
                # attempt to extract price
                price = None
                for key in ('price', 'last', 'close', 'mid'):
                    if key in data and data[key] is not None:
                        try:
                            price = float(data[key])
                            break
                        except Exception:
                            continue
                return {
                    'symbol': data.get('symbol', symbol),
                    'price': round(price, 2) if price is not None else None,
                    'bid': data.get('bid'),
                    'ask': data.get('ask'),
                    'timestamp': data.get('timestamp') or datetime.now().isoformat(),
                    'source': self.provider,
                    'raw': data
                }

        except Exception as e:
            logger.error(f"MassiveMarketDataService.fetch_quote failed for {symbol}: {e}")
            # On unexpected exceptions, attempt to return cached data if available
            if symbol in self._last_prices:
                return self._last_prices[symbol]
            raise

    # --- Provider fallback helpers ---
    def _try_alpha_vantage(self, symbol: str) -> float | None:
        """Try Alpha Vantage as a fallback source using GLOBAL_QUOTE."""
        av_key = (os.getenv('ALPHAVANTAGE_API_KEY') or os.getenv('ALPHA_VANTAGE_KEY') or os.getenv('ALPHA_VANTAGE'))
        if not av_key:
            return None
        try:
            url = "https://www.alphavantage.co/query"
            params = {'function': 'GLOBAL_QUOTE', 'symbol': symbol, 'apikey': av_key}
            resp = self._request_with_retries('GET', url, params=params, timeout=5)
            if getattr(resp, 'ok', False):
                data = resp.json()
                quote = data.get('Global Quote', {})
                price_str = quote.get('05. price')
                if price_str:
                    return float(price_str)
        except Exception:
            logger.exception('Alpha Vantage try failed')
        return None

    def _try_yfinance(self, symbol: str) -> float | None:
        """Try yfinance to fetch recent close price."""
        try:
            import yfinance as yf
            ticker = yf.Ticker(symbol)
            data = ticker.history(period='1d')
            if data.empty:
                return None
            price = float(data['Close'].iloc[-1])
            return price
        except Exception:
            logger.exception('YFinance try failed')
            return None
