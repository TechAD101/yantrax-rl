"""Market-data adapter for the canonical pipeline (god-cycle convergence).

Wraps the v2 real-provider price service and yfinance history/fundamentals
into the canonical provider interface:

    MarketDataProvider
     ├── get_stock_price()
     ├── get_price_history()
     ├── get_fundamentals()
     └── (options/market_status added with broker adapters)

Real data only — every method raises on failure so the pipeline fails closed
with explicit provenance instead of substituting synthetic values.
"""
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class CanonicalMarketProvider:
    """Real market-data provider for the canonical DecisionPipeline."""

    def __init__(self, price_service: Optional[Any] = None):
        from backend.services.market_data_service_v2 import MarketDataService, MarketDataConfig
        self._price_service = price_service or MarketDataService(MarketDataConfig())
        self._source = 'v2_market_data_service'

    def get_stock_price(self, symbol: str) -> Dict[str, Any]:
        quote = self._price_service.get_stock_price(symbol)
        if not quote or not quote.get('price') or quote.get('price', 0) <= 0:
            raise ValueError(f"No usable price for {symbol}")
        quote.setdefault('source', 'real_market_data')
        return quote

    def get_price_history(self, symbol: str, days: int = 60) -> List[Dict[str, Any]]:
        """Real daily closes via yfinance (no synthetic fill)."""
        import yfinance as yf
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=f"{max(days, 60)}d")
        if hist is None or hist.empty or len(hist) < 50:
            raise ValueError(f"Real price history unavailable for {symbol}")
        closes = [
            {'close': float(row['Close']), 'date': str(idx.date())}
            for idx, row in hist.iterrows()
        ]
        return closes[-days:]

    def get_fundamentals(self, symbol: str) -> Dict[str, Any]:
        """Real fundamentals via yfinance info. Raises on unavailability."""
        import yfinance as yf
        info = yf.Ticker(symbol).info or {}
        fundamentals = {
            'pe_ratio': info.get('trailingPE'),
            'return_on_equity': info.get('returnOnEquity'),
            'debt_to_equity': info.get('debtToEquity'),
            'revenue_growth': info.get('revenueGrowth'),
            'earnings_growth': info.get('earningsGrowth'),
            'profit_margin': info.get('profitMargins'),
            'dividend_yield': info.get('dividendYield'),
        }
        if not fundamentals.get('pe_ratio'):
            raise ValueError(f"Real fundamentals unavailable for {symbol}")
        return fundamentals


def get_canonical_market_provider() -> 'CanonicalMarketProvider':
    return CanonicalMarketProvider()
