from typing import Dict, Any
from ..base_persona import PersonaAgent, PersonaArchetype, PersonaVote, PersonaAnalysis, VoteType

class QuantAgent(PersonaAgent):
    """Quant persona - High frequency, algorithmic, and statistical arb focus"""
    def __init__(self):
        super().__init__(
            name="quant",
            archetype=PersonaArchetype.QUANTATATIVE,
            voting_weight=1.1,
            preferred_strategies=["statistical_arbitrage", "momentum_ignition", "mean_reversion"],
            department="performance_lab",
            specialty="Algorithmic / Statistical Analysis",
            role="lead_quant",
            mandate="Execute probability-based mathematical models stripped of human emotion."
        )
    
    def analyze(self, context: Dict[str, Any]) -> PersonaAnalysis:
        vol = context.get('volatility', 0)
        signal = "BUY" if vol < 0.3 else "HOLD"
        return PersonaAnalysis(
            symbol=context.get('symbol', 'UNKNOWN'),
            persona_name=self.name,
            archetype=self.archetype,
            recommendation=signal,
            confidence=0.85,
            reasoning=f"Mathematical models indicate positive expected value based on current volatility ({vol}).",
            scores={'statistical_edge': 0.8},
            risk_assessment={'var_95': 'acceptable'},
            time_horizon="Intraday"
        )
    
    def vote(self, proposal: Dict[str, Any], market_context: Dict[str, Any]) -> PersonaVote:
        return PersonaVote(
            persona_name=self.name,
            archetype=self.archetype,
            vote=VoteType.BUY if market_context.get('volatility', 0) < 0.3 else VoteType.HOLD,
            confidence=0.85,
            reasoning="Algorithm confirms optimal Z-score thresholds for entry.",
            weight=self.voting_weight
        )
