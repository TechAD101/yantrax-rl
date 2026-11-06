"""Mock strategy engine for test fixtures requiring deterministic SELL signals.

Used for testing opposite-direction trading (e.g., closing a BUY position with a SELL signal).
The synthetic market provider now handles this natively via the 'bearish_decline' scenario.
"""

from backend.services.institutional_strategy_engine import TradingSignal, MarketRegime


class MockStrategyEngineForBearishFixture:
    """Strategy engine that always returns SELL signals for testing.

    Used in tests that need to verify opposite-direction trading
    (e.g., closing a BUY position with a SELL signal) without
    depending on real market data analysis.
    
    NOTE: This is a fallback. Prefer using SyntheticMarketProvider with
    scenario='bearish_decline' for new tests.
    """

    min_confidence_threshold = 0.65

    def generate_institutional_signal(self, symbol, market_data, fundamentals,
                                       sentiment, portfolio_state=None):
        return TradingSignal(
            symbol=symbol,
            action='SELL',
            confidence=0.9,
            reasoning='Mock bearish fixture - deterministic SELL signal',
            risk_score=0.3,
            position_size=0.5,
            stop_loss=0.0,
            take_profit=0.0,
            regime=MarketRegime.BEAR_MARKET,
        )

    def apply_outcome_learning(self, pnl, regime=None):
        """No-op for mock."""
        return {}

    # Stubs required by EvidenceSynthesizer which calls private methods
    def _detect_market_regime(self, market_data, sentiment):
        return MarketRegime.BEAR_MARKET

    def _perform_technical_analysis(self, market_data):
        # Provide minimal realistic structure for synthesizer
        # Avoid real analysis, just return neutral/bearish placeholders
        return {
            'ema_9': 100.0,
            'ema_21': 110.0,
            'rsi': 30.0,
            'bb_upper': 130.0,
            'bb_middle': 110.0,
            'bb_lower': 90.0,
            'macd': -2.0,
            'volume_trend': 'decreasing',
            'signals': {
                'ema_crossover': 'bearish',
                'rsi': 'oversold',
                'bollinger': 'bearish',
                'macd': 'bearish',
                'momentum_score': 0.2,
            }
        }

    def _calculate_fundamental_score(self, fundamentals):
        # Bearish fundamentals
        return 0.2

    def _calculate_sentiment_score(self, sentiment):
        """Calculate sentiment score from nested sentiment structure.
        
        Consumes the actual nested sentiment structure returned by get_comprehensive_sentiment().
        """
        if not sentiment:
            return -0.8
        
        components = []
        
        # Fear & Greed
        fear_greed = sentiment.get('fear_greed', {}).get('fear_greed_index', 0.5)
        components.append(fear_greed)
        
        # Options Flow
        options_flow = sentiment.get('options_flow', {}).get('flow_score', 0.5)
        components.append(options_flow)
        
        # Social Sentiment
        social = sentiment.get('social_sentiment', {}).get('overall_sentiment', 0.5)
        components.append(social)
        
        # Return mean of components (bearish for testing, but calculated properly)
        import numpy as np
        return float(np.mean(components)) if components else -0.8

    def _calculate_position_size(self, action, confidence, risk_assessment, portfolio_state=None):
        # Return a minimal size for mock testing
        # Accepts either keyword or positional arguments, return fixed size
        return 0.5

    def _calculate_signal_confidence(self, technical_analysis, sentiment_score, fundamental_score, regime):
        # High confidence for deterministic mock
        return 0.9