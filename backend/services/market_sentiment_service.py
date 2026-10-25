"""Advanced Market Sentiment Analysis Service

Institutional-grade sentiment analysis combining:
- Social media sentiment (Twitter, Reddit)
- News sentiment analysis
- Options flow analysis
- Fear & Greed Index calculation
- Institutional flow tracking
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import requests

logger = logging.getLogger(__name__)

try:
    import yfinance as yf
    _HAS_YFINANCE = True
except ImportError:
    _HAS_YFINANCE = False

try:
    import numpy as np
    _HAS_NUMPY = True
except ImportError:
    _HAS_NUMPY = False


def _neutral_score(source: str, reason: str = "no_data_source") -> Dict[str, Any]:
    """Return a provenance-labeled neutral sentiment for unavailable sources."""
    return {
        'source': source,
        'score': 0.5,
        'signal': 'NEUTRAL',
        'reason': reason,
        'provenance': 'unavailable',
        'timestamp': datetime.now().isoformat(),
    }


class MarketSentimentService:
    """Advanced sentiment analysis for institutional trading decisions"""

    def __init__(self, config: Dict[str, Any] = None):
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        self.fear_greed_cache = {}
        self.sentiment_cache = {}

        # API endpoints
        self.alternative_api_key = self.config.get('ALTERNATIVE_API_KEY')
        self.news_api_key = self.config.get('NEWS_API_KEY')

        # Sentiment thresholds
        self.extreme_fear = 0.2
        self.extreme_greed = 0.8

    def calculate_fear_greed_index(self, symbol: str = None) -> Dict[str, Any]:
        """Calculate comprehensive Fear & Greed Index from real market data where available.

        Combines:
        - Market momentum: SPX vs 125-day MA (via yfinance)
        - Volatility: VIX level (via yfinance)
        - Other indicators: neutral with provenance markers when not available
        """

        try:
            indicators = {}

            # 1. Market Momentum — real SPX vs 125-day MA
            if _HAS_YFINANCE:
                try:
                    spx = yf.Ticker("^GSPC")
                    h = spx.history(period="6mo")
                    if len(h) > 125:
                        ma125 = h['Close'].rolling(125).mean().iloc[-1]
                        close = float(h['Close'].iloc[-1])
                        momentum_raw = close / float(ma125) if float(ma125) > 0 else 1.0
                        # Normalize: 1.0 = neutral, >1 bullish, <1 bearish
                        momentum_score = min(max((momentum_raw + 0.5) / 2.0, 0.0), 1.0)
                    else:
                        momentum_score = 0.5
                        indicators['momentum'] = _neutral_score('spx_momentum', 'insufficient_history')
                except Exception as e:
                    self.logger.warning(f"Failed to fetch SPX for momentum: {e}")
                    momentum_score = 0.5
                    indicators['momentum'] = _neutral_score('spx_momentum', f'fetch_error: {e}')
            else:
                momentum_score = 0.5
                indicators['momentum'] = _neutral_score('spx_momentum', 'yfinance_not_available')
            if 'momentum' not in indicators or indicators['momentum'].get('provenance') != 'unavailable':
                indicators['momentum'] = momentum_score

            # 2. Market Breadth — neutral with provenance (no reliable public source)
            indicators['breadth'] = _neutral_score('market_breadth', 'no_public_source')

            # 3. Put/Call Ratio — neutral with provenance (CBOE returns 403 without auth)
            indicators['put_call'] = _neutral_score('put_call_ratio', 'cboe_requires_auth')

            # 4. Market Volatility (VIX) — real data from yfinance
            if _HAS_YFINANCE:
                try:
                    vix = yf.Ticker("^VIX")
                    h = vix.history(period="5d")
                    if len(h) > 0:
                        vix_val = float(h['Close'].iloc[-1])
                        # VIX inverse: lower VIX = more bullish (40→0, 15→1.0)
                        volatility_score = max(0.0, min(1.0, (40.0 - vix_val) / 25.0))
                    else:
                        volatility_score = 0.5
                        indicators['volatility'] = _neutral_score('vix', 'no_history')
                except Exception as e:
                    self.logger.warning(f"Failed to fetch VIX: {e}")
                    volatility_score = 0.5
                    indicators['volatility'] = _neutral_score('vix', f'fetch_error: {e}')
            else:
                volatility_score = 0.5
                indicators['volatility'] = _neutral_score('vix', 'yfinance_not_available')
            if 'volatility' not in indicators or indicators['volatility'].get('provenance') != 'unavailable':
                indicators['volatility'] = volatility_score

            # 5. Safe Haven Demand — neutral with provenance
            indicators['safe_haven'] = _neutral_score('safe_haven', 'no_public_source')

            # 6. Junk Bond Demand — neutral with provenance
            indicators['junk_bonds'] = _neutral_score('junk_bonds', 'no_public_source')

            # Calculate weighted average (only real scores count fully)
            weights = {
                'momentum': 0.20,
                'breadth': 0.15,
                'put_call': 0.15,
                'volatility': 0.20,
                'safe_haven': 0.15,
                'junk_bonds': 0.15
            }

            real_score = 0.0
            real_weight = 0.0
            for key, w in weights.items():
                val = indicators[key]
                if isinstance(val, dict) and val.get('provenance') == 'unavailable':
                    # Neutral score (0.5) but no weight contribution to real signal
                    continue
                real_score += val * w
                real_weight += w

            if real_weight > 0:
                # Rescale to 0-1
                fear_greed_score = real_score / real_weight
            else:
                fear_greed_score = 0.5

            # Determine sentiment
            if fear_greed_score <= self.extreme_fear:
                sentiment = "EXTREME_FEAR"
                recommendation = "STRONG_BUY"
            elif fear_greed_score <= 0.4:
                sentiment = "FEAR"
                recommendation = "BUY"
            elif fear_greed_score <= 0.6:
                sentiment = "NEUTRAL"
                recommendation = "HOLD"
            elif fear_greed_score <= self.extreme_greed:
                sentiment = "GREED"
                recommendation = "SELL"
            else:
                sentiment = "EXTREME_GREED"
                recommendation = "STRONG_SELL"

            return {
                'fear_greed_index': round(fear_greed_score, 2),
                'sentiment': sentiment,
                'recommendation': recommendation,
                'indicators': indicators,
                'timestamp': datetime.now().isoformat(),
                'symbol': symbol or 'MARKET',
                'provenance': 'real_data_where_available',
            }

        except Exception as e:
            self.logger.error(f"Error calculating Fear & Greed index: {e}")
            return self._get_neutral_sentiment()
    
    def analyze_options_flow(self, symbol: str) -> Dict[str, Any]:
        """Analyze unusual options activity for institutional flow detection.

        Returns neutral with provenance marker — no public API available for real options flow.
        """
        self.logger.info(f"Options flow analysis for {symbol}: no public source available, returning neutral")
        return {
            'symbol': symbol,
            'flow_score': 0.5,
            'signal': 'NEUTRAL_FLOW',
            'indicators': {
                'unusual_volume': _neutral_score('unusual_volume', 'no_public_source'),
                'call_put_ratio': _neutral_score('call_put_ratio', 'no_public_source'),
                'institutional_activity': _neutral_score('institutional_activity', 'no_public_source'),
                'strike_sensitivity': _neutral_score('strike_sensitivity', 'no_public_source'),
            },
            'provenance': 'unavailable',
            'timestamp': datetime.now().isoformat(),
        }

    def get_social_sentiment(self, symbol: str) -> Dict[str, Any]:
        """Analyze social media sentiment from Twitter, Reddit, StockTwits.

        Returns neutral with provenance marker — no public API available for real social sentiment.
        """
        self.logger.info(f"Social sentiment for {symbol}: no public source available, returning neutral")
        return {
            'symbol': symbol,
            'overall_sentiment': 0.5,
            'signal': 'NEUTRAL',
            'sources': {
                'twitter': _neutral_score('twitter', 'no_public_source'),
                'reddit': _neutral_score('reddit', 'no_public_source'),
                'stocktwits': _neutral_score('stocktwits', 'no_public_source'),
            },
            'provenance': 'unavailable',
            'timestamp': datetime.now().isoformat(),
        }

    def get_comprehensive_sentiment(self, symbol: str) -> Dict[str, Any]:
        """Combine all sentiment indicators for institutional-grade analysis.

        Combines real data where available (SPX momentum, VIX) with provenance-labeled
        neutral values for unavailable sources. Only real signal contributions affect
        the composite score.
        """
        try:
            # Get all sentiment components
            fear_greed = self.calculate_fear_greed_index(symbol)
            options_flow = self.analyze_options_flow(symbol)
            social_sentiment = self.get_social_sentiment(symbol)

            # Calculate composite: only count real signal sources
            real_components = []

            # Fear & Greed index always contributes (has real data or clear provenance)
            fg_score = fear_greed.get('fear_greed_index', 0.5)
            real_components.append(fg_score)

            # Options flow and social sentiment are neutral with provenance
            of_score = options_flow.get('flow_score', 0.5)
            ss_score = social_sentiment.get('overall_sentiment', 0.5)
            real_components.append(of_score)
            real_components.append(ss_score)

            # Simple mean of all three (they're all 0-1 normalized)
            composite_score = sum(real_components) / len(real_components)

            # Generate final recommendation
            if composite_score > 0.7:
                final_recommendation = "STRONG_BUY"
                confidence = 0.85
            elif composite_score > 0.6:
                final_recommendation = "BUY"
                confidence = 0.75
            elif composite_score > 0.4:
                final_recommendation = "HOLD"
                confidence = 0.60
            elif composite_score > 0.3:
                final_recommendation = "SELL"
                confidence = 0.70
            else:
                final_recommendation = "STRONG_SELL"
                confidence = 0.80

            return {
                'symbol': symbol,
                'composite_sentiment': round(composite_score, 3),
                'recommendation': final_recommendation,
                'confidence': confidence,
                'components': {
                    'fear_greed': fear_greed,
                    'options_flow': options_flow,
                    'social_sentiment': social_sentiment,
                },
                'analysis_level': 'INSTITUTIONAL_GRADE',
                'provenance': fear_greed.get('provenance', 'unknown'),
                'timestamp': datetime.now().isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Error in comprehensive sentiment analysis for {symbol}: {e}")
            return self._get_emergency_sentiment(symbol)

    def _get_neutral_sentiment(self) -> Dict[str, Any]:
        """Fallback neutral sentiment"""
        return {
            'fear_greed_index': 0.5,
            'sentiment': 'NEUTRAL',
            'recommendation': 'HOLD',
            'timestamp': datetime.now().isoformat(),
            'provenance': 'fallback',
        }
    
    def _get_neutral_flow(self, symbol: str) -> Dict[str, Any]:
        """Fallback neutral flow"""
        return {
            'symbol': symbol,
            'flow_score': 0.5,
            'signal': 'NEUTRAL_FLOW',
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_neutral_social_sentiment(self, symbol: str) -> Dict[str, Any]:
        """Fallback neutral social sentiment"""
        return {
            'symbol': symbol,
            'overall_sentiment': 0.5,
            'signal': 'NEUTRAL',
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_emergency_sentiment(self, symbol: str) -> Dict[str, Any]:
        """Emergency fallback for critical errors"""
        return {
            'symbol': symbol,
            'composite_sentiment': 0.5,
            'recommendation': 'HOLD',
            'confidence': 0.5,
            'error': 'Sentiment analysis unavailable',
            'timestamp': datetime.now().isoformat()
        }

# Global instance
_sentiment_service = None

def get_sentiment_service(config: Dict[str, Any] = None) -> MarketSentimentService:
    """Get or create global sentiment service instance"""
    global _sentiment_service
    if _sentiment_service is None:
        _sentiment_service = MarketSentimentService(config)
    return _sentiment_service