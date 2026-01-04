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
        
        # Initialize Personas
        self.personas = [
            Warren(),
            Cathie(),
            Quant(),
            DegenAuditor()
        ]

    def conduct_debate(self, ticker: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Hosts a debate between agents regarding a specific ticker/asset with throttling"""
        
        # 0. Check Cache
        if ticker in self.debate_cache:
            cached = self.debate_cache[ticker]
            if datetime.now() < cached['expiry']:
                return cached['result']

        self.logger.info(f"🎤 Starting debate for {ticker}")
        
        arguments = []
        
        # 1. Gather Arguments from Personas
        for persona in self.personas:
            analysis = persona.analyze(context, context) # Pass context as market_data for now
            
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
                    'quote': persona.get_philosophy_quote()
                })
        
        # 2. Tally Votes
        vote_tally = {}
        total_weight = 0
        
        for arg in arguments:
            sig = arg['signal']
            if sig not in vote_tally:
                vote_tally[sig] = 0
            vote_tally[sig] += arg['weight']
            total_weight += arg['weight']
        
        # 3. Resolve Consensus
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
