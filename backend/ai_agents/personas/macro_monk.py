from typing import Dict, Any
from ..base_persona import PersonaAgent, PersonaArchetype, PersonaVote, PersonaAnalysis, VoteType

class MacroMonkAgent(PersonaAgent):
    """Macro Monk persona - Geopolitical and war economics focus"""
    
    def __init__(self):
        super().__init__(
            name="macro_monk",
            archetype=PersonaArchetype.MACRO,
            voting_weight=1.1,
            preferred_strategies=["macro_trend", "geopolitical_hedge", "commodity_focus"],
            department="market_intelligence",
            specialty="Geopolitical / War Economics",
            role="director",
            mandate="Navigate global shifts and identify institutional opportunities in chaos."
        )
    
    def analyze(self, context: Dict[str, Any]) -> PersonaAnalysis:
        return PersonaAnalysis(
            symbol=context.get('symbol', 'UNKNOWN'),
            persona_name=self.name,
            archetype=self.archetype,
            recommendation="BUY",
            confidence=0.85,
            reasoning="Global macro trends support long-term positioning.",
            scores={'macro_alignment': 0.8},
            risk_assessment={'geopolitical': 'moderate'},
            time_horizon="Strategic"
        )
    
    def vote(self, proposal: Dict[str, Any], market_context: Dict[str, Any]) -> PersonaVote:
        return PersonaVote(
            persona_name=self.name,
            archetype=self.archetype,
            vote=VoteType.BUY,
            confidence=0.8,
            reasoning="Macro alignment confirmed.",
            weight=self.voting_weight
        )
