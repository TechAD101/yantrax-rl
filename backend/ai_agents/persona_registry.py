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
        # 1. CORE PERSONAS (Explicitly defined)
        persona_configs = [
            ("Warren", "ai_agents.personas.warren", "WarrenAgent"),
            ("Cathie", "ai_agents.personas.cathie", "CathieAgent"),
            ("The Ghost", "ai_agents.personas.the_ghost", "TheGhostAgent"),
            ("Macro Monk", "ai_agents.personas.macro_monk", "MacroMonkAgent"),
            ("Quant", "ai_agents.personas.quant", "QuantAgent"),
            ("Degen Auditor", "ai_agents.personas.degen_auditor", "DegenAuditorAgent")
        ]

        for display_name, module_path, class_name in persona_configs:
            try:
                import importlib
                module = importlib.import_module(module_path)
                agent_class = getattr(module, class_name)
                agent = agent_class()
                self._personas[agent.name.lower()] = agent
                self.logger.info(f"✓ Registered persona: {agent.name} ({agent.archetype.value})")
            except Exception as e:
                self.logger.warning(f"Failed to register {display_name} class: {e}. Falling back to placeholder.")

        # 2. SUPPLEMENTARY PERSONAS (Placeholders for 20+ vision)
        from ai_agents.base_agent import BaseAgent
        supplementary_configs = [
            ("TradeExecutor", PersonaArchetype.SYSTEMATIC),
            ("NewsAggregator", PersonaArchetype.MACRO),
            ("SentimentBot", PersonaArchetype.GHOST),
            ("ValueScout", PersonaArchetype.VALUE),
            ("GrowthPilot", PersonaArchetype.GROWTH),
            ("RiskSentinel", PersonaArchetype.RISK_AUDITOR)
        ]

        for name, archetype in supplementary_configs:
            if name.lower() not in self._personas:
                placeholder_agent = BaseAgent(name=name, archetype=archetype)
                self._personas[name.lower()] = placeholder_agent
                self.logger.debug(f"Registered institutional placeholder: {name}")
            
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
        
        # Check if persona has PersonaAgent attributes
        has_persona_attrs = hasattr(persona, 'voting_weight')
        
        summary = {
            'name': persona.name.lower(),
            'display_name': persona.name,
            'archetype': persona.archetype.value,
        }
        
        if has_persona_attrs:
            # Full PersonaAgent summary
            summary.update({
                'voting_weight': persona.voting_weight,
                'preferred_strategies': persona.preferred_strategies,
                'department': persona.department,
                'specialty': persona.specialty,
                'role': persona.role,
                'mandate': persona.mandate,
                'confidence': persona.get_performance_summary().get('confidence', 0.8),
                'performance': persona.get_performance_summary(),
                'recent_reasoning': persona.get_recent_reasoning(limit=3)
            })
        else:
            # BaseAgent summary
            summary.update({
                'voting_weight': 1.0,  # Default weight
                'preferred_strategies': [],
                'department': 'placeholder',
                'specialty': 'general',
                'role': 'analyst',
                'mandate': 'Placeholder agent',
                'confidence': persona.confidence,
                'performance': {'total_votes': 0, 'confidence': persona.confidence},
                'recent_reasoning': []
            })
        
        return summary
    
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
