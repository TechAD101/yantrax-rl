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
                last_resp = requests.get(stock_url, params={'apiKey': self.api_key}, timeout=self.timeout)
                if last_resp.ok:
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

                    return {
                        'symbol': symbol,
                        'price': round(float(price), 2) if price is not None else None,
                        'bid': None,
                        'ask': None,
                        'timestamp': ts_iso,
                        'source': 'polygon',
                        'raw': data
                    }

                # 2) Try forex endpoint if symbol looks like EURUSD (6 chars)
                if len(symbol) == 6 and symbol.isalpha():
                    frm = symbol[:3]
                    to = symbol[3:]
                    forex_url = f"https://api.polygon.io/v1/last/forex/{frm}/{to}"
                    last_resp = requests.get(forex_url, params={'apiKey': self.api_key}, timeout=self.timeout)
                    if last_resp.ok:
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
                        return {
                            'symbol': symbol,
                            'price': round(float(price), 6) if price is not None else None,
                            'bid': None,
                            'ask': None,
                            'timestamp': ts_iso,
                            'source': 'polygon',
                            'raw': data
                        }

                # 3) Try crypto last (assume USD pair if simple symbol given)
                # If symbol like BTC or ETH, query BTC/USD
                crypto_pair = None
                if len(symbol) <= 4 and symbol.isalpha():
                    crypto_pair = (symbol, 'USD')
                elif len(symbol) >= 6 and symbol.endswith('USD'):
                    crypto_pair = (symbol[:-3], 'USD')

                if crypto_pair:
                    crypto_url = f"https://api.polygon.io/v1/last/crypto/{crypto_pair[0]}/{crypto_pair[1]}"
                    last_resp = requests.get(crypto_url, params={'apiKey': self.api_key}, timeout=self.timeout)
                    if last_resp.ok:
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
                        return {
                            'symbol': symbol,
                            'price': round(float(price), 2) if price is not None else None,
                            'bid': None,
                            'ask': None,
                            'timestamp': ts_iso,
                            'source': 'polygon',
                            'raw': data
                        }

                # If none of the above succeeded, raise with last response info
                if last_resp is not None and not last_resp.ok:
                    logger.error(f"Polygon requests failed: status={last_resp.status_code}, body={last_resp.text[:200]}")
                    raise RuntimeError(f"Polygon API error: {last_resp.status_code}: {last_resp.text[:200]}")
                else:
                    # Generic unknown failure
                    logger.error("Polygon API: unknown failure for symbol {symbol}")
                    raise RuntimeError("Polygon API: unknown failure")

            else:
                # Provider with base_url: use generic quote endpoint
                resp = requests.get(url, params=params, timeout=self.timeout)
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
            raise
