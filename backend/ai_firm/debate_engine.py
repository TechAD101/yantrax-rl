import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List
from .personas import Warren, Cathie, Quant, DegenAuditor

class DebateEngine:
    """
    Facilitates structured arguments and voting among AI agents using formal Persona classes.
    Implements weighted voting and consensus building.
    """
    
    def __init__(self, agent_manager):
        self.agent_manager = agent_manager
        self.logger = logging.getLogger(__name__)
        self.debate_history = []
        self.debate_cache = {} # ticker -> {'result': dict, 'expiry': datetime}
        self.cache_ttl_seconds = 30
        
        from ai_agents.persona_registry import get_persona_registry
        self.persona_registry = get_persona_registry()
        self.personas = self.persona_registry.get_all_personas()
        
        # Perplexity Service placeholder (set by main.py)
        self.perplexity_service = None

    def set_perplexity_service(self, service):
        self.perplexity_service = service

    async def conduct_debate(self, ticker: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Hosts a debate between agents regarding a specific ticker/asset with Perplexity context"""
        
        # 0. Check Cache
        if ticker in self.debate_cache:
            cached = self.debate_cache[ticker]
            if datetime.now() < cached['expiry']:
                return cached['result']

        self.logger.info(f"🎤 Starting enhanced debate for {ticker}")
        
        # 0.5 Fetch Perplexity Debate Context for "World Class" Intelligence
        perplexity_context = ""
        if self.perplexity_service:
            try:
                topic = f"Critical debate points for {ticker} in the current {context.get('market_trend', 'neutral')} market"
                search_res = await self.perplexity_service.get_debate_context(topic, [ticker])
                perplexity_context = search_res.get('market_context', '')
                if perplexity_context:
                    self.logger.info(f"✓ Perplexity Context Injected: {len(perplexity_context)} chars")
            except Exception as e:
                self.logger.error(f"Perplexity context fetch failed: {e}")

        # Add Perplexity context to market_data for persona analysis
        enriched_context = dict(context)
        enriched_context['perplexity_market_lore'] = perplexity_context
        
        arguments = []
        
        # 1. Round 1: Initial Analysis
        for persona in self.personas:
            analysis = persona.analyze(enriched_context, enriched_context)
            
            # Only include if confidence meets threshold
            if analysis['confidence'] >= persona.confidence_threshold:
                arguments.append({
                    'agent': persona.name,
                    'role': persona.role,
                    'signal': analysis['signal'],
                    'reasoning': analysis['reasoning'],
                    'concerns': analysis['concerns'],
                    'weight': persona.vote_weight * analysis['confidence'],
                    'confidence': analysis['confidence'],
                    'quote': persona.get_philosophy_quote(),
                    'rebuttals': []
                })
        
        # 2. Round 2: Rebuttals (Simple Multi-Turn)
        if len(arguments) > 1:
            winning_temp = max(arguments, key=lambda x: x['weight'])['signal']
            for arg in arguments:
                if arg['signal'] != winning_temp:
                    # Dissenter rebuttal
                    rebuttal = f"Wait, {arg['agent']} notes that while the majority looks for {winning_temp}, we cannot ignore {arg['concerns'][0] if arg['concerns'] else 'the underlying risk'}."
                    arg['rebuttals'].append(rebuttal)
                elif arg['confidence'] > 0.85:
                    # Supporter strong reinforcement
                     reinforcement = f"{arg['agent']} double-confirms the {winning_temp} thesis based on Institutional Wisdom."
                     arg['rebuttals'].append(reinforcement)

        # 3. Tally Votes
        vote_tally = {}
        total_weight = 0
        
        for arg in arguments:
            sig = arg['signal']
            if sig not in vote_tally:
                vote_tally[sig] = 0
            vote_tally[sig] += arg['weight']
            total_weight += arg['weight']
        
        # 4. Resolve Consensus
        if total_weight > 0:
            winning_signal = max(vote_tally.items(), key=lambda x: x[1])[0]
            consensus_score = vote_tally[winning_signal] / total_weight
        else:
            winning_signal = 'HOLD' # Default if no one votes
            consensus_score = 0
            
        debate_result = {
            'id': str(uuid.uuid4()),
            'ticker': ticker,
            'timestamp': datetime.now().isoformat(),
            'perplexity_context': perplexity_context,
            'arguments': arguments,
            'winning_signal': winning_signal,
            'consensus_score': round(consensus_score, 2),
            'vote_distribution': {k: round(v/total_weight, 2) for k, v in vote_tally.items()} if total_weight > 0 else {},
            'participants': [p.name for p in self.personas]
        }
        
        # Update Cache
        self.debate_cache[ticker] = {
            'result': debate_result,
            'expiry': datetime.now() + timedelta(seconds=self.cache_ttl_seconds)
        }
        
        self.debate_history.append(debate_result)
        return debate_result
