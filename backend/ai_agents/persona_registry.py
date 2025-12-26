"""Persona Registry

Centralized registry for all AI personas with explicit voting power.
Provides persona discovery, instantiation, and management.
"""

from typing import Dict, List, Optional, Any
from ai_agents.base_persona import PersonaAgent, PersonaArchetype
import logging


class PersonaRegistry:
    """
    Central registry for all AI trading personas
    
    Aligned with project history vision:
    - Named agents with distinct mandates
    - Explicit voting power in debate engine
    - Structured persona discovery
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._personas: Dict[str, PersonaAgent] = {}
        self._initialize_personas()
    
    def _initialize_personas(self):
        """Initialize all available personas"""
        try:
            # Import and instantiate Warren
            from ai_agents.personas.warren import WarrenAgent
            warren = WarrenAgent()
            self._personas[warren.name.lower()] = warren
            self.logger.info(f"✓ Registered persona: {warren.name} ({warren.archetype.value})")
        except Exception as e:
            self.logger.error(f"Failed to register Warren: {e}")
        
        try:
            # Import and instantiate Cathie
            from ai_agents.personas.cathie import CathieAgent
            cathie = CathieAgent()
            self._personas[cathie.name.lower()] = cathie
            self.logger.info(f"✓ Registered persona: {cathie.name} ({cathie.archetype.value})")
        except Exception as e:
            self.logger.error(f"Failed to register Cathie: {e}")
        
        self.logger.info(f"PersonaRegistry initialized with {len(self._personas)} personas")
    
    def get_persona(self, name: str) -> Optional[PersonaAgent]:
        """Get persona by name"""
        return self._personas.get(name.lower())
    
    def get_all_personas(self) -> List[PersonaAgent]:
        """Get all registered personas"""
        return list(self._personas.values())
    
    def get_personas_by_archetype(self, archetype: PersonaArchetype) -> List[PersonaAgent]:
        """Get personas filtered by archetype"""
        return [
            p for p in self._personas.values()
            if p.archetype == archetype
        ]
    
    def get_persona_summary(self, name: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive summary of a persona"""
        persona = self.get_persona(name)
        if not persona:
            return None
        
        return {
            'name': persona.name,
            'archetype': persona.archetype.value,
            'voting_weight': persona.voting_weight,
            'preferred_strategies': persona.preferred_strategies,
            'performance': persona.get_performance_summary(),
            'recent_reasoning': persona.get_recent_reasoning(limit=3)
        }
    
    def get_all_summaries(self) -> List[Dict[str, Any]]:
        """Get summaries of all personas"""
        return [
            self.get_persona_summary(name)
            for name in self._personas.keys()
        ]
    
    def conduct_vote(self, proposal: Dict[str, Any], market_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Conduct a vote across all personas
        
        Args:
            proposal: Trade proposal dict
            market_context: Current market conditions
        
        Returns:
            Dict with votes from all personas and consensus
        """
        votes = []
        total_weight = 0
        vote_tally = {}
        
        for persona in self._personas.values():
            try:
                vote = persona.vote(proposal, market_context)
                votes.append(vote.to_dict())
                
                # Tally weighted votes
                vote_key = vote.vote.value
                if vote_key not in vote_tally:
                    vote_tally[vote_key] = 0
                vote_tally[vote_key] += vote.weight * vote.confidence
                total_weight += vote.weight * vote.confidence
            except Exception as e:
                self.logger.error(f"Error getting vote from {persona.name}: {e}")
        
        # Determine consensus
        if vote_tally and total_weight > 0:
            winning_vote = max(vote_tally.items(), key=lambda x: x[1])[0]
            consensus_strength = vote_tally[winning_vote] / total_weight
        else:
            winning_vote = "HOLD"
            consensus_strength = 0.0
        
        return {
            'proposal': proposal,
            'votes': votes,
            'consensus': winning_vote,
            'consensus_strength': round(consensus_strength, 3),
            'vote_distribution': {
                k: round(v / total_weight, 3) for k, v in vote_tally.items()
            } if total_weight > 0 else {},
            'total_voting_power': round(total_weight, 3)
        }


# Global singleton instance
_persona_registry = None


def get_persona_registry() -> PersonaRegistry:
    """Get or create the global PersonaRegistry singleton"""
    global _persona_registry
    if _persona_registry is None:
        _persona_registry = PersonaRegistry()
    return _persona_registry
