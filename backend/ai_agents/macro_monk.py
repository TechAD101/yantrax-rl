# ai_agents/macro_monk.py - Enhanced Strategic Decision Agent
import numpy as np
import random
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class MacroMonkAgent:
    """
    Enhanced Macro Monk - Strategic decision making with ML-powered analysis
    """

    def __init__(self):
        self.decision_history = []
        self.market_regime_memory = []
        self.strategy_performance = {
            "BUY": {"wins": 0, "losses": 0, "total_return": 0.0},
            "SELL": {"wins": 0, "losses": 0, "total_return": 0.0},
            "HOLD": {"wins": 0, "losses": 0, "total_return": 0.0}
        }

        # Strategy weights (adaptive based on performance)
        self.strategy_weights = {
            "trend_following": 0.3,
            "mean_reversion": 0.2,
            "momentum": 0.25,
            "sentiment_driven": 0.15,
            "volatility_breakout": 0.1
        }

        # Market regime classifier
        self.regime_classifier = MarketRegimeClassifier()

    def macro_monk_decision(self, market_data: Dict) -> str:
        """
        Enhanced strategic decision making with multiple ML strategies
        """
        try:
            price = market_data.get("price", 0)
            trend = market_data.get("trend", "sideways")
            volume = market_data.get("volume", 0)
            sentiment = market_data.get("sentiment", "neutral")
            volatility = market_data.get("volatility", 0.02)
            technical_indicators = market_data.get("technical_indicators", {})

            logger.info(f"[Macro Monk] Analyzing market: Price=${price:,.2f}, Trend={trend}, Sentiment={sentiment}")

            # 1. Detect current market regime
            market_regime = self.regime_classifier.classify_regime(market_data)

            # 2. Generate signals from multiple strategies
            strategy_signals = self._generate_strategy_signals(market_data, market_regime)

            # 3. Apply ensemble voting with adaptive weights
            decision = self._ensemble_decision(strategy_signals, market_regime)

            # 4. Apply risk management filters
            final_decision = self._apply_risk_filters(decision, market_data)

            # 5. Update strategy performance tracking
            self._update_performance_tracking(final_decision, market_data)

            # 6. Log decision reasoning
            confidence = self._calculate_decision_confidence(strategy_signals)
            self._log_decision_reasoning(final_decision, market_regime, confidence, strategy_signals)

            logger.info(f"[Macro Monk] Strategic decision: {final_decision} (Confidence: {confidence:.2f})")

            return final_decision

        except Exception as e:
            logger.error(f"[Macro Monk] Decision error: {str(e)}")
            return "HOLD"  # Safe default

    def _generate_strategy_signals(self, market_data: Dict, regime: str) -> Dict[str, str]:
        """Generate signals from multiple trading strategies"""
        signals = {}

        price = market_data.get("price", 0)
        trend = market_data.get("trend", "sideways")
        sentiment = market_data.get("sentiment", "neutral")
        volatility = market_data.get("volatility", 0.02)
        technical_indicators = market_data.get("technical_indicators", {})

        # Strategy 1: Trend Following
        signals["trend_following"] = self._trend_following_strategy(price, trend, technical_indicators)

        # Strategy 2: Mean Reversion
        signals["mean_reversion"] = self._mean_reversion_strategy(price, volatility, technical_indicators)

        # Strategy 3: Momentum Strategy
        signals["momentum"] = self._momentum_strategy(price, market_data.get("volume", 0), technical_indicators)

        # Strategy 4: Sentiment-Driven Strategy
        signals["sentiment_driven"] = self._sentiment_strategy(sentiment, trend)

        # Strategy 5: Volatility Breakout
        signals["volatility_breakout"] = self._volatility_breakout_strategy(price, volatility, regime)

        return signals

    def _trend_following_strategy(self, price: float, trend: str, indicators: Dict) -> str:
        """Trend following strategy with technical indicators"""
        ma_20 = indicators.get("moving_average_20", price)
        ma_50 = indicators.get("moving_average_50", price)

        # Enhanced trend analysis
        if trend in ["strong_bullish", "bullish"] and price > ma_20 and ma_20 > ma_50:
            if price < 60000:  # Don't buy at extreme highs
                return "BUY"
        elif trend in ["strong_bearish", "bearish"] and price < ma_20 and ma_20 < ma_50:
            if price > 5000:  # Don't sell at extreme lows
                return "SELL"

        return "HOLD"

    def _mean_reversion_strategy(self, price: float, volatility: float, indicators: Dict) -> str:
        """Mean reversion strategy for oversold/overbought conditions"""
        rsi = indicators.get("rsi", 50)
        ma_20 = indicators.get("moving_average_20", price)

        # Look for mean reversion opportunities
        price_deviation = abs(price - ma_20) / ma_20

        if rsi < 30 and price_deviation > 0.1:  # Oversold
            return "BUY"
        elif rsi > 70 and price_deviation > 0.1:  # Overbought
            return "SELL"

        return "HOLD"

    def _momentum_strategy(self, price: float, volume: int, indicators: Dict) -> str:
        """Momentum-based strategy using price and volume"""
        macd_signal = indicators.get("macd_signal", "neutral")

        # Volume-confirmed momentum
        volume_threshold = 5000000  # High volume threshold

        if macd_signal == "bullish" and volume > volume_threshold:
            if price < 55000:  # Momentum buy with volume confirmation
                return "BUY"
        elif macd_signal == "bearish" and volume > volume_threshold:
            if price > 10000:  # Momentum sell with volume confirmation
                return "SELL"

        return "HOLD"

    def _sentiment_strategy(self, sentiment: str, trend: str) -> str:
        """Sentiment-based contrarian and momentum strategies"""
        # Contrarian approach for extreme sentiment
        if sentiment == "very_bearish" and trend != "strong_bearish":
            return "BUY"  # Contrarian buy when sentiment is extremely negative
        elif sentiment == "very_bullish" and trend != "strong_bullish":
            return "SELL"  # Contrarian sell when sentiment is extremely positive

        # Momentum approach for moderate sentiment
        elif sentiment == "bullish" and trend in ["bullish", "strong_bullish"]:
            return "BUY"
        elif sentiment == "bearish" and trend in ["bearish", "strong_bearish"]:
            return "SELL"

        return "HOLD"

    def _volatility_breakout_strategy(self, price: float, volatility: float, regime: str) -> str:
        """Volatility breakout strategy"""
        high_vol_threshold = 0.4
        low_vol_threshold = 0.15

        if volatility > high_vol_threshold and regime == "crisis_vol":
            # Crisis buying opportunity
            if price < 20000:
                return "BUY"
        elif volatility < low_vol_threshold and regime == "low_vol":
            # Low volatility - prepare for breakout
            if price > 45000:
                return "SELL"  # Take profits in low vol, high price environment

        return "HOLD"

    def _ensemble_decision(self, strategy_signals: Dict[str, str], regime: str) -> str:
        """Ensemble voting with adaptive weights"""
        # Adjust weights based on market regime
        adjusted_weights = self._adjust_weights_for_regime(regime)

        # Count weighted votes
        vote_scores = {"BUY": 0.0, "SELL": 0.0, "HOLD": 0.0}

        for strategy, signal in strategy_signals.items():
            weight = adjusted_weights.get(strategy, 0.2)
            vote_scores[signal] += weight

        # Return decision with highest weighted vote
        return max(vote_scores, key=vote_scores.get)

    def _adjust_weights_for_regime(self, regime: str) -> Dict[str, float]:
        """Adjust strategy weights based on market regime"""
        weights = self.strategy_weights.copy()

        if regime == "bull_market":
            weights["trend_following"] *= 1.3  # Favor trend following in bull markets
            weights["momentum"] *= 1.2
            weights["mean_reversion"] *= 0.8
        elif regime == "bear_market":
            weights["mean_reversion"] *= 1.4  # Favor mean reversion in bear markets
            weights["sentiment_driven"] *= 1.3
            weights["trend_following"] *= 0.7
        elif regime == "range_bound":
            weights["mean_reversion"] *= 1.5  # Strong mean reversion in range markets
            weights["volatility_breakout"] *= 1.3
            weights["momentum"] *= 0.6

        # Normalize weights
        total_weight = sum(weights.values())
        return {k: v/total_weight for k, v in weights.items()}

    def _apply_risk_filters(self, decision: str, market_data: Dict) -> str:
        """Apply risk management filters to decisions"""
        price = market_data.get("price", 0)
        volatility = market_data.get("volatility", 0.02)

        # Extreme price filters
        if decision == "BUY" and price > 65000:
            logger.warning("[Macro Monk] Risk Filter: Price too high for BUY, switching to HOLD")
            return "HOLD"

        if decision == "SELL" and price < 3000:
            logger.warning("[Macro Monk] Risk Filter: Price too low for SELL, switching to HOLD")
            return "HOLD"

        # Extreme volatility filter
        if volatility > 0.6:
            logger.warning("[Macro Monk] Risk Filter: Extreme volatility detected, switching to HOLD")
            return "HOLD"

        return decision

    def _calculate_decision_confidence(self, strategy_signals: Dict[str, str]) -> float:
        """Calculate confidence level for the decision"""
        signal_counts = {"BUY": 0, "SELL": 0, "HOLD": 0}

        for signal in strategy_signals.values():
            signal_counts[signal] += 1

        total_strategies = len(strategy_signals)
        max_agreement = max(signal_counts.values())

        return max_agreement / total_strategies

    def _update_performance_tracking(self, decision: str, market_data: Dict):
        """Update strategy performance tracking"""
        # Store decision for performance evaluation
        self.decision_history.append({
            "timestamp": datetime.now().isoformat(),
            "decision": decision,
            "price": market_data.get("price", 0),
            "market_data": market_data
        })

        # Keep only last 100 decisions
        if len(self.decision_history) > 100:
            self.decision_history.pop(0)

    def _log_decision_reasoning(self, decision: str, regime: str, confidence: float, signals: Dict):
        """Log detailed decision reasoning"""
        signal_summary = ", ".join([f"{k}: {v}" for k, v in signals.items()])
        logger.info(f"[Macro Monk] Decision Reasoning:")
        logger.info(f"  Market Regime: {regime}")
        logger.info(f"  Strategy Signals: {signal_summary}")
        logger.info(f"  Final Decision: {decision}")
        logger.info(f"  Confidence: {confidence:.2f}")

    def get_performance_summary(self) -> Dict:
        """Get performance summary for the agent"""
        return {
            "total_decisions": len(self.decision_history),
            "strategy_performance": self.strategy_performance,
            "current_weights": self.strategy_weights,
            "recent_decisions": self.decision_history[-10:] if self.decision_history else []
        }


class MarketRegimeClassifier:
    """
    Market regime classification for adaptive strategy selection
    """

    def __init__(self):
        self.regime_history = []

    def classify_regime(self, market_data: Dict) -> str:
        """Classify current market regime"""
        price = market_data.get("price", 0)
        volatility = market_data.get("volatility", 0.02)
        trend = market_data.get("trend", "sideways")
        volume = market_data.get("volume", 0)
        sentiment = market_data.get("sentiment", "neutral")

        # Multi-factor regime classification
        regime_scores = {
            "bull_market": 0.0,
            "bear_market": 0.0,
            "range_bound": 0.0,
            "crisis_mode": 0.0
        }

        # Price-based factors
        if price > 45000:
            regime_scores["bull_market"] += 0.3
        elif price < 15000:
            regime_scores["bear_market"] += 0.3
        else:
            regime_scores["range_bound"] += 0.3

        # Trend-based factors
        if trend in ["strong_bullish", "bullish"]:
            regime_scores["bull_market"] += 0.25
        elif trend in ["strong_bearish", "bearish"]:
            regime_scores["bear_market"] += 0.25
        else:
            regime_scores["range_bound"] += 0.25

        # Volatility-based factors
        if volatility > 0.5:
            regime_scores["crisis_mode"] += 0.4
        elif volatility < 0.2:
            regime_scores["range_bound"] += 0.2
            regime_scores["bull_market"] += 0.1

        # Sentiment-based factors
        if sentiment in ["very_bullish", "bullish"]:
            regime_scores["bull_market"] += 0.15
        elif sentiment in ["very_bearish", "bearish"]:
            regime_scores["bear_market"] += 0.15

        # Volume-based factors (high volume indicates regime changes)
        if volume > 8000000:  # High volume threshold
            regime_scores["crisis_mode"] += 0.1

        # Determine regime
        current_regime = max(regime_scores, key=regime_scores.get)

        # Store regime history
        self.regime_history.append({
            "timestamp": datetime.now().isoformat(),
            "regime": current_regime,
            "confidence": regime_scores[current_regime]
        })

        # Keep only last 50 regime classifications
        if len(self.regime_history) > 50:
            self.regime_history.pop(0)

        return current_regime


# Global agent instance
macro_monk_agent = MacroMonkAgent()

def macro_monk_decision(market_data: Dict) -> str:
    """
    Main function for Macro Monk strategic decision making
    """
    return macro_monk_agent.macro_monk_decision(market_data)

def get_macro_monk_performance() -> Dict:
    """Get Macro Monk performance metrics"""
    return macro_monk_agent.get_performance_summary()

def reset_macro_monk() -> Dict:
    """Reset Macro Monk state"""
    global macro_monk_agent
    macro_monk_agent = MacroMonkAgent()
    return {"status": "reset_complete", "timestamp": datetime.now().isoformat()}
