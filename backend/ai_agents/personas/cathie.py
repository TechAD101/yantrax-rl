"""Cathie Wood-Inspired AI Persona

Growth-focused innovation scouting agent with disruptive technology focus
and sector rotation capabilities for emerging market opportunities.
"""

from datetime import datetime
from typing import Dict, Any
from dataclasses import dataclass

from ..base_persona import PersonaAgent, PersonaArchetype, VoteType, PersonaVote, PersonaAnalysis

@dataclass
class CathiePersonality:
    """Cathie's core personality traits and investment philosophy"""
    innovation_focus: float = 0.95
    growth_seeking: float = 0.90
    risk_tolerance: float = 0.85
    disruption_radar: float = 0.92
    future_vision: float = 0.88
    conviction_strength: float = 0.87
    
class CathieAgent(PersonaAgent):
    """Cathie Wood-inspired AI trading agent focused on disruptive innovation with explicit voting power"""
    
    def __init__(self):
        # Initialize base PersonaAgent
        super().__init__(
            name="Cathie",
            archetype=PersonaArchetype.GROWTH,
            voting_weight=1.0,  # Standard weight
            preferred_strategies=["innovation_investing", "disruptive_tech", "growth_at_scale", "sector_rotation"],
            department="performance_lab",
            specialty="Disruptive Innovation",
            role="director",
            mandate="Invest in the future of technology and the companies poised to disrupt established industries."
        )
        
        self.personality = CathiePersonality()
        self.innovation_criteria = self._initialize_innovation_criteria()
        self.sector_weights = self._initialize_sector_weights()
        self.memory = CathieMemory()
        
    def _initialize_innovation_criteria(self) -> Dict[str, Any]:
        """Initialize Cathie's innovation investment criteria"""
        return {
            'min_revenue_growth': 0.20,  # Minimum 20% revenue growth
            'rd_spending_threshold': 0.15,  # Minimum 15% R&D spending
            'market_size_potential': 1000000000,  # $1B+ TAM
            'adoption_curve_stage': 'early_growth',
            'competitive_moat_innovation': True,
            'management_vision_score': 0.8
        }
    
    def _initialize_sector_weights(self) -> Dict[str, float]:
        """Initialize Cathie's preferred sector allocations"""
        return {
            'artificial_intelligence': 0.25,
            'robotics_automation': 0.20,
            'energy_storage': 0.18,
            'space_exploration': 0.12,
            'genomics': 0.15,
            'fintech_blockchain': 0.10
        }
    
    def analyze_investment(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform Cathie-style innovation and growth analysis"""
        
        symbol = context.get('symbol', 'UNKNOWN')
        company_data = context.get('company_data', {})
        market_data = context.get('market_data', {})
        sector_data = context.get('sector_data', {})
        
        # Perform innovation analysis
        innovation_score = self._calculate_innovation_score(company_data, sector_data)
        growth_potential = self._assess_growth_potential(company_data, market_data)
        disruption_analysis = self._analyze_disruption_potential(context)
        sector_timing = self._evaluate_sector_timing(sector_data)
        
        # Generate Cathie's recommendation
        recommendation = self._generate_recommendation(
            innovation_score, growth_potential, disruption_analysis, sector_timing
        )
        
        # Store in memory
        self.memory.store_analysis(symbol, recommendation, context)
        
        return {
            'agent': self.name,
            'symbol': symbol,
            'recommendation': recommendation['action'],
            'confidence': recommendation['confidence'],
            'reasoning': recommendation['reasoning'],
            'innovation_score': innovation_score,
            'growth_potential': growth_potential['score'],
            'disruption_score': disruption_analysis['score'],
            'sector_timing': sector_timing['timing_score'],
            'time_horizon': recommendation['time_horizon'],
            'position_sizing': recommendation['position_sizing'],
            'timestamp': datetime.now().isoformat()
        }
    
    def _calculate_innovation_score(self, company_data: Dict[str, Any], sector_data: Dict[str, Any]) -> float:
        """Calculate comprehensive innovation score"""
        
        score_components = []
        
        # R&D Investment
        rd_spending_ratio = company_data.get('rd_spending_ratio', 0)
        score_components.append(min(1.0, rd_spending_ratio / 0.3) if rd_spending_ratio >= 0.15 else 0.4)
        
        # Patent Portfolio
        patent_strength = company_data.get('patent_portfolio_score', 0.5)
        score_components.append(patent_strength)
        
        # Technology Leadership
        tech_leadership = company_data.get('technology_leadership_score', 0.5)
        score_components.append(tech_leadership)
        
        # Sector momentum
        sector_momentum = sector_data.get('innovation_momentum', 0.5)
        score_components.append(sector_momentum)
        
        return sum(score_components) / len(score_components)
    
    def _assess_growth_potential(self, company_data: Dict[str, Any], market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess long-term growth potential"""
        
        revenue_growth = company_data.get('revenue_growth_3yr', 0)
        tam_growth = company_data.get('projected_tam_5yr', 1000000000) / company_data.get('total_addressable_market', 1000000000)
        
        growth_score = min(1.0, (revenue_growth / 0.5 + min(tam_growth, 3) / 3) / 2)
        
        return {
            'score': growth_score,
            'revenue_growth': revenue_growth,
            'tam_expansion': tam_growth,
            'growth_sustainability': "High" if growth_score > 0.7 else "Moderate"
        }
    
    def _analyze_disruption_potential(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze potential to disrupt existing industries"""
        
        company_data = context.get('company_data', {})
        
        disruption_factors = {
            'technology_superiority': company_data.get('tech_superiority_score', 0.5),
            'cost_structure_advantage': company_data.get('cost_advantage_score', 0.5),
            'user_experience_improvement': company_data.get('ux_improvement_score', 0.5),
            'business_model_innovation': company_data.get('business_model_score', 0.5)
        }
        
        disruption_score = sum(disruption_factors.values()) / len(disruption_factors)
        
        return {
            'score': disruption_score,
            'disruption_timeline': "1-3 years" if disruption_score > 0.8 else "3-7 years",
            'disruption_probability': min(0.95, disruption_score * 1.2)
        }
    
    def _evaluate_sector_timing(self, sector_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate sector timing and rotation opportunities"""
        
        adoption_stage = sector_data.get('adoption_stage', 'early_growth')
        
        stage_scores = {
            'innovation': 0.3,
            'early_adoption': 0.6,
            'early_growth': 0.9,
            'late_growth': 0.7,
            'maturity': 0.3,
            'decline': 0.1
        }
        
        timing_score = stage_scores.get(adoption_stage, 0.5)
        
        return {
            'timing_score': timing_score,
            'adoption_stage': adoption_stage,
            'optimal_entry': adoption_stage in ['early_adoption', 'early_growth']
        }
    
    def _generate_recommendation(self, innovation_score: float, growth_potential: Dict[str, Any],
                               disruption_analysis: Dict[str, Any], sector_timing: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Cathie's final investment recommendation"""
        
        composite_score = (
            innovation_score * 0.35 +
            growth_potential['score'] * 0.30 +
            disruption_analysis['score'] * 0.25 +
            sector_timing['timing_score'] * 0.10
        )
        
        if composite_score >= 0.8:
            action = "HIGH_CONVICTION_BUY"
            confidence = 0.9
            position_sizing = "Large (5-8%)"
            time_horizon = "3-7 years"
            reasoning = "Exceptional innovation with strong growth potential"
        elif composite_score >= 0.7:
            action = "BUY"
            confidence = 0.8
            position_sizing = "Medium (3-5%)"
            time_horizon = "2-5 years"
            reasoning = "Strong innovation profile with good growth prospects"
        else:
            action = "RESEARCH"
            confidence = 0.6
            position_sizing = "Small (1-2%)"
            time_horizon = "Monitor"
            reasoning = "Interesting potential but needs more development"
        
        return {
            'action': action,
            'confidence': confidence,
            'position_sizing': position_sizing,
            'time_horizon': time_horizon,
            'reasoning': reasoning,
            'composite_score': composite_score
        }
    
    # ============ PersonaAgent Interface Implementation ============
    
    def analyze(self, context: Dict[str, Any]) -> PersonaAnalysis:
        """
        Perform Cathie's full innovation analysis (implements PersonaAgent.analyze())
        
        Args:
            context: Market context with symbol, fundamentals, sector_data, market_data, etc.
        
        Returns:
            PersonaAnalysis structured result
        """
        symbol = context.get('symbol', 'UNKNOWN')
        
        # Run Cathie's existing analysis pipeline
        innovation_score = self._analyze_innovation(context)
        growth_score = self._assess_growth_potential(context)
        disruption_score = self._evaluate_disruption(context)
        sector_timing = self._evaluate_sector_timing(context)
        recommendation = self._generate_innovation_recommendation(
            innovation_score, growth_score, disruption_score, sector_timing
        )
        
        # Create structured PersonaAnalysis
        analysis = PersonaAnalysis(
            symbol=symbol,
            persona_name=self.name,
            archetype=self.archetype,
            recommendation=recommendation['action'],
            confidence=recommendation['confidence'],
            reasoning=recommendation['reasoning'],
            scores={
                'innovation': innovation_score,
                'growth': growth_score,
                'disruption': disruption_score,
                'sector_timing': sector_timing.get('score', 0.5),
                'composite': recommendation.get('composite_score', 0)
            },
            risk_assessment={
                'volatility_tolerance': 'High',
                'innovation_risk': 'Acceptable' if innovation_score > 0.7 else 'High',
                'time_horizon_risk': 'Long-term focused'
            },
            time_horizon=recommendation.get('time_horizon', 'Long-term (3-7 years)'),
            position_sizing=recommendation.get('position_sizing')
        )
        
        # Record in both Cathie memory and PersonaAgent history
        self.memory.store_analysis(symbol, recommendation, context)
        self.record_analysis(analysis)
        
        return analysis
    
    def vote(self, proposal: Dict[str, Any], market_context: Dict[str, Any]) -> PersonaVote:
        """
        Cast Cathie's vote on a trade proposal (implements PersonaAgent.vote())
        
        Args:
            proposal: Trade proposal dict with symbol, action, entry_price, target_price, etc.
            market_context: Current market conditions (innovation metrics, sector trends, etc.)
        
        Returns:
            PersonaVote with vote type, confidence, reasoning, weight
        """
        symbol = proposal.get('symbol', 'UNKNOWN')
        proposed_action = proposal.get('action', 'HOLD').upper()
        
        # Perform fresh analysis
        context = {
            'symbol': symbol,
            **market_context
        }
        analysis = self.analyze(context)
        
        # Map recommendation to VoteType
        vote_mapping = {
            'STRONG_BUY': VoteType.STRONG_BUY,
            'BUY': VoteType.BUY,
            'RESEARCH': VoteType.HOLD,
            'HOLD': VoteType.HOLD,
            'SELL': VoteType.SELL
        }
        
        vote_type = vote_mapping.get(analysis.recommendation, VoteType.ABSTAIN)
        
        # Check if proposal aligns with Cathie's analysis
        if proposed_action in ['BUY', 'STRONG_BUY']:
            if analysis.recommendation in ['BUY', 'STRONG_BUY']:
                reasoning = f"✓ Aligned: {analysis.reasoning}. Innovation metrics support aggressive growth play."
                confidence = analysis.confidence
            else:
                vote_type = VoteType.HOLD
                reasoning = f"⚠ Cautious: Cathie sees {analysis.recommendation}. {analysis.reasoning}"
                confidence = 0.65  # Moderate confidence in caution
        else:
            reasoning = analysis.reasoning
            confidence = analysis.confidence
        
        # Create formal vote
        vote = PersonaVote(
            persona_name=self.name,
            archetype=self.archetype,
            vote=vote_type,
            confidence=confidence,
            reasoning=reasoning,
            weight=self.get_vote_weight(market_context)
        )
        
        # Record vote
        self.record_vote(vote)
        
        return vote
    
    def _adjust_weight_for_context(self, context: Dict[str, Any], base_weight: float) -> float:
        """
        Adjust Cathie's voting weight based on market conditions
        Cathie gets higher weight in bull markets and innovation-driven environments
        """
        market_trend = context.get('market_trend', 'neutral').lower()
        innovation_sentiment = context.get('innovation_sentiment', 0.5)
        
        # Increase weight in bull markets and high-innovation environments
        if market_trend == 'bullish':
            base_weight *= 1.3
        elif innovation_sentiment > 0.75:
            base_weight *= 1.2
        
        return min(base_weight, 2.0)  # Cap at 2.0


class CathieMemory:
    """Memory system for Cathie agent"""
    
    def __init__(self):
        self.analysis_history = []
        
    def store_analysis(self, symbol: str, recommendation: Dict[str, Any], context: Dict[str, Any]):
        """Store analysis with innovation focus"""
        
        analysis_record = {
            'timestamp': datetime.now(),
            'symbol': symbol,
            'recommendation': recommendation,
            'innovation_score': context.get('innovation_score', 0),
            'sector': context.get('sector_data', {}).get('sector', 'unknown')
        }
        
        self.analysis_history.append(analysis_record)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary with innovation focus"""
        
        if not self.analysis_history:
            return {'total_analyses': 0, 'innovation_success_rate': 0}
        
        high_innovation_analyses = [a for a in self.analysis_history 
                                  if a.get('innovation_score', 0) > 0.7]
        
        return {
            'total_analyses': len(self.analysis_history),
            'high_innovation_picks': len(high_innovation_analyses),
            'average_innovation_score': sum(a.get('innovation_score', 0) for a in self.analysis_history) / len(self.analysis_history)
        }
