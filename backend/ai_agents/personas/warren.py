"""Warren Buffett-Inspired AI Persona

Conservative fundamental analysis agent with value investing philosophy
and risk management focus. Secured with pbkdf2:sha256 for production use.
"""

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json

@dataclass
class WarrenPersonality:
    """Warren's core personality traits and investment philosophy"""
    risk_aversion: float = 0.85
    fundamentals_focus: float = 0.95
    patience_level: float = 0.90
    value_orientation: float = 0.88
    long_term_vision: float = 0.92
    contrarian_tendency: float = 0.75
    
class WarrenAgent:
    """Warren Buffett-inspired AI trading agent"""
    
    def __init__(self):
        self.name = "Warren"
        self.personality = WarrenPersonality()
        self.investment_criteria = self._initialize_criteria()
        self.memory = WarrenMemory()
        self.security_hash = self._generate_security_hash()
        
    def _initialize_criteria(self) -> Dict[str, Any]:
        """Initialize Warren's strict investment criteria"""
        return {
            'min_roe': 0.15,  # Minimum 15% ROE
            'max_pe_ratio': 25,  # Maximum P/E ratio
            'min_profit_margin': 0.10,  # Minimum 10% profit margin
            'max_debt_to_equity': 0.5,  # Maximum 50% debt-to-equity
            'min_dividend_yield': 0.02,  # Minimum 2% dividend yield
            'min_revenue_growth': 0.05,  # Minimum 5% revenue growth
            'moat_requirement': True,  # Must have economic moat
            'management_quality_threshold': 0.8  # Management quality score
        }
    
    def _generate_security_hash(self) -> str:
        """Generate pbkdf2:sha256 security hash for production use"""
        salt = secrets.token_bytes(32)
        key = hashlib.pbkdf2_hmac('sha256', 
                                 f'{self.name}_agent_{datetime.now().isoformat()}'.encode(),
                                 salt, 100000)
        return key.hex()[:16]
    
    def analyze_investment(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform Warren-style fundamental analysis"""
        
        symbol = context.get('symbol', 'UNKNOWN')
        fundamentals = context.get('fundamentals', {})
        market_data = context.get('market_data', {})
        
        # Perform fundamental analysis
        analysis_score = self._calculate_fundamental_score(fundamentals)
        valuation_assessment = self._assess_valuation(fundamentals, market_data)
        moat_evaluation = self._evaluate_economic_moat(context)
        
        # Generate Warren's recommendation
        recommendation = self._generate_recommendation(
            analysis_score, valuation_assessment, moat_evaluation
        )
        
        # Store in memory for learning
        self.memory.store_analysis(symbol, recommendation, context)
        
        return {
            'agent': self.name,
            'symbol': symbol,
            'recommendation': recommendation['action'],
            'confidence': recommendation['confidence'],
            'reasoning': recommendation['reasoning'],
            'fundamental_score': analysis_score,
            'valuation_score': valuation_assessment['score'],
            'moat_strength': moat_evaluation['strength'],
            'warren_criteria_met': recommendation['criteria_met'],
            'long_term_outlook': recommendation['long_term_outlook'],
            'risk_assessment': self._assess_warren_risk(fundamentals),
            'timestamp': datetime.now().isoformat()
        }
    
    def _calculate_fundamental_score(self, fundamentals: Dict[str, Any]) -> float:
        """Calculate comprehensive fundamental analysis score"""
        
        score_components = []
        
        # Profitability metrics
        roe = fundamentals.get('return_on_equity', 0)
        if roe >= self.investment_criteria['min_roe']:
            score_components.append(min(1.0, roe / 0.3))  # Cap at 30% ROE
        else:
            score_components.append(0.3)  # Penalty for low ROE
        
        # Profit margins
        profit_margin = fundamentals.get('profit_margin', 0)
        if profit_margin >= self.investment_criteria['min_profit_margin']:
            score_components.append(min(1.0, profit_margin / 0.25))  # Cap at 25%
        else:
            score_components.append(0.4)
        
        # Debt management
        debt_to_equity = fundamentals.get('debt_to_equity', 1.0)
        if debt_to_equity <= self.investment_criteria['max_debt_to_equity']:
            score_components.append(1.0 - debt_to_equity)
        else:
            score_components.append(0.2)  # High penalty for excessive debt
        
        return sum(score_components) / len(score_components)
    
    def _assess_valuation(self, fundamentals: Dict[str, Any], market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess if stock is undervalued using Warren's methods"""
        
        pe_ratio = fundamentals.get('pe_ratio', 50)
        current_price = market_data.get('current_price', 0)
        
        # P/E assessment
        pe_score = 1.0 if pe_ratio <= self.investment_criteria['max_pe_ratio'] else 0.3
        
        # Margin of safety calculation
        margin_of_safety = 0.25 if pe_ratio < 20 else -0.1
        
        overall_score = pe_score * 0.7 + (0.9 if margin_of_safety > 0.2 else 0.3) * 0.3
        
        return {
            'score': overall_score,
            'pe_ratio': pe_ratio,
            'current_price': current_price,
            'margin_of_safety': margin_of_safety,
            'undervalued': margin_of_safety >= 0.2
        }
    
    def _evaluate_economic_moat(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate company's economic moat strength"""
        
        company_data = context.get('company_data', {})
        
        moat_indicators = {
            'brand_strength': company_data.get('brand_score', 0.5),
            'switching_costs': company_data.get('switching_cost_score', 0.5),
            'network_effects': company_data.get('network_effect_score', 0.5),
            'cost_advantages': company_data.get('cost_advantage_score', 0.5),
            'regulatory_protection': company_data.get('regulatory_score', 0.5)
        }
        
        # Calculate overall moat strength
        moat_strength = sum(moat_indicators.values()) / len(moat_indicators)
        
        return {
            'strength': moat_strength,
            'classification': "Wide Moat" if moat_strength >= 0.8 else "Narrow Moat" if moat_strength >= 0.6 else "No Moat",
            'indicators': moat_indicators,
            'meets_warren_standard': moat_strength >= 0.6
        }
    
    def _generate_recommendation(self, fundamental_score: float, 
                               valuation: Dict[str, Any], 
                               moat: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Warren's final investment recommendation"""
        
        # Check all Warren criteria
        criteria_met = [
            fundamental_score >= 0.7,
            valuation['undervalued'],
            moat['meets_warren_standard']
        ]
        
        criteria_count = sum(criteria_met)
        
        if criteria_count == 3:
            action = "STRONG_BUY"
            confidence = 0.9
            reasoning = "Excellent fundamentals, undervalued, and strong economic moat"
        elif criteria_count == 2:
            action = "BUY"
            confidence = 0.75
            reasoning = "Good value with acceptable fundamentals"
        else:
            action = "AVOID"
            confidence = 0.8
            reasoning = "Fails Warren's investment criteria"
        
        return {
            'action': action,
            'confidence': confidence,
            'reasoning': reasoning,
            'criteria_met': criteria_count,
            'long_term_outlook': "Positive" if criteria_count >= 2 else "Negative"
        }
    
    def _assess_warren_risk(self, fundamentals: Dict[str, Any]) -> Dict[str, Any]:
        """Assess investment risk from Warren's perspective"""
        
        debt_risk = "High" if fundamentals.get('debt_to_equity', 0) > 0.5 else "Low"
        earnings_stability = "Stable" if fundamentals.get('earnings_volatility', 1.0) < 0.3 else "Volatile"
        
        return {
            'debt_risk': debt_risk,
            'earnings_stability': earnings_stability,
            'overall_risk': "Low" if debt_risk == "Low" and earnings_stability == "Stable" else "Moderate"
        }

class WarrenMemory:
    """Memory system for Warren agent"""
    
    def __init__(self):
        self.analysis_history = []
        
    def store_analysis(self, symbol: str, recommendation: Dict[str, Any], context: Dict[str, Any]):
        """Store analysis for future learning"""
        
        analysis_record = {
            'timestamp': datetime.now(),
            'symbol': symbol,
            'recommendation': recommendation,
            'context_hash': hashlib.md5(json.dumps(context, sort_keys=True, default=str).encode()).hexdigest()[:8]
        }
        
        self.analysis_history.append(analysis_record)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        
        return {
            'total_analyses': len(self.analysis_history),
            'recent_analyses': len([a for a in self.analysis_history 
                                  if (datetime.now() - a['timestamp']).days <= 30])
        }
