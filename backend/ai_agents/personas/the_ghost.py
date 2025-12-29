from typing import Dict, Any
from ..base_persona import PersonaAgent, PersonaArchetype, PersonaVote, PersonaAnalysis, VoteType

class TheGhostAgent(PersonaAgent):
    """The Ghost persona - Quantum sentiment and reversals focus"""
    
    def __init__(self):
        super().__init__(
            name="the_ghost",
            archetype=PersonaArchetype.GHOST,
            voting_weight=1.3,
            preferred_strategies=["quantum_sentiment", "reversal_timing", "liquidity_hunt"],
            department="market_intelligence",
            specialty="Quantum Sentiment / Non-Linear Reversals",
            role="senior_analyst",
            mandate="Identify the hidden hand of the market and capitalize on collective emotion."
        )
    
    def analyze(self, context: Dict[str, Any]) -> PersonaAnalysis:
        return PersonaAnalysis(
            symbol=context.get('symbol', 'UNKNOWN'),
            persona_name=self.name,
            archetype=self.archetype,
            recommendation="HOLD",
            confidence=0.92,
            reasoning="Market whispers suggest a reversal is imminent.",
            scores={'quantum_signal': 0.9},
            risk_assessment={'volatility': 'high'},
            time_horizon="Intraday/Swing"
        )
    
    def vote(self, proposal: Dict[str, Any], market_context: Dict[str, Any]) -> PersonaVote:
        return PersonaVote(
            persona_name=self.name,
            archetype=self.archetype,
            vote=VoteType.HOLD,
            confidence=0.9,
            reasoning="The Ghost senses uncertainty in current liquidity zones.",
            weight=self.voting_weight
        )
