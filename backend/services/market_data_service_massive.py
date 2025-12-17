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
        self.base_url = base_url or os.getenv('MASSIVE_BASE_URL', 'https://api.massivemarketdata.example/v1')
        self.timeout = timeout

        if not self.api_key:
            raise ValueError('MASSIVE_API_KEY is not configured')

    def fetch_quote(self, symbol: str) -> Dict[str, Any]:
        symbol = (symbol or '').upper()
        if not symbol:
            raise ValueError('symbol is required')

        url = f"{self.base_url}/quote/{symbol}"
        params = {'apikey': self.api_key}

        try:
            resp = requests.get(url, params=params, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()

            # Normalize response — be defensive about missing keys
            price = None
            for key in ('price', 'last', 'close', 'mid'):
                if key in data and data[key] is not None:
                    try:
                        price = float(data[key])
                        break
                    except Exception:
                        continue

            result = {
                'symbol': data.get('symbol', symbol),
                'price': round(price, 2) if price is not None else None,
                'bid': data.get('bid'),
                'ask': data.get('ask'),
                'timestamp': data.get('timestamp') or datetime.now().isoformat(),
                'source': 'massive',
                'raw': data
            }

            return result
        except Exception as e:
            logger.error(f"MassiveMarketDataService.fetch_quote failed for {symbol}: {e}")
            raise
