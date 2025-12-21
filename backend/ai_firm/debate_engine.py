import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any

class DebateEngine:
    """Facilitates structured arguments and voting among AI agents"""
    
    def __init__(self, agent_manager):
        self.agent_manager = agent_manager
        self.logger = logging.getLogger(__name__)
        self.debate_history = []
        self.debate_cache = {} # ticker -> {'result': dict, 'expiry': datetime}
        self.cache_ttl_seconds = 30

    def conduct_debate(self, ticker: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Hosts a debate between agents regarding a specific ticker/asset with throttling"""
        
        # 0. Check Cache
        if ticker in self.debate_cache:
            cached = self.debate_cache[ticker]
            if datetime.now() < cached['expiry']:
                # self.logger.debug(f"🔇 Throttling debate for {ticker}")
                return cached['result']

        self.logger.info(f"🎤 Starting debate for {ticker}")
        
        arguments = []
        
        # 1. Gather Arguments from Personas
        for agent_name, agent_data in self.agent_manager.enhanced_agents.items():
            if agent_data.get('persona', False) or agent_data.get('role') == 'director':
                signal = self.agent_manager._generate_agent_signal(agent_name, agent_data, context)
                reasoning = self._generate_persona_reasoning(agent_name, signal, context)
                
                arguments.append({
                    'agent': agent_name,
                    'signal': signal,
                    'reasoning': reasoning,
                    'weight': self.agent_manager._get_vote_weight(agent_data['role']) * agent_data['confidence']
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
        winning_signal = max(vote_tally.items(), key=lambda x: x[1])[0] if vote_tally else 'HOLD'
        consensus_score = vote_tally[winning_signal] / total_weight if total_weight > 0 else 0
        
        debate_result = {
            'id': str(uuid.uuid4()),
            'ticker': ticker,
            'timestamp': datetime.now().isoformat(),
            'arguments': arguments,
            'winning_signal': winning_signal,
            'consensus_score': round(consensus_score, 2),
            'vote_distribution': {k: round(v/total_weight, 2) for k, v in vote_tally.items()} if total_weight > 0 else {}
        }
        
        # Update Cache
        self.debate_cache[ticker] = {
            'result': debate_result,
            'expiry': datetime.now() + timedelta(seconds=self.cache_ttl_seconds)
        }
        
        self.debate_history.append(debate_result)
        return debate_result

    def _generate_persona_reasoning(self, agent: str, signal: str, context: Dict) -> str:
        """Generates deterministic pseudo-LLM reasoning for the agent's signal"""
        fundamentals = context.get('fundamentals', {})
        pe = fundamentals.get('pe_ratio', 'N/A')
        roe = fundamentals.get('return_on_equity', 'N/A')
        
        if agent == 'warren':
            if signal == 'BUY':
                return f"Fundamentals are robust. P/E of {pe} and ROE of {roe} signify a margin of safety."
            elif signal == 'SELL':
                return f"The market is overvaluing this. P/E of {pe} is too high for the current yield."
            return "Current pricing doesn't offer a significant enough discount to intrinsic value."
            
        elif agent == 'cathie':
            if 'BUY' in signal:
                return "Disruption is happening. Momentum indicators are surging, and we must bet on the future."
            return "Seeking better entry points for high-growth innovation."
            
        elif agent == 'quant':
            trend = context.get('market_trend', 'neutral')
            return f"Regime detection shows a {trend} trend. Statistical probability favors this signal."
            
        return f"Aligned with department protocols and specialized metrics for {agent}."
