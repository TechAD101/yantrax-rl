from typing import Dict, Any
from ..base_persona import PersonaAgent, PersonaArchetype, PersonaVote, PersonaAnalysis, VoteType

class DegenAuditorAgent(PersonaAgent):
    """Degen Auditor persona - Risk management, checks speculative excess"""
    def __init__(self):
        super().__init__(
            name="degen_auditor",
            archetype=PersonaArchetype.SPECULATIVE,
            voting_weight=1.5,
            preferred_strategies=["risk_mitigation", "volatility_crush", "capital_preservation"],
            department="risk_control",
            specialty="Risk Management / Speculation Control",
            role="chief_risk_officer",
            mandate="Halt any trades that resemble gambling or lack fundamental liquidity/macro support."
        )
    
    def analyze(self, context: Dict[str, Any]) -> PersonaAnalysis:
        mood = context.get('market_mood', 'neutral')
        signal = "SELL" if mood == 'euphoric' else "HOLD"
        return PersonaAnalysis(
            symbol=context.get('symbol', 'UNKNOWN'),
            persona_name=self.name,
            archetype=self.archetype,
            recommendation=signal,
            confidence=0.95,
            reasoning=f"Auditing speculative levels. Current mood is {mood}, triggering defensive protocols if euphoric.",
            scores={'speculation_risk': 0.9},
            risk_assessment={'gambling_probability': 'high'},
            time_horizon="Immediate"
        )
    
    def vote(self, proposal: Dict[str, Any], market_context: Dict[str, Any]) -> PersonaVote:
        mood = market_context.get('market_mood', 'neutral')
        vote = VoteType.SELL if mood == 'euphoric' else VoteType.HOLD
        return PersonaVote(
            persona_name=self.name,
            archetype=self.archetype,
            vote=vote,
            confidence=0.9,
            reasoning="Degen Auditor flags excessive retail froth. Capital preservation activated.",
            weight=self.voting_weight
        )
