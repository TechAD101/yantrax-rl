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
                      'neutral_flat', 'mean_reversion_bounce'
        """
        self._scenario = scenario
        self._base_price = 150.0
        self._source = 'synthetic_test_fixture'

    def get_stock_price(self, symbol: str) -> Dict[str, Any]:
        """Get current synthetic price with full market data."""
        symbol = symbol.upper()

        if self._scenario == 'bullish_mean_reversion':
            # Mean-reversion bounce: 60 days decline RSI=0 (oversold), trend=bullish
            # This triggers: RSI<30=oversold, sentiment=0.68>0.6, fundamental=0.80>0.6
            # Result: bullish_count(1) > bearish_count(0) → BUY signal
            price = 41.0
            change_pct = 3.0
            trend = 'bullish'  # BULL_MARKET regime: bullish trend + greed > 0.6
        elif self._scenario == 'bearish_decline':
            # Bearish decline scenario for closing positions
            # Price is collapsing with bearish technical signals
            price = 50.0
            change_pct = -2.5
            trend = 'bearish'
        elif self._scenario == 'mean_reversion_bounce':
            # Sharp decline with recovery and pullback
            price = 80.0
            change_pct = 2.0
            trend = 'bullish'
        else:
            price = self._base_price
            change_pct = 0.0
            trend = 'neutral'

        return {
            'symbol': symbol,
            'price': price,
            'change_percent': change_pct,
            'volume': 15000000,  # High volume for conviction
            'volatility': 0.03,
            'trend': trend,
            'price_history': self.get_price_history(symbol, days=60),
            'source': self._source,
            'verified': True,
        }
    
    def get_price_history(self, symbol: str, days: int = 60) -> List[Dict[str, Any]]:
        """Get deterministic price history for technical analysis."""
        history = []

        if self._scenario == 'bullish_mean_reversion':
            # Mean-reversion bounce: 60 days steady decline from 100 to 40
            # All losses in last 14 periods → RSI < 30 (oversold)
            for i in range(60):
                price = 100.0 - (i * 1.0)  # 40 at end
                history.append({'close': round(price, 2)})
        elif self._scenario == 'bearish_decline':
            # Bearish decline: price falling with bearish EMA crossover
            # Start from 100, decline steadily to 50
            # EMA9 will stay below EMA21 (bearish crossover)
            # RSI will show overbought initially, then neutral/bearish
            for i in range(60):
                price = 100.0 - (i * 0.83)  # ~50 at end
                history.append({'close': round(price, 2)})
        elif self._scenario == 'mean_reversion_bounce':
            # 40 days decline from 100 to ~60
            for i in range(40):
                price = 100.0 - (1.0 * i)
                history.append({'close': round(price, 2)})
            # 15 days recovery to ~85
            for i in range(15):
                price = history[-1]['close'] + 1.7
                history.append({'close': round(price, 2)})
            # 5 days slight pullback to ~80
            for i in range(5):
                price = history[-1]['close'] - 1.0
                history.append({'close': round(price, 2)})
        else:
            # Default flat price
            for i in range(60):
                history.append({'close': round(self._base_price, 2)})

        return history[-days:]
    
    def get_fundamentals(self, symbol: str) -> Dict[str, Any]:
        """Get synthetic fundamentals."""
        if self._scenario == 'bearish_decline':
            # Bearish fundamentals for bearish scenario
            return {
                'pe_ratio': 8.0,  # Low P/E = distressed
                'return_on_equity': 0.05,  # Low ROE
                'debt_to_equity': 0.8,  # High debt
                'revenue_growth': -0.15,  # Negative growth
                'earnings_growth': -0.20,  # Negative earnings growth
                'profit_margin': 0.05,  # Low margin
            }
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
    
    def get_comprehensive_sentiment(self, symbol: str) -> Dict[str, Any]:
        """Get comprehensive sentiment data matching the market scenario.
        
        This method allows SyntheticMarketProvider to serve as both
        market data provider AND sentiment service for the canonical pipeline.
        """
        symbol = symbol.upper()
        
        # Scenario-specific sentiment that aligns with market regime for genuine BUY/SELL signals
        if self._scenario == 'bullish_mean_reversion':
            fear_greed_index = 0.70  # GREED territory - triggers BULL_MARKET regime
            composite_sentiment = 0.68  # Slightly below 0.7 to keep recommendation valid
        elif self._scenario == 'mean_reversion_bounce':
            fear_greed_index = 0.65  # GREED territory - triggers BULL_MARKET regime
            composite_sentiment = 0.68
        elif self._scenario == 'bearish_decline':
            # Bearish sentiment for SELL signal
            fear_greed_index = 0.25  # FEAR territory - triggers BEAR_MARKET regime
            composite_sentiment = 0.28  # Below 0.35 for SELL recommendation
        else:
            fear_greed_index = 0.50
            composite_sentiment = 0.55
        
        # Recommendation derived from composite_sentiment
        if composite_sentiment >= 0.65:
            recommendation = 'BUY'
        elif composite_sentiment <= 0.35:
            recommendation = 'SELL'
        else:
            recommendation = 'HOLD'
        
        return {
            'symbol': symbol,
            'composite_sentiment': composite_sentiment,
            'recommendation': recommendation,
            'confidence': 0.75,
            'components': {
                'fear_greed': {
                    'fear_greed_index': fear_greed_index,
                },
                'options_flow': {
                    'flow_score': composite_sentiment,
                    'signal': 'NET_LONG' if composite_sentiment > 0.5 else 'NET_SHORT',
                },
                'social_sentiment': {
                    'overall_sentiment': composite_sentiment,
                    'signal': 'BULLISH' if composite_sentiment > 0.5 else 'BEARISH',
                },
            },
            'source': self._source,
        }


def get_synthetic_market_provider(scenario: str = 'bullish_mean_reversion') -> SyntheticMarketProvider:
    """Factory function for synthetic provider."""
    return SyntheticMarketProvider(scenario=scenario)