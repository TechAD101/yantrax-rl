"""Market-data adapter for the canonical pipeline (god-cycle convergence).

Price: yfinance real market data (no synthetic fallback - fail-closed when unavailable).
History + fundamentals: yfinance (real data only - every method raises on failure).

This provider uses yfinance as the single source of truth for all market data,
ensuring consistency across price, history, and fundamentals. No Alpaca dependency.
"""
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class CanonicalMarketProvider:
    """Real market-data provider using yfinance (no synthetic data)."""

    def __init__(self, price_service: Optional[Any] = None):
        import yfinance as yf
        self._yf = yf
        self._source = 'yfinance'

    def get_stock_price(self, symbol: str) -> Dict[str, Any]:
        """Get current price via yfinance. Raises on failure (fail-closed)."""
        ticker = self._yf.Ticker(symbol.upper())
        hist = ticker.history(period='5d')
        
        if hist is None or hist.empty:
            raise ValueError(f"No usable price data for {symbol}")
        
        price = float(hist['Close'].iloc[-1])
        if price <= 0:
            raise ValueError(f"Invalid price for {symbol}: {price}")
        
        # Calculate metrics
        closes = hist['Close'].astype(float)
        returns = closes.pct_change().dropna()
        volatility = float(returns.std()) if len(returns) >= 2 else 0.0
        volume = float(hist['Volume'].iloc[-1]) if 'Volume' in hist.columns else 0.0
        
        change_pct = 0.0
        if len(closes) >= 2 and closes.iloc[0] > 0:
            change_pct = float((closes.iloc[-1] / closes.iloc[0] - 1.0) * 100.0)
        
        return {
            'symbol': symbol.upper(),
            'price': price,
            'change_percent': change_pct,
            'volume': volume,
            'volatility': volatility,
            'trend': 'neutral',  # Will be updated by regime detection
            'source': self._source,
            'verified': True,
            'timestamp': hist.index[-1].isoformat() if hasattr(hist.index[-1], 'isoformat') else str(hist.index[-1]),
        }

    def get_price_history(self, symbol: str, days: int = 60) -> List[Dict[str, Any]]:
        """Real daily closes via yfinance (no synthetic fill)."""
        ticker = self._yf.Ticker(symbol)
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
        ticker = self._yf.Ticker(symbol)
        info = ticker.info or {}
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