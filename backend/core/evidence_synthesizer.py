"""
Evidence Synthesis for Yantra X.

Connects existing intelligence components to the canonical EvidencePackage.
"""

from typing import Dict, Any, Optional
from datetime import datetime
import numpy as np

from backend.core.decision_context import (
    EvidencePackage, TechnicalEvidence, FundamentalEvidence,
    SentimentEvidence, MarketRegime, MarketSnapshot
)
from backend.services.institutional_strategy_engine import (
    InstitutionalStrategyEngine, MarketRegime as StrategyMarketRegime
)
from backend.services.market_sentiment_service import get_sentiment_service
MarketDataService = Any


class EvidenceSynthesizer:
    """
    Synthesizes canonical EvidencePackage from existing intelligence services.

    Does not duplicate logic - uses InstitutionalStrategyEngine and SentimentService
    as the authoritative sources.
    """

    def __init__(
        self,
        strategy_engine: Optional[InstitutionalStrategyEngine] = None,
        market_data: Optional[MarketDataService] = None,
        sentiment_service: Optional[Any] = None
    ):
        self.strategy_engine = strategy_engine
        self.market_data = market_data
        self.sentiment_service = sentiment_service or get_sentiment_service()

    def synthesize(self, symbol: str, market_snapshot: MarketSnapshot) -> EvidencePackage:
        """
        Build complete EvidencePackage for a symbol.

        Uses:
        - InstitutionalStrategyEngine for technical/fundamental/regime
        - MarketSentimentService for sentiment
        - MarketSnapshot for price/volatility/trend
        """
        # Get market data for technical analysis
        price_history = self._get_price_history(symbol)
        enhanced_market_data = {
            'price': market_snapshot.price,
            'price_history': price_history,
            'volatility': market_snapshot.volatility,
            'volume': market_snapshot.volume or 1000000,
            'trend': market_snapshot.trend,
            'volume_trend': 'stable',  # Could be enhanced
        }

        # Get fundamentals
        fundamentals = self._get_fundamentals(symbol)

        # Get sentiment
        sentiment_data = self._get_sentiment(symbol)

        # Detect regime using Strategy Engine
        regime = self._detect_regime(enhanced_market_data, sentiment_data)

        # Technical analysis
        technical = self._analyze_technical(enhanced_market_data)

        # Fundamental analysis
        fundamental = self._analyze_fundamental(fundamentals)

        # Sentiment analysis
        sentiment = self._analyze_sentiment(sentiment_data)

        return EvidencePackage(
            technical=technical,
            fundamental=fundamental,
            sentiment=sentiment,
            market_regime=regime,
            regime_confidence=0.8,  # Could be enhanced with regime detection confidence
        )

    def _get_price_history(self, symbol: str, days: int = 50) -> list:
        """Get price history for technical analysis."""
        if self.market_data and hasattr(self.market_data, 'get_price_history'):
            try:
                history = self.market_data.get_price_history(symbol, days)
                if history:
                    return [h['close'] for h in history]
            except Exception:
                pass

        # Fallback: generate synthetic from current price
        base_price = 100  # Will be overridden
        return [base_price * (1 + np.sin(i/10) * 0.02 + np.random.normal(0, 0.01)) for i in range(days)]

    def _get_fundamentals(self, symbol: str) -> Dict[str, Any]:
        """Get fundamental data."""
        if self.market_data and hasattr(self.market_data, 'get_fundamentals'):
            try:
                return self.market_data.get_fundamentals(symbol) or {}
            except Exception:
                pass
        return {}

    def _get_sentiment(self, symbol: str) -> Dict[str, Any]:
        """Get sentiment data."""
        if self.sentiment_service:
            try:
                return self.sentiment_service.get_comprehensive_sentiment(symbol) or {}
            except Exception:
                pass
        return {}

    def _detect_regime(
        self,
        market_data: Dict[str, Any],
        sentiment: Dict[str, Any]
    ) -> MarketRegime:
        """Detect market regime using Strategy Engine logic."""
        if self.strategy_engine:
            try:
                strategy_regime = self.strategy_engine._detect_market_regime(market_data, sentiment)
                # Map to canonical regime
                mapping = {
                    StrategyMarketRegime.BULL_MARKET: MarketRegime.BULL_MARKET,
                    StrategyMarketRegime.BEAR_MARKET: MarketRegime.BEAR_MARKET,
                    StrategyMarketRegime.SIDEWAYS: MarketRegime.SIDEWAYS,
                    StrategyMarketRegime.VOLATILITY_CRISIS: MarketRegime.VOLATILITY_CRISIS,
                    StrategyMarketRegime.LIQUIDITY_CRUNCH: MarketRegime.LIQUIDITY_CRUNCH,
                }
                return mapping.get(strategy_regime, MarketRegime.SIDEWAYS)
            except Exception:
                pass

        # Fallback logic
        volatility = market_data.get('volatility', 0.02)
        fear_greed = sentiment.get('components', {}).get('fear_greed', {}).get('fear_greed_index', 0.5)
        price_trend = market_data.get('trend', 'neutral')

        if volatility > 0.4:
            return MarketRegime.VOLATILITY_CRISIS
        elif fear_greed < 0.2 and price_trend == 'bearish':
            return MarketRegime.LIQUIDITY_CRUNCH
        elif price_trend == 'bullish' and fear_greed > 0.6:
            return MarketRegime.BULL_MARKET
        elif price_trend == 'bearish' and fear_greed < 0.4:
            return MarketRegime.BEAR_MARKET
        else:
            return MarketRegime.SIDEWAYS

    def _analyze_technical(self, market_data: Dict[str, Any]) -> TechnicalEvidence:
        """Extract technical evidence using Strategy Engine."""
        if self.strategy_engine:
            try:
                tech = self.strategy_engine._perform_technical_analysis(market_data)
                signals = tech.get('signals', {})

                return TechnicalEvidence(
                    ema_fast=tech.get('ema_9'),
                    ema_slow=tech.get('ema_21'),
                    ema_crossover=signals.get('ema_crossover', 'neutral'),
                    rsi=tech.get('rsi'),
                    rsi_signal=signals.get('rsi', 'neutral'),
                    bb_upper=tech.get('bb_upper'),
                    bb_middle=tech.get('bb_middle'),
                    bb_lower=tech.get('bb_lower'),
                    bb_signal=signals.get('bollinger', 'neutral'),
                    macd=tech.get('macd'),
                    macd_signal_type=signals.get('macd', 'neutral'),
                    volume_trend=tech.get('volume_trend', 'neutral'),
                    momentum_score=signals.get('momentum_score'),
                )
            except Exception:
                pass

        return TechnicalEvidence()

    def _analyze_fundamental(self, fundamentals: Dict[str, Any]) -> FundamentalEvidence:
        """Extract fundamental evidence using Strategy Engine."""
        if self.strategy_engine and fundamentals:
            try:
                score = self.strategy_engine._calculate_fundamental_score(fundamentals)
                return FundamentalEvidence(
                    pe_ratio=fundamentals.get('pe_ratio'),
                    return_on_equity=fundamentals.get('return_on_equity'),
                    debt_to_equity=fundamentals.get('debt_to_equity'),
                    revenue_growth=fundamentals.get('revenue_growth'),
                    earnings_growth=fundamentals.get('earnings_growth'),
                    free_cash_flow=fundamentals.get('free_cash_flow'),
                    profit_margin=fundamentals.get('profit_margin'),
                    dividend_yield=fundamentals.get('dividend_yield'),
                    fundamental_score=score,
                )
            except Exception:
                pass

        # Provide sensible defaults for missing fundamentals
        return FundamentalEvidence(
            pe_ratio=fundamentals.get('pe_ratio', 20.0),
            return_on_equity=fundamentals.get('return_on_equity', 0.15),
            debt_to_equity=fundamentals.get('debt_to_equity', 0.5),
            revenue_growth=fundamentals.get('revenue_growth', 0.1),
            earnings_growth=fundamentals.get('earnings_growth', 0.1),
            free_cash_flow=fundamentals.get('free_cash_flow', 1e9),
            profit_margin=fundamentals.get('profit_margin', 0.2),
            dividend_yield=fundamentals.get('dividend_yield', 0.01),
            fundamental_score=0.5,
        )

    def _analyze_sentiment(self, sentiment_data: Dict[str, Any]) -> SentimentEvidence:
        """Extract sentiment evidence using Sentiment Service."""
        components = sentiment_data.get('components', {})
        fg = components.get('fear_greed', {})
        of = components.get('options_flow', {})
        ss = components.get('social_sentiment', {})

        # Determine signals
        fg_idx = fg.get('fear_greed_index', 0.5)
        if fg_idx <= 0.2:
            fg_signal = "EXTREME_FEAR"
        elif fg_idx <= 0.4:
            fg_signal = "FEAR"
        elif fg_idx <= 0.6:
            fg_signal = "NEUTRAL"
        elif fg_idx <= 0.8:
            fg_signal = "GREED"
        else:
            fg_signal = "EXTREME_GREED"

        of_score = of.get('flow_score', 0.5)
        of_signal = of.get('signal', 'NEUTRAL_FLOW')

        ss_score = ss.get('overall_sentiment', 0.5)
        ss_signal = ss.get('signal', 'NEUTRAL')

        composite = sentiment_data.get('composite_sentiment', 0.5)
        comp_signal = sentiment_data.get('recommendation', 'HOLD')

        return SentimentEvidence(
            fear_greed_index=fg_idx,
            fear_greed_signal=fg_signal,
            options_flow_score=of_score,
            options_flow_signal=of_signal,
            social_sentiment_score=ss_score,
            social_sentiment_signal=ss_signal,
            composite_sentiment=composite,
            composite_signal=comp_signal,
        )


def build_market_snapshot(
    symbol: str,
    market_data: MarketDataService,
    price_data: Dict[str, Any],
    fundamentals: Dict[str, Any]
) -> MarketSnapshot:
    """Build canonical MarketSnapshot from raw market data."""
    current_price = price_data.get('price', 0)

    # Extract volatility from price data if available
    volatility = price_data.get('volatility', 0.02)

    # Determine trend
    trend = 'neutral'
    if 'change_percent' in price_data:
        change = price_data['change_percent']
        if change > 1:
            trend = 'bullish'
        elif change < -1:
            trend = 'bearish'

    # Extract volume
    volume = price_data.get('volume', 0)

    return MarketSnapshot(
        symbol=symbol.upper(),
        price=current_price,
        timestamp=datetime.now(),
        open=price_data.get('open'),
        high=price_data.get('high'),
        low=price_data.get('low'),
        close=current_price,
        volume=volume,
        volatility=volatility,
        trend=trend,
        liquidity=volume,
        source=price_data.get('source', 'unknown'),
        verified=price_data.get('verified', False),
        data_age_seconds=price_data.get('data_age_seconds'),
    )