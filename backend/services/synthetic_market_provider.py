"""Synthetic market data provider for deterministic testing.

This provider supplies deterministic market data for testing the canonical
decision pipeline without requiring yfinance or external market data.

Used by integration tests to verify the full pipeline works correctly.
"""
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class SyntheticMarketProvider:
    """Deterministic market data provider for testing.
    
    Provides consistent price history, fundamentals, and current prices
    that trigger specific trading signals for comprehensive pipeline testing.
    """
    
    def __init__(self, scenario: str = 'bullish_mean_reversion'):
        """Initialize the synthetic provider with a scenario.

        Args:
            scenario: One of 'bullish_mean_reversion', 'bearish_decline',
                      'neutral_flat', 'strong_bullish'
        """
        self._scenario = scenario
        self._base_price = 150.0
        self._source = 'synthetic_test_fixture'

    def get_stock_price(self, symbol: str) -> Dict[str, Any]:
        """Get current synthetic price with full market data."""
        symbol = symbol.upper()

        if self._scenario == 'bullish_mean_reversion':
            # Price is at oversold level, primed for bounce
            price = 70.0
            change_pct = 0.8
            trend = 'neutral'
        elif self._scenario == 'bearish_decline':
            # Price is collapsing
            price = 50.0
            change_pct = -2.5
            trend = 'bearish'
        elif self._scenario == 'strong_bullish':
            # Strong uptrend with bullish indicators
            price = 165.0
            change_pct = 2.3
            trend = 'bullish'
        else:
            price = self._base_price
            change_pct = 0.0
            trend = 'neutral'

        return {
            'symbol': symbol,
            'price': price,
            'change_percent': change_pct,
            'volume': 1000000,
            'volatility': 0.02,
            'trend': trend,
            'price_history': self.get_price_history(symbol, days=60),
            'source': self._source,
            'verified': True,
        }
    
    def get_price_history(self, symbol: str, days: int = 60) -> List[Dict[str, Any]]:
        """Get deterministic price history for technical analysis."""
        history = []

        if self._scenario == 'bullish_mean_reversion':
            # 50 days of gentle decline from 100 to ~70
            for i in range(50):
                price = 100.0 - (0.1 * i)
                history.append({'close': round(price, 2)})
            # 10 days of sharp decline to ~45
            for i in range(10):
                price = history[-1]['close'] - 2.5
                history.append({'close': round(price, 2)})
        elif self._scenario == 'strong_bullish':
            # Strong uptrend: gradual rise from 140 to 165 over 60 days
            for i in range(60):
                price = 140.0 + (0.417 * i)  # ~140 to ~165 over 60 days
                history.append({'close': round(price, 2)})
        else:
            # Default flat price
            for i in range(60):
                history.append({'close': round(self._base_price, 2)})

        return history[-days:]
    
    def get_fundamentals(self, symbol: str) -> Dict[str, Any]:
        """Get synthetic fundamentals."""
        return {
            'pe_ratio': 18.0,
            'return_on_equity': 0.25,
            'debt_to_equity': 0.3,
            'revenue_growth': 0.12,
            'earnings_growth': 0.15,
            'profit_margin': 0.22,
        }
    
    def get_price_verified(self, symbol: str) -> Dict[str, Any]:
        """Get verified price info."""
        price_data = self.get_stock_price(symbol)
        return {
            'verified': price_data.get('verified', True),
            'symbol': price_data.get('symbol', symbol.upper()),
            'price': price_data.get('price', 0),
            'source': self._source,
            'error': None,
        }
    
    def get_verification_stats(self) -> Dict[str, Any]:
        """Get provider verification stats."""
        return {
            'provider': self._source,
            'verified': True,
        }
    
    def get_recent_audit_logs(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get synthetic audit logs."""
        return [{'source': 'synthetic', 'type': 'test_fixture', 'verified': True}]


def get_synthetic_market_provider(scenario: str = 'bullish_mean_reversion') -> SyntheticMarketProvider:
    """Factory function for synthetic provider."""
    return SyntheticMarketProvider(scenario=scenario)