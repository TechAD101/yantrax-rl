# ai_agents/the_ghost.py - Enhanced Emotional Intelligence Signal Processor
import numpy as np
import random
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class TheGhostAgent:
    """
    Enhanced The Ghost - Emotional Intelligence and Signal Processing Agent
    """

    def __init__(self):
        self.emotional_state = "balanced"
        self.signal_history = []
        self.emotional_memory = []
        self.market_psychology_model = MarketPsychologyModel()
        self.signal_confidence_tracker = SignalConfidenceTracker()

        # Emotional states and their characteristics
        self.emotional_states = {
            "euphoric": {"risk_tolerance": 0.9, "signal_amplification": 1.3, "confidence_boost": 0.2},
            "optimistic": {"risk_tolerance": 0.7, "signal_amplification": 1.1, "confidence_boost": 0.1},
            "balanced": {"risk_tolerance": 0.5, "signal_amplification": 1.0, "confidence_boost": 0.0},
            "cautious": {"risk_tolerance": 0.3, "signal_amplification": 0.9, "confidence_boost": -0.1},
            "fearful": {"risk_tolerance": 0.1, "signal_amplification": 0.7, "confidence_boost": -0.2}
        }

    def ghost_signal_handler(self, strategy: str, market_data: Optional[Dict] = None) -> str:
        """
        Enhanced emotional intelligence signal processing
        """
        try:
            logger.info(f"[The Ghost] Processing strategy signal: {strategy}")

            # 1. Update emotional state based on market conditions
            if market_data:
                self._update_emotional_state(market_data)

            # 2. Analyze market psychology
            market_psychology = self.market_psychology_model.analyze_psychology(market_data or {})

            # 3. Apply emotional intelligence to strategy
            emotional_strategy = self._apply_emotional_intelligence(strategy, market_psychology)

            # 4. Generate nuanced signal with confidence scoring
            nuanced_signal = self._generate_nuanced_signal(emotional_strategy, market_psychology)

            # 5. Apply market timing filters
            final_signal = self._apply_timing_filters(nuanced_signal, market_data or {})

            # 6. Calculate and track signal confidence
            confidence = self.signal_confidence_tracker.calculate_confidence(
                final_signal, market_psychology, self.emotional_state
            )

            # 7. Log comprehensive reasoning
            self._log_signal_reasoning(strategy, final_signal, confidence, market_psychology)

            # 8. Update signal history
            self._update_signal_history(final_signal, confidence, market_psychology)

            logger.info(f"[The Ghost] Final signal: {final_signal} (Confidence: {confidence:.2f})")

            return final_signal

        except Exception as e:
            logger.error(f"[The Ghost] Signal processing error: {str(e)}")
            return "WAIT"  # Safe default

    def _update_emotional_state(self, market_data: Dict):
        """Update emotional state based on market conditions"""
        volatility = market_data.get("volatility", 0.02)
        trend = market_data.get("trend", "sideways")
        sentiment = market_data.get("sentiment", "neutral")
        price = market_data.get("price", 0)

        # Calculate emotional factors
        fear_factor = min(1.0, volatility * 5)  # High volatility increases fear
        greed_factor = 0.8 if trend in ["strong_bullish", "bullish"] else 0.2
        uncertainty_factor = 0.9 if trend == "sideways" else 0.3

        # Determine new emotional state
        if fear_factor > 0.7:
            new_state = "fearful"
        elif greed_factor > 0.6 and fear_factor < 0.3:
            new_state = "euphoric"
        elif greed_factor > 0.4:
            new_state = "optimistic"
        elif uncertainty_factor > 0.6:
            new_state = "cautious"
        else:
            new_state = "balanced"

        # Emotional state transition with memory
        if new_state != self.emotional_state:
            logger.info(f"[The Ghost] Emotional transition: {self.emotional_state} → {new_state}")
            self.emotional_memory.append({
                "timestamp": datetime.now().isoformat(),
                "from_state": self.emotional_state,
                "to_state": new_state,
                "trigger_factors": {
                    "fear_factor": fear_factor,
                    "greed_factor": greed_factor,
                    "uncertainty_factor": uncertainty_factor
                }
            })
            self.emotional_state = new_state

    def _apply_emotional_intelligence(self, strategy: str, market_psychology: Dict) -> str:
        """Apply emotional intelligence to modify strategy"""
        current_traits = self.emotional_states.get(self.emotional_state, self.emotional_states["balanced"])

        # Emotional modulation of strategy
        if strategy == "BUY":
            if self.emotional_state in ["fearful", "cautious"]:
                return "CAUTIOUS_BUY"
            elif self.emotional_state == "euphoric":
                return "AGGRESSIVE_BUY"
            else:
                return "CONFIDENT_BUY"

        elif strategy == "SELL":
            if self.emotional_state in ["fearful", "cautious"]:
                return "EMERGENCY_SELL"
            elif self.emotional_state == "euphoric":
                return "PROFIT_TAKING_SELL"
            else:
                return "CAUTIOUS_SELL"

        else:  # HOLD
            if self.emotional_state == "fearful":
                return "DEFENSIVE_WAIT"
            elif self.emotional_state == "euphoric":
                return "PATIENT_WAIT"
            else:
                return "WAIT"

    def _generate_nuanced_signal(self, emotional_strategy: str, market_psychology: Dict) -> str:
        """Generate nuanced signal based on emotional strategy and market psychology"""
        crowd_sentiment = market_psychology.get("crowd_sentiment", "neutral")
        fear_greed_index = market_psychology.get("fear_greed_index", 50)
        market_regime = market_psychology.get("market_regime", "normal")

        # Signal mapping with psychological context
        signal_map = {
            "AGGRESSIVE_BUY": self._handle_aggressive_buy(fear_greed_index, crowd_sentiment),
            "CONFIDENT_BUY": self._handle_confident_buy(fear_greed_index, market_regime),
            "CAUTIOUS_BUY": self._handle_cautious_buy(crowd_sentiment, market_regime),
            "EMERGENCY_SELL": "IMMEDIATE_SELL",
            "PROFIT_TAKING_SELL": self._handle_profit_taking(fear_greed_index),
            "CAUTIOUS_SELL": self._handle_cautious_sell(crowd_sentiment),
            "DEFENSIVE_WAIT": "DEFENSIVE_HOLD",
            "PATIENT_WAIT": "STRATEGIC_WAIT",
            "WAIT": "WAIT"
        }

        return signal_map.get(emotional_strategy, "WAIT")

    def _handle_aggressive_buy(self, fear_greed_index: float, crowd_sentiment: str) -> str:
        """Handle aggressive buy signals with crowd psychology"""
        if fear_greed_index > 80 and crowd_sentiment == "very_bullish":
            return "CONTRARIAN_HOLD"  # Too much greed, be contrarian
        elif fear_greed_index < 20:
            return "FEARLESS_BUY"  # Buy when others are fearful
        else:
            return "MOMENTUM_BUY"

    def _handle_confident_buy(self, fear_greed_index: float, market_regime: str) -> str:
        """Handle confident buy signals"""
        if market_regime == "crisis" and fear_greed_index < 30:
            return "CRISIS_BUY"  # Opportunity buying in crisis
        elif market_regime == "bull_run":
            return "TREND_BUY"
        else:
            return "CONFIDENT_BUY"

    def _handle_cautious_buy(self, crowd_sentiment: str, market_regime: str) -> str:
        """Handle cautious buy signals"""
        if crowd_sentiment == "very_bearish" and market_regime != "crisis":
            return "CONTRARIAN_BUY"  # Contrarian when crowd is very bearish
        else:
            return "DCA_BUY"  # Dollar-cost averaging approach

    def _handle_profit_taking(self, fear_greed_index: float) -> str:
        """Handle profit taking decisions"""
        if fear_greed_index > 75:
            return "SMART_PROFIT_SELL"  # Take profits when greed is high
        else:
            return "PARTIAL_PROFIT_SELL"

    def _handle_cautious_sell(self, crowd_sentiment: str) -> str:
        """Handle cautious sell signals"""
        if crowd_sentiment == "very_bullish":
            return "CONTRARIAN_SELL"  # Sell when crowd is very bullish
        else:
            return "CAUTIOUS_SELL"

    def _apply_timing_filters(self, signal: str, market_data: Dict) -> str:
        """Apply market timing filters to signals"""
        current_hour = datetime.now().hour
        volatility = market_data.get("volatility", 0.02)
        volume = market_data.get("volume", 0)

        # Market hours consideration (assuming US market focus)
        if current_hour < 9 or current_hour > 16:  # Outside market hours
            if signal in ["IMMEDIATE_SELL", "EMERGENCY_SELL"]:
                return signal  # Allow emergency actions
            else:
                return "WAIT_FOR_MARKET"  # Wait for market open

        # High volatility filter
        if volatility > 0.5 and signal not in ["EMERGENCY_SELL", "DEFENSIVE_HOLD"]:
            logger.warning("[The Ghost] High volatility detected, applying caution filter")
            return "VOLATILE_WAIT"

        # Low volume filter
        if volume < 1000000 and signal in ["MOMENTUM_BUY", "TREND_BUY"]:
            return "LOW_VOLUME_WAIT"  # Don't chase momentum on low volume

        return signal

    def _log_signal_reasoning(self, original_strategy: str, final_signal: str, confidence: float, psychology: Dict):
        """Log detailed signal processing reasoning"""
        logger.info(f"[The Ghost] Signal Processing Analysis:")
        logger.info(f"  Original Strategy: {original_strategy}")
        logger.info(f"  Emotional State: {self.emotional_state}")
        logger.info(f"  Market Psychology: {psychology.get('crowd_sentiment', 'unknown')}")
        logger.info(f"  Fear/Greed Index: {psychology.get('fear_greed_index', 'N/A')}")
        logger.info(f"  Final Signal: {final_signal}")
        logger.info(f"  Signal Confidence: {confidence:.2f}")

    def _update_signal_history(self, signal: str, confidence: float, psychology: Dict):
        """Update signal history for performance tracking"""
        self.signal_history.append({
            "timestamp": datetime.now().isoformat(),
            "signal": signal,
            "confidence": confidence,
            "emotional_state": self.emotional_state,
            "market_psychology": psychology
        })

        # Keep only last 50 signals
        if len(self.signal_history) > 50:
            self.signal_history.pop(0)

    def get_emotional_analysis(self) -> Dict:
        """Get current emotional analysis"""
        return {
            "current_emotional_state": self.emotional_state,
            "emotional_traits": self.emotional_states[self.emotional_state],
            "recent_transitions": self.emotional_memory[-5:] if self.emotional_memory else [],
            "signal_history_summary": {
                "total_signals": len(self.signal_history),
                "recent_signals": [s["signal"] for s in self.signal_history[-5:]]
            }
        }


class MarketPsychologyModel:
    """
    Advanced market psychology analysis model
    """

    def analyze_psychology(self, market_data: Dict) -> Dict:
        """Analyze current market psychology"""
        sentiment = market_data.get("sentiment", "neutral")
        volatility = market_data.get("volatility", 0.02)
        volume = market_data.get("volume", 0)
        price = market_data.get("price", 0)
        trend = market_data.get("trend", "sideways")

        # Calculate fear/greed index (0-100)
        fear_greed_index = self._calculate_fear_greed_index(volatility, sentiment, trend)

        # Determine crowd sentiment
        crowd_sentiment = self._analyze_crowd_sentiment(sentiment, volatility, volume)

        # Detect market regime
        market_regime = self._detect_market_regime(volatility, trend, fear_greed_index)

        # Calculate psychological indicators
        psychological_indicators = {
            "panic_level": min(100, volatility * 200),
            "euphoria_level": 80 if sentiment == "very_bullish" and trend == "strong_bullish" else 20,
            "uncertainty_level": 70 if trend == "sideways" else 30,
            "herd_mentality": self._calculate_herd_mentality(sentiment, volume)
        }

        return {
            "fear_greed_index": fear_greed_index,
            "crowd_sentiment": crowd_sentiment,
            "market_regime": market_regime,
            "psychological_indicators": psychological_indicators
        }

    def _calculate_fear_greed_index(self, volatility: float, sentiment: str, trend: str) -> float:
        """Calculate fear/greed index (0 = Extreme Fear, 100 = Extreme Greed)"""
        base_score = 50  # Neutral

        # Volatility component (high volatility = fear)
        volatility_score = max(0, 50 - (volatility * 100))

        # Sentiment component
        sentiment_scores = {
            "very_bearish": 10, "bearish": 25, "neutral": 50,
            "bullish": 75, "very_bullish": 90
        }
        sentiment_score = sentiment_scores.get(sentiment, 50)

        # Trend component
        trend_scores = {
            "strong_bearish": 15, "bearish": 30, "sideways": 50,
            "bullish": 70, "strong_bullish": 85
        }
        trend_score = trend_scores.get(trend, 50)

        # Weighted average
        fear_greed = (volatility_score * 0.4 + sentiment_score * 0.35 + trend_score * 0.25)
        return max(0, min(100, fear_greed))

    def _analyze_crowd_sentiment(self, sentiment: str, volatility: float, volume: int) -> str:
        """Analyze crowd sentiment with volume confirmation"""
        high_volume_threshold = 5000000

        if volume > high_volume_threshold:  # High volume confirms sentiment
            if sentiment in ["very_bullish", "bullish"]:
                return "very_bullish"
            elif sentiment in ["very_bearish", "bearish"]:
                return "very_bearish"

        return sentiment

    def _detect_market_regime(self, volatility: float, trend: str, fear_greed: float) -> str:
        """Detect current market regime"""
        if volatility > 0.5 or fear_greed < 20:
            return "crisis"
        elif trend in ["strong_bullish", "bullish"] and fear_greed > 70:
            return "bull_run"
        elif trend in ["strong_bearish", "bearish"] and fear_greed < 30:
            return "bear_market"
        elif volatility < 0.15 and 40 < fear_greed < 60:
            return "accumulation"
        else:
            return "normal"

    def _calculate_herd_mentality(self, sentiment: str, volume: int) -> float:
        """Calculate herd mentality strength (0-1)"""
        # High volume with extreme sentiment indicates strong herd behavior
        volume_factor = min(1.0, volume / 10000000)  # Normalize volume

        sentiment_extremity = {
            "very_bearish": 0.9, "very_bullish": 0.9,
            "bearish": 0.6, "bullish": 0.6,
            "neutral": 0.1
        }

        sentiment_factor = sentiment_extremity.get(sentiment, 0.1)

        return min(1.0, volume_factor * sentiment_factor)


class SignalConfidenceTracker:
    """
    Track and calculate signal confidence based on multiple factors
    """

    def calculate_confidence(self, signal: str, market_psychology: Dict, emotional_state: str) -> float:
        """Calculate confidence score for signal (0-1)"""
        base_confidence = 0.5

        # Signal type confidence
        signal_confidence_map = {
            "FEARLESS_BUY": 0.9,
            "CRISIS_BUY": 0.8,
            "CONTRARIAN_BUY": 0.8,
            "CONFIDENT_BUY": 0.7,
            "TREND_BUY": 0.7,
            "MOMENTUM_BUY": 0.6,
            "DCA_BUY": 0.6,
            "SMART_PROFIT_SELL": 0.8,
            "CONTRARIAN_SELL": 0.7,
            "IMMEDIATE_SELL": 0.9,
            "WAIT": 0.4,
            "DEFENSIVE_HOLD": 0.6
        }

        signal_conf = signal_confidence_map.get(signal, 0.5)

        # Market psychology confidence
        fear_greed = market_psychology.get("fear_greed_index", 50)
        psychology_conf = 0.8 if fear_greed < 30 or fear_greed > 70 else 0.5  # More confident at extremes

        # Emotional state confidence
        emotional_conf_map = {
            "balanced": 0.7,
            "cautious": 0.6,
            "optimistic": 0.6,
            "fearful": 0.8,  # High confidence in fear-based decisions
            "euphoric": 0.4   # Low confidence in euphoric decisions
        }

        emotional_conf = emotional_conf_map.get(emotional_state, 0.5)

        # Weighted confidence calculation
        final_confidence = (signal_conf * 0.4 + psychology_conf * 0.35 + emotional_conf * 0.25)

        return max(0.1, min(1.0, final_confidence))


# Global agent instance
the_ghost_agent = TheGhostAgent()

def ghost_signal_handler(strategy: str, market_data: Optional[Dict] = None) -> str:
    """
    Main function for The Ghost emotional intelligence signal processing
    """
    return the_ghost_agent.ghost_signal_handler(strategy, market_data)

def get_ghost_emotional_analysis() -> Dict:
    """Get The Ghost emotional analysis"""
    return the_ghost_agent.get_emotional_analysis()

def reset_ghost_state() -> Dict:
    """Reset The Ghost state"""
    global the_ghost_agent
    the_ghost_agent = TheGhostAgent()
    return {"status": "reset_complete", "timestamp": datetime.now().isoformat()}
