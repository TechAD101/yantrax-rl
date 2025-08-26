# ai_agents/degen_auditor.py - Enhanced Risk Assessment and Trade Auditing Agent
import numpy as np
import random
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
import logging
import math

logger = logging.getLogger(__name__)

class DegenAuditorAgent:
    """
    Enhanced Degen Auditor - Advanced Risk Assessment and Trade Validation
    """

    def __init__(self):
        self.audit_history = []
        self.risk_metrics_cache = {}
        self.portfolio_tracker = PortfolioRiskTracker()
        self.risk_models = {
            "var": VaRCalculator(),
            "drawdown": DrawdownAnalyzer(),
            "sharpe": SharpeRatioCalculator(),
            "volatility": VolatilityAnalyzer()
        }

        # Risk thresholds (configurable)
        self.risk_thresholds = {
            "max_position_size": 0.25,  # 25% of portfolio
            "max_daily_var": 0.05,      # 5% daily VaR
            "max_drawdown": 0.20,       # 20% max drawdown
            "min_sharpe_ratio": 0.5,    # Minimum Sharpe ratio
            "max_volatility": 0.60,     # Maximum volatility threshold
            "correlation_limit": 0.80   # Maximum correlation with market
        }

        # Dynamic risk adjustment factors
        self.risk_adjustment_factors = {
            "market_regime": 1.0,
            "volatility_regime": 1.0,
            "liquidity_factor": 1.0,
            "correlation_factor": 1.0
        }

    def audit_trade(self, signal: str, market_data: Optional[Dict] = None) -> str:
        """
        Enhanced trade auditing with comprehensive risk assessment
        """
        try:
            logger.info(f"[Degen Auditor] Auditing trade signal: {signal}")

            # 1. Parse and validate signal
            parsed_signal = self._parse_signal(signal)
            if not parsed_signal:
                return "REJECTED - Invalid Signal"

            # 2. Comprehensive risk assessment
            risk_assessment = self._comprehensive_risk_assessment(parsed_signal, market_data or {})

            # 3. Portfolio impact analysis
            portfolio_impact = self.portfolio_tracker.analyze_impact(parsed_signal, market_data or {})

            # 4. Market condition analysis
            market_conditions = self._analyze_market_conditions(market_data or {})

            # 5. Generate audit decision with detailed reasoning
            audit_decision = self._generate_audit_decision(
                risk_assessment, portfolio_impact, market_conditions, parsed_signal
            )

            # 6. Calculate overall risk score
            risk_score = self._calculate_overall_risk_score(risk_assessment, portfolio_impact)

            # 7. Apply dynamic risk adjustments
            adjusted_decision = self._apply_dynamic_adjustments(audit_decision, market_conditions, risk_score)

            # 8. Log comprehensive audit trail
            self._log_audit_trail(parsed_signal, adjusted_decision, risk_assessment, risk_score)

            # 9. Update audit history and learning
            self._update_audit_history(parsed_signal, adjusted_decision, risk_score, market_data or {})

            logger.info(f"[Degen Auditor] Audit result: {adjusted_decision} (Risk Score: {risk_score:.2f})")

            return adjusted_decision

        except Exception as e:
            logger.error(f"[Degen Auditor] Audit error: {str(e)}")
            return "REJECTED - Audit Error"

    def audit_risk(self, trade_data: Dict) -> Dict:
        """
        Enhanced risk analysis with multiple risk models
        """
        try:
            risk_analysis = {
                "timestamp": datetime.now().isoformat(),
                "overall_risk_level": "UNKNOWN",
                "risk_score": 0.0,
                "risk_factors": {},
                "recommendations": [],
                "alerts": []
            }

            # Calculate individual risk metrics
            risk_metrics = {}

            # Value at Risk (VaR) calculation
            var_result = self.risk_models["var"].calculate_var(trade_data)
            risk_metrics["var"] = var_result

            # Drawdown analysis
            drawdown_result = self.risk_models["drawdown"].analyze_drawdown(trade_data)
            risk_metrics["drawdown"] = drawdown_result

            # Sharpe ratio calculation
            sharpe_result = self.risk_models["sharpe"].calculate_sharpe(trade_data)
            risk_metrics["sharpe"] = sharpe_result

            # Volatility analysis
            volatility_result = self.risk_models["volatility"].analyze_volatility(trade_data)
            risk_metrics["volatility"] = volatility_result

            # Aggregate risk assessment
            risk_analysis = self._aggregate_risk_assessment(risk_metrics, trade_data)

            # Generate actionable recommendations
            risk_analysis["recommendations"] = self._generate_risk_recommendations(risk_analysis)

            return risk_analysis

        except Exception as e:
            logger.error(f"[Degen Auditor] Risk analysis error: {str(e)}")
            return {
                "error": str(e),
                "overall_risk_level": "HIGH",
                "risk_score": 1.0,
                "recommendations": ["Avoid trading due to analysis error"]
            }

    def _parse_signal(self, signal: str) -> Optional[Dict]:
        """Parse and validate trading signal"""
        if not signal or not isinstance(signal, str):
            return None

        signal_upper = signal.upper()

        # Advanced signal parsing
        signal_mapping = {
            # Buy signals
            "BUY": {"action": "BUY", "confidence": "MEDIUM", "urgency": "NORMAL"},
            "CONFIDENT BUY": {"action": "BUY", "confidence": "HIGH", "urgency": "NORMAL"},
            "AGGRESSIVE_BUY": {"action": "BUY", "confidence": "HIGH", "urgency": "HIGH"},
            "FEARLESS_BUY": {"action": "BUY", "confidence": "VERY_HIGH", "urgency": "HIGH"},
            "CRISIS_BUY": {"action": "BUY", "confidence": "HIGH", "urgency": "MEDIUM"},
            "CONTRARIAN_BUY": {"action": "BUY", "confidence": "MEDIUM", "urgency": "LOW"},
            "DCA_BUY": {"action": "BUY", "confidence": "MEDIUM", "urgency": "LOW"},
            "CAUTIOUS_BUY": {"action": "BUY", "confidence": "LOW", "urgency": "LOW"},

            # Sell signals
            "SELL": {"action": "SELL", "confidence": "MEDIUM", "urgency": "NORMAL"},
            "CAUTIOUS SELL": {"action": "SELL", "confidence": "LOW", "urgency": "LOW"},
            "IMMEDIATE_SELL": {"action": "SELL", "confidence": "VERY_HIGH", "urgency": "VERY_HIGH"},
            "EMERGENCY_SELL": {"action": "SELL", "confidence": "VERY_HIGH", "urgency": "VERY_HIGH"},
            "SMART_PROFIT_SELL": {"action": "SELL", "confidence": "HIGH", "urgency": "MEDIUM"},
            "CONTRARIAN_SELL": {"action": "SELL", "confidence": "MEDIUM", "urgency": "MEDIUM"},

            # Hold/Wait signals
            "HOLD": {"action": "HOLD", "confidence": "MEDIUM", "urgency": "NONE"},
            "WAIT": {"action": "HOLD", "confidence": "MEDIUM", "urgency": "NONE"},
            "DEFENSIVE_HOLD": {"action": "HOLD", "confidence": "HIGH", "urgency": "NONE"},
            "STRATEGIC_WAIT": {"action": "HOLD", "confidence": "HIGH", "urgency": "NONE"}
        }

        for pattern, details in signal_mapping.items():
            if pattern in signal_upper:
                return {
                    "original_signal": signal,
                    "parsed_signal": pattern,
                    **details
                }

        # Default parsing for unknown signals
        return {
            "original_signal": signal,
            "parsed_signal": signal_upper,
            "action": "HOLD",
            "confidence": "LOW",
            "urgency": "NONE"
        }

    def _comprehensive_risk_assessment(self, parsed_signal: Dict, market_data: Dict) -> Dict:
        """Perform comprehensive risk assessment"""
        risk_factors = {}

        # 1. Signal-based risk assessment
        action = parsed_signal.get("action", "HOLD")
        confidence = parsed_signal.get("confidence", "LOW")
        urgency = parsed_signal.get("urgency", "NONE")

        signal_risk = self._assess_signal_risk(action, confidence, urgency)
        risk_factors["signal_risk"] = signal_risk

        # 2. Market condition risk
        market_risk = self._assess_market_risk(market_data)
        risk_factors["market_risk"] = market_risk

        # 3. Volatility risk
        volatility = market_data.get("volatility", 0.02)
        volatility_risk = min(1.0, volatility * 2.5)  # Scale volatility to risk score
        risk_factors["volatility_risk"] = volatility_risk

        # 4. Liquidity risk
        volume = market_data.get("volume", 0)
        liquidity_risk = self._assess_liquidity_risk(volume)
        risk_factors["liquidity_risk"] = liquidity_risk

        # 5. Correlation risk
        correlation_risk = self._assess_correlation_risk(market_data)
        risk_factors["correlation_risk"] = correlation_risk

        # 6. Timing risk
        timing_risk = self._assess_timing_risk(urgency, market_data)
        risk_factors["timing_risk"] = timing_risk

        return risk_factors

    def _assess_signal_risk(self, action: str, confidence: str, urgency: str) -> float:
        """Assess risk based on signal characteristics"""
        # Base risk by action
        action_risk = {"BUY": 0.6, "SELL": 0.4, "HOLD": 0.1}.get(action, 0.5)

        # Confidence adjustment
        confidence_multiplier = {
            "VERY_HIGH": 0.7, "HIGH": 0.8, "MEDIUM": 1.0, "LOW": 1.3
        }.get(confidence, 1.0)

        # Urgency adjustment
        urgency_multiplier = {
            "VERY_HIGH": 1.4, "HIGH": 1.2, "MEDIUM": 1.0, "LOW": 0.9, "NONE": 0.8
        }.get(urgency, 1.0)

        return min(1.0, action_risk * confidence_multiplier * urgency_multiplier)

    def _assess_market_risk(self, market_data: Dict) -> float:
        """Assess market condition risk"""
        trend = market_data.get("trend", "sideways")
        sentiment = market_data.get("sentiment", "neutral")
        price = market_data.get("price", 0)

        # Trend risk
        trend_risk_map = {
            "strong_bearish": 0.9, "bearish": 0.7, "sideways": 0.4,
            "bullish": 0.5, "strong_bullish": 0.6
        }
        trend_risk = trend_risk_map.get(trend, 0.5)

        # Sentiment risk
        sentiment_risk_map = {
            "very_bearish": 0.8, "bearish": 0.6, "neutral": 0.3,
            "bullish": 0.4, "very_bullish": 0.7  # Extreme bullish can be risky
        }
        sentiment_risk = sentiment_risk_map.get(sentiment, 0.5)

        # Price level risk
        if price > 60000 or price < 5000:  # Extreme price levels
            price_risk = 0.8
        elif price > 50000 or price < 10000:
            price_risk = 0.6
        else:
            price_risk = 0.3

        return (trend_risk * 0.4 + sentiment_risk * 0.3 + price_risk * 0.3)

    def _assess_liquidity_risk(self, volume: int) -> float:
        """Assess liquidity risk based on volume"""
        if volume < 500000:  # Very low volume
            return 0.9
        elif volume < 1000000:  # Low volume
            return 0.7
        elif volume < 5000000:  # Medium volume
            return 0.4
        else:  # High volume
            return 0.2

    def _assess_correlation_risk(self, market_data: Dict) -> float:
        """Assess correlation risk with broader market"""
        # Simplified correlation risk assessment
        # In production, this would analyze correlation with major indices
        sentiment = market_data.get("sentiment", "neutral")
        trend = market_data.get("trend", "sideways")

        # High correlation risk when following market sentiment/trend strongly
        if sentiment in ["very_bullish", "very_bearish"] and trend in ["strong_bullish", "strong_bearish"]:
            return 0.8  # High correlation risk
        else:
            return 0.3  # Lower correlation risk

    def _assess_timing_risk(self, urgency: str, market_data: Dict) -> float:
        """Assess timing risk based on urgency and market conditions"""
        current_hour = datetime.now().hour
        volatility = market_data.get("volatility", 0.02)

        # Market hours timing risk
        if current_hour < 9 or current_hour > 16:  # Outside market hours
            timing_risk = 0.7
        else:
            timing_risk = 0.2

        # Urgency timing risk
        urgency_risk_map = {
            "VERY_HIGH": 0.8,  # Very urgent trades are risky
            "HIGH": 0.6,
            "MEDIUM": 0.4,
            "LOW": 0.3,
            "NONE": 0.2
        }

        urgency_risk = urgency_risk_map.get(urgency, 0.5)

        # Volatility timing risk
        vol_timing_risk = min(0.9, volatility * 3)  # Higher vol = higher timing risk

        return max(timing_risk, urgency_risk, vol_timing_risk)

    def _generate_audit_decision(self, risk_assessment: Dict, portfolio_impact: Dict, 
                               market_conditions: Dict, parsed_signal: Dict) -> str:
        """Generate audit decision based on comprehensive analysis"""

        # Calculate weighted risk score
        risk_weights = {
            "signal_risk": 0.25,
            "market_risk": 0.20,
            "volatility_risk": 0.20,
            "liquidity_risk": 0.15,
            "correlation_risk": 0.10,
            "timing_risk": 0.10
        }

        total_risk = sum(risk_assessment[factor] * weight 
                        for factor, weight in risk_weights.items() 
                        if factor in risk_assessment)

        # Portfolio impact adjustment
        portfolio_risk = portfolio_impact.get("risk_increase", 0)
        adjusted_risk = (total_risk * 0.7 + portfolio_risk * 0.3)

        # Decision matrix based on risk levels
        if adjusted_risk < 0.3:
            return "APPROVED"
        elif adjusted_risk < 0.5:
            return "APPROVED_WITH_CAUTION"
        elif adjusted_risk < 0.7:
            return "CONDITIONAL_APPROVAL"
        else:
            return "REJECTED_HIGH_RISK"

    def _calculate_overall_risk_score(self, risk_assessment: Dict, portfolio_impact: Dict) -> float:
        """Calculate overall risk score (0-1)"""
        risk_values = list(risk_assessment.values())
        if not risk_values:
            return 0.5  # Default moderate risk

        # Weighted average of risk factors
        avg_risk = sum(risk_values) / len(risk_values)
        portfolio_risk = portfolio_impact.get("risk_increase", 0)

        # Combined risk score
        overall_risk = (avg_risk * 0.8 + portfolio_risk * 0.2)
        return max(0.0, min(1.0, overall_risk))

    def _apply_dynamic_adjustments(self, decision: str, market_conditions: Dict, risk_score: float) -> str:
        """Apply dynamic risk adjustments based on current conditions"""

        # Market regime adjustments
        market_regime = market_conditions.get("regime", "normal")

        if market_regime == "crisis" and decision == "REJECTED_HIGH_RISK":
            if risk_score < 0.8:  # Allow some trades during crisis
                return "CONDITIONAL_APPROVAL"

        elif market_regime == "low_volatility" and decision == "CONDITIONAL_APPROVAL":
            return "APPROVED_WITH_CAUTION"  # More lenient in stable conditions

        # Time-based adjustments
        current_hour = datetime.now().hour
        if current_hour < 10 or current_hour > 15:  # Market open/close periods
            if decision in ["APPROVED", "APPROVED_WITH_CAUTION"]:
                return "CONDITIONAL_APPROVAL"  # More cautious during volatile periods

        return decision

    def _log_audit_trail(self, parsed_signal: Dict, decision: str, risk_assessment: Dict, risk_score: float):
        """Log comprehensive audit trail"""
        logger.info(f"[Degen Auditor] Audit Trail:")
        logger.info(f"  Signal: {parsed_signal.get('original_signal', 'Unknown')}")
        logger.info(f"  Action: {parsed_signal.get('action', 'Unknown')}")
        logger.info(f"  Confidence: {parsed_signal.get('confidence', 'Unknown')}")
        logger.info(f"  Risk Score: {risk_score:.3f}")
        logger.info(f"  Risk Factors: {', '.join([f'{k}: {v:.2f}' for k, v in risk_assessment.items()])}")
        logger.info(f"  Final Decision: {decision}")

    def _update_audit_history(self, parsed_signal: Dict, decision: str, risk_score: float, market_data: Dict):
        """Update audit history for learning and performance tracking"""
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "signal": parsed_signal.get("original_signal", ""),
            "action": parsed_signal.get("action", ""),
            "decision": decision,
            "risk_score": risk_score,
            "market_price": market_data.get("price", 0),
            "market_volatility": market_data.get("volatility", 0),
            "market_sentiment": market_data.get("sentiment", "")
        }

        self.audit_history.append(audit_entry)

        # Keep only last 100 audit entries
        if len(self.audit_history) > 100:
            self.audit_history.pop(0)

    def _analyze_market_conditions(self, market_data: Dict) -> Dict:
        """Analyze current market conditions for risk assessment"""
        volatility = market_data.get("volatility", 0.02)
        volume = market_data.get("volume", 0)
        sentiment = market_data.get("sentiment", "neutral")

        # Determine market regime
        if volatility > 0.5:
            regime = "crisis"
        elif volatility < 0.15:
            regime = "low_volatility"
        elif volume > 8000000:
            regime = "high_activity"
        else:
            regime = "normal"

        return {
            "regime": regime,
            "volatility_level": "high" if volatility > 0.3 else "normal",
            "liquidity_level": "high" if volume > 5000000 else "low",
            "sentiment_extremity": sentiment in ["very_bullish", "very_bearish"]
        }

    def _aggregate_risk_assessment(self, risk_metrics: Dict, trade_data: Dict) -> Dict:
        """Aggregate multiple risk metrics into overall assessment"""
        risk_scores = []

        # Extract risk scores from different models
        if "var" in risk_metrics and "risk_level" in risk_metrics["var"]:
            var_risk_map = {"LOW": 0.2, "MEDIUM": 0.5, "HIGH": 0.8}
            risk_scores.append(var_risk_map.get(risk_metrics["var"]["risk_level"], 0.5))

        if "sharpe" in risk_metrics and "risk_assessment" in risk_metrics["sharpe"]:
            sharpe_risk_map = {"EXCELLENT": 0.2, "GOOD": 0.3, "FAIR": 0.5, "POOR": 0.8}
            risk_scores.append(sharpe_risk_map.get(risk_metrics["sharpe"]["risk_assessment"], 0.5))

        if "volatility" in risk_metrics and "risk_level" in risk_metrics["volatility"]:
            vol_risk_map = {"LOW": 0.3, "MEDIUM": 0.5, "HIGH": 0.8, "EXTREME": 1.0}
            risk_scores.append(vol_risk_map.get(risk_metrics["volatility"]["risk_level"], 0.5))

        # Calculate overall risk
        overall_risk_score = sum(risk_scores) / len(risk_scores) if risk_scores else 0.5

        # Determine risk level
        if overall_risk_score < 0.3:
            risk_level = "LOW"
        elif overall_risk_score < 0.6:
            risk_level = "MEDIUM"
        else:
            risk_level = "HIGH"

        return {
            "overall_risk_level": risk_level,
            "risk_score": round(overall_risk_score, 3),
            "risk_factors": risk_metrics,
            "alerts": self._generate_risk_alerts(overall_risk_score, risk_metrics)
        }

    def _generate_risk_recommendations(self, risk_analysis: Dict) -> List[str]:
        """Generate actionable risk recommendations"""
        recommendations = []
        risk_score = risk_analysis.get("risk_score", 0.5)
        risk_level = risk_analysis.get("overall_risk_level", "MEDIUM")

        if risk_level == "HIGH":
            recommendations.extend([
                "Consider reducing position size",
                "Implement tighter stop-loss levels",
                "Monitor trade closely for early exit opportunities",
                "Review correlation with existing positions"
            ])
        elif risk_level == "MEDIUM":
            recommendations.extend([
                "Use standard position sizing",
                "Set appropriate stop-loss and take-profit levels",
                "Monitor key risk metrics regularly"
            ])
        else:  # LOW risk
            recommendations.extend([
                "Consider standard or slightly larger position size",
                "Set trailing stops to capture upside",
                "Look for opportunities to add to position"
            ])

        return recommendations

    def _generate_risk_alerts(self, risk_score: float, risk_metrics: Dict) -> List[str]:
        """Generate risk alerts based on analysis"""
        alerts = []

        if risk_score > 0.8:
            alerts.append("CRITICAL: Very high risk detected")
        elif risk_score > 0.6:
            alerts.append("WARNING: High risk level")

        # Specific metric alerts
        for metric_name, metric_data in risk_metrics.items():
            if isinstance(metric_data, dict) and "alert" in metric_data:
                alerts.append(f"{metric_name.upper()}: {metric_data['alert']}")

        return alerts

    def get_audit_summary(self) -> Dict:
        """Get comprehensive audit summary"""
        if not self.audit_history:
            return {"message": "No audit history available"}

        # Calculate audit statistics
        total_audits = len(self.audit_history)
        decisions = [entry["decision"] for entry in self.audit_history]
        risk_scores = [entry["risk_score"] for entry in self.audit_history]

        decision_counts = {}
        for decision in decisions:
            decision_counts[decision] = decision_counts.get(decision, 0) + 1

        return {
            "total_audits": total_audits,
            "average_risk_score": sum(risk_scores) / len(risk_scores),
            "decision_breakdown": decision_counts,
            "approval_rate": (decision_counts.get("APPROVED", 0) + 
                            decision_counts.get("APPROVED_WITH_CAUTION", 0)) / total_audits,
            "recent_audits": self.audit_history[-5:],
            "risk_thresholds": self.risk_thresholds
        }


class PortfolioRiskTracker:
    """Portfolio-level risk tracking and analysis"""

    def __init__(self):
        self.positions = []
        self.max_portfolio_risk = 0.15  # 15% maximum portfolio risk

    def analyze_impact(self, signal: Dict, market_data: Dict) -> Dict:
        """Analyze impact of new trade on portfolio risk"""
        action = signal.get("action", "HOLD")
        current_price = market_data.get("price", 0)

        # Simplified portfolio impact analysis
        if action == "BUY":
            risk_increase = 0.3  # Adding long position increases risk
        elif action == "SELL":
            risk_increase = 0.1  # Reducing positions typically reduces risk
        else:
            risk_increase = 0.0  # No change

        return {
            "risk_increase": risk_increase,
            "portfolio_risk_after": min(1.0, self.max_portfolio_risk + risk_increase),
            "recommendation": "PROCEED" if risk_increase < 0.5 else "REDUCE_SIZE"
        }


# Individual risk model classes
class VaRCalculator:
    """Value at Risk calculation"""

    def calculate_var(self, trade_data: Dict, confidence_level: float = 0.95) -> Dict:
        # Simplified VaR calculation
        volatility = trade_data.get("volatility", 0.02)
        position_size = trade_data.get("position_size", 0.1)

        # Daily VaR estimate
        daily_var = volatility * position_size * 1.645  # 95% confidence interval

        risk_level = "LOW" if daily_var < 0.02 else "MEDIUM" if daily_var < 0.05 else "HIGH"

        return {
            "daily_var": daily_var,
            "confidence_level": confidence_level,
            "risk_level": risk_level,
            "alert": f"Daily VaR: {daily_var:.3f}" if daily_var > 0.03 else None
        }


class DrawdownAnalyzer:
    """Maximum drawdown analysis"""

    def analyze_drawdown(self, trade_data: Dict) -> Dict:
        # Simplified drawdown analysis
        volatility = trade_data.get("volatility", 0.02)
        leverage = trade_data.get("leverage", 1.0)

        # Estimate potential drawdown
        estimated_drawdown = volatility * leverage * 3  # Rough estimate

        risk_level = "LOW" if estimated_drawdown < 0.1 else "MEDIUM" if estimated_drawdown < 0.2 else "HIGH"

        return {
            "estimated_max_drawdown": estimated_drawdown,
            "risk_level": risk_level,
            "alert": f"High drawdown risk: {estimated_drawdown:.1%}" if estimated_drawdown > 0.15 else None
        }


class SharpeRatioCalculator:
    """Sharpe ratio calculation and analysis"""

    def calculate_sharpe(self, trade_data: Dict) -> Dict:
        # Simplified Sharpe ratio estimation
        expected_return = trade_data.get("expected_return", 0.05)  # 5% default
        volatility = trade_data.get("volatility", 0.02)
        risk_free_rate = 0.02  # 2% risk-free rate

        if volatility == 0:
            sharpe_ratio = 0
        else:
            sharpe_ratio = (expected_return - risk_free_rate) / volatility

        if sharpe_ratio > 1.0:
            assessment = "EXCELLENT"
        elif sharpe_ratio > 0.5:
            assessment = "GOOD"
        elif sharpe_ratio > 0:
            assessment = "FAIR"
        else:
            assessment = "POOR"

        return {
            "sharpe_ratio": sharpe_ratio,
            "risk_assessment": assessment,
            "expected_return": expected_return,
            "volatility": volatility
        }


class VolatilityAnalyzer:
    """Volatility analysis and regime detection"""

    def analyze_volatility(self, trade_data: Dict) -> Dict:
        volatility = trade_data.get("volatility", 0.02)

        if volatility < 0.15:
            risk_level = "LOW"
            regime = "Low Volatility"
        elif volatility < 0.30:
            risk_level = "MEDIUM"
            regime = "Normal Volatility"
        elif volatility < 0.50:
            risk_level = "HIGH"
            regime = "High Volatility"
        else:
            risk_level = "EXTREME"
            regime = "Crisis Volatility"

        return {
            "volatility": volatility,
            "risk_level": risk_level,
            "volatility_regime": regime,
            "alert": f"Extreme volatility: {volatility:.1%}" if risk_level == "EXTREME" else None
        }


# Global agent instance
degen_auditor_agent = DegenAuditorAgent()

def audit_trade(signal: str, market_data: Optional[Dict] = None) -> str:
    """
    Main function for trade auditing
    """
    return degen_auditor_agent.audit_trade(signal, market_data)

def audit_risk(trade_data: Dict) -> Dict:
    """
    Main function for risk analysis
    """
    return degen_auditor_agent.audit_risk(trade_data)

def get_audit_summary() -> Dict:
    """Get audit performance summary"""
    return degen_auditor_agent.get_audit_summary()

def reset_auditor_state() -> Dict:
    """Reset auditor state"""
    global degen_auditor_agent
    degen_auditor_agent = DegenAuditorAgent()
    return {"status": "reset_complete", "timestamp": datetime.now().isoformat()}
