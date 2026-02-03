"""Enhanced Agent Manager for YantraX RL

Integrates with existing Flask structure while adding 20+ agent coordination
"""

import logging
import uuid
import numpy as np
from datetime import datetime
from typing import Dict, Any, List, Optional
from services.knowledge_base_service import get_knowledge_base

class Agent:
    """Lightweight Agent representation used by the package API.

    This minimal class satisfies imports from `ai_firm.__init__` and
    higher-level code that expects an `Agent` type. It is intentionally
    small — the full runtime uses the `AgentManager`'s internal dicts.
    """

    def __init__(self, name: str, confidence: float = 0.5, role: str = 'analyst', **kwargs):
        self.name = name
        self.confidence = confidence
        self.role = role
        for k, v in kwargs.items():
            setattr(self, k, v)

    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in self.__dict__.items()}


class AgentDecision:
    """Simple container for an agent decision/result."""

    def __init__(self, agent_name: str, decision: str, confidence: float = 0.5):
        self.agent_name = agent_name
        self.decision = decision
        self.confidence = confidence

    def as_dict(self) -> Dict[str, Any]:
        return {
            'agent_name': self.agent_name,
            'decision': self.decision,
            'confidence': self.confidence
        }


class AgentManager:
    """Manages enhanced agent coordination for YantraX"""
    
    def __init__(self):
        self.enhanced_agents = self._initialize_20_plus_agents()
        self.voting_sessions = []
        self.logger = logging.getLogger(__name__)
        self.kb = get_knowledge_base()
        
    def _initialize_20_plus_agents(self) -> Dict[str, Dict]:
        """Initialize 20+ agent ecosystem"""
        
        agents = {}
        
        # Market Intelligence Department (5 agents)
        agents.update({
            'warren': {
                'confidence': 0.88, 'performance': 24.5, 'specialty': 'Value Analysis',
                'department': 'market_intelligence', 'role': 'director', 'persona': True
            },
            'cathie': {
                'confidence': 0.82, 'performance': 21.8, 'specialty': 'Innovation Scouting',
                'department': 'market_intelligence', 'role': 'senior', 'persona': True
            },
            'quant': {
                'confidence': 0.90, 'performance': 26.3, 'specialty': 'Statistical Modeling',
                'department': 'market_intelligence', 'role': 'senior', 'persona': False
            },
            'sentiment_analyzer': {
                'confidence': 0.84, 'performance': 22.1, 'specialty': 'Market Sentiment',
                'department': 'market_intelligence', 'role': 'specialist', 'persona': False
            },
            'news_interpreter': {
                'confidence': 0.79, 'performance': 19.6, 'specialty': 'News Analysis',
                'department': 'market_intelligence', 'role': 'analyst', 'persona': False
            }
        })
        
        # Trade Operations Department (4 agents)
        agents.update({
            'trade_executor': {
                'confidence': 0.91, 'performance': 28.1, 'specialty': 'Order Execution',
                'department': 'trade_operations', 'role': 'director', 'persona': False
            },
            'portfolio_optimizer': {
                'confidence': 0.86, 'performance': 23.7, 'specialty': 'Asset Allocation',
                'department': 'trade_operations', 'role': 'senior', 'persona': False
            },
            'liquidity_hunter': {
                'confidence': 0.79, 'performance': 19.4, 'specialty': 'Market Timing',
                'department': 'trade_operations', 'role': 'specialist', 'persona': False
            },
            'arbitrage_scout': {
                'confidence': 0.75, 'performance': 17.2, 'specialty': 'Cross-Market Analysis',
                'department': 'trade_operations', 'role': 'analyst', 'persona': False
            },
            'macro_monk': {
                'confidence': 0.88, 'performance': 0.0, 'specialty': 'Geopolitics & Black Swan',
                'department': 'market_intelligence', 'role': 'specialist', 'persona': True
            },
            'degen_auditor': {
                'confidence': 0.95, 'performance': 0.0, 'specialty': 'Scam Detection',
                'department': 'risk_control', 'role': 'director', 'persona': True
            }
        })
        
        # Risk Control Department (4 agents)
        agents.update({
            'var_guardian': {
                'confidence': 0.87, 'performance': 25.6, 'specialty': 'VaR Modeling',
                'department': 'risk_control', 'role': 'senior', 'persona': False
            },
            'correlation_detective': {
                'confidence': 0.81, 'performance': 20.9, 'specialty': 'Systemic Risk',
                'department': 'risk_control', 'role': 'specialist', 'persona': False
            },
            'black_swan_sentinel': {
                'confidence': 0.77, 'performance': 18.3, 'specialty': 'Tail Risk',
                'department': 'risk_control', 'role': 'analyst', 'persona': False
            },
            'stress_tester': {
                'confidence': 0.83, 'performance': 21.7, 'specialty': 'Scenario Analysis',
                'department': 'risk_control', 'role': 'specialist', 'persona': False
            }
        })
        
        # Performance Lab Department (4 agents)
        agents.update({
            'performance_analyst': {
                'confidence': 0.89, 'performance': 27.4, 'specialty': 'Performance Attribution',
                'department': 'performance_lab', 'role': 'director', 'persona': False
            },
            'alpha_hunter': {
                'confidence': 0.84, 'performance': 22.8, 'specialty': 'Alpha Generation',
                'department': 'performance_lab', 'role': 'senior', 'persona': False
            },
            'backtesting_engine': {
                'confidence': 0.88, 'performance': 25.1, 'specialty': 'Strategy Validation',
                'department': 'performance_lab', 'role': 'specialist', 'persona': False
            },
            'ml_optimizer': {
                'confidence': 0.86, 'performance': 24.3, 'specialty': 'ML Model Optimization',
                'department': 'performance_lab', 'role': 'specialist', 'persona': False
            }
        })
        
        # Custom Personas Department (Special Layer)
        agents.update({
            'macro_monk': {
                'confidence': 0.92, 'performance': 31.2, 'specialty': 'Geopolitical / War Economics',
                'department': 'market_intelligence', 'role': 'director', 'persona': True
            },
            'the_ghost': {
                'confidence': 0.95, 'performance': 42.0, 'specialty': 'Divine Doubt / Paradox Injection',
                'department': 'risk_control', 'role': 'director', 'persona': True
            },
            'degen_auditor': {
                'confidence': 0.88, 'performance': 25.5, 'specialty': 'Degenerate Risk Mitigation',
                'department': 'risk_control', 'role': 'senior', 'persona': True
            }
        })
        
        return agents
    
    def conduct_agent_voting(self, context: Dict[str, Any], expert_opinions: Dict[str, str] = None) -> Dict[str, Any]:
        """Conduct weighted voting across all agents
        
        Args:
            context: Market data and context
            expert_opinions: Optional dict of {agent_name: signal} from complex personas (e.g. Warren)
        """

        
        vote_tally = {}
        total_weight = 0
        participating_agents = []
        
        # Include all enhanced agents in voting
        for agent_name, agent_data in self.enhanced_agents.items():
            # Generate signal based on agent specialty and confidence
            if expert_opinions and agent_name in expert_opinions:
                signal = expert_opinions[agent_name]
            else:
                signal = self._generate_agent_signal(agent_name, agent_data, context)
            weight = self._get_vote_weight(agent_data['role']) * agent_data['confidence']
            
            if signal not in vote_tally:
                vote_tally[signal] = 0
                
            vote_tally[signal] += weight
            total_weight += weight
            
            participating_agents.append({
                'name': agent_name,
                'signal': signal,
                'confidence': agent_data['confidence'],
                'weight': weight,
                'department': agent_data['department']
            })
        
        # Determine winning signal
        divine_doubt_triggered = False
        if vote_tally:
            winning_signal = max(vote_tally.items(), key=lambda x: x[1])[0]
            consensus_strength = vote_tally[winning_signal] / total_weight if total_weight > 0 else 0
            
            # DIVINE DOUBT PROTOCOL
            # If consensus is too high (>90%), The Ghost injects doubt
            if consensus_strength > 0.9 and 'the_ghost' in self.enhanced_agents:
                self.logger.info("👻 Divine Doubt triggered! Consensus too high (%s)", consensus_strength)
                # Pivot: Force a re-evaluation
                winning_signal = "HOLD_FOR_CLARITY"
                consensus_strength *= 0.7  # Dilute confidence
                divine_doubt_triggered = True
        else:
            winning_signal = 'HOLD'
            consensus_strength = 0.5
        
        voting_result = {
            'winning_signal': winning_signal,
            'consensus_strength': round(consensus_strength, 3),
            'vote_distribution': {k: round(v/total_weight, 3) for k, v in vote_tally.items()} if total_weight > 0 else {},
            'participating_agents': len(participating_agents),
            'total_weight': round(total_weight, 2),
            'session_id': str(uuid.uuid4()),
            'timestamp': datetime.now().isoformat(),
            'divine_doubt_applied': divine_doubt_triggered
        }
        
        self.voting_sessions.append(voting_result)
        return voting_result
    
    def _generate_agent_signal(self, agent_name: str, agent_data: Dict, context: Dict = None) -> str:
        """Generate trading signal based on agent specialty and real data + KB context"""
        confidence = agent_data['confidence']
        specialty = agent_data.get('specialty', '')
        
        # 0. Fetch Contextual Wisdom from KB
        market_condition = context.get('market_trend', 'neutral') if context else 'neutral'
        query = f"{specialty} in {market_condition} market"
        wisdom_items = self.kb.query_wisdom(topic=query, archetype_filter=agent_name, max_results=1)
        
        wisdom_citation = ""
        if wisdom_items:
            wisdom = wisdom_items[0]
            wisdom_citation = f" [Wisdom: \"{wisdom['content']}\" — {wisdom['source']}]"
            # Dynamic confidence adjustment based on wisdom relevance
            if wisdom.get('relevance_score', 0) > 0.8:
                confidence = min(0.98, confidence + 0.05)
        
        # Pull real data from context provided by waterfall service
        fundamentals = context.get('fundamentals', {}) if context else {}
        pe_ratio = fundamentals.get('pe_ratio', 0)
        roe = fundamentals.get('return_on_equity', 0)
        debt_to_equity = fundamentals.get('debt_to_equity', 0)
        
        # Technicals (if available in context)
        rsi = context.get('rsi', 50) if context else 50
        trend = context.get('market_trend', 'neutral') if context else 'neutral'
        
        # 1. WARREN: Value/Fundamental Archetype
        if agent_name == 'warren' or 'Value' in specialty:
            # Warren likes low PE, high ROE, low debt
            if 0 < pe_ratio < 22 and roe > 0.18 and debt_to_equity < 1.0:
                return 'BUY'
            elif pe_ratio > 40 or debt_to_equity > 3.0:
                return 'SELL'
            return 'HOLD'
            
        # 2. CATHIE: Growth/Disruptive Archetype
        elif agent_name == 'cathie' or 'Innovation' in specialty:
            # Cathie likes momentum (RSI) and isn't afraid of high PE if growth is implied
            if rsi > 60 and trend == 'bullish':
                return 'HIGH_CONVICTION_BUY' if confidence > 0.85 else 'BUY'
            elif rsi < 30:
                return 'HOLD' # Buying dips in growth
            return 'HOLD'

        # 3. MACRO MONK: Geopolitical / Macro Risk
        elif agent_name == 'macro_monk':
            # Monk likes stability and low debt
            if debt_to_equity < 0.5 and trend == 'bullish':
                return 'BUY'
            elif debt_to_equity > 5.0:
                return 'SELL'
            return 'HOLD'

        # 4. DEGEN AUDITOR: Risk Gatekeeper
        elif agent_name == 'degen_auditor':
            # Flags unsustainable risk
            if debt_to_equity > 4.0 or pe_ratio > 100:
                return 'REJECT'
            return 'APPROVED'

        # 5. THE GHOST: Paradox / Doubt
        elif agent_name == 'the_ghost':
            # The Ghost is unpredictable but tends to disagree with extreme momentum
            if rsi > 85: return 'SELL'
            if rsi < 15: return 'BUY'
            return 'WHISPER_HOLD'
            
        # 6. QUANT / SYSTEMATIC: Pure Data
        elif 'Statistical' in specialty or 'Quant' in agent_name:
            if trend == 'bullish' and rsi < 70:
                return 'BUY'
            elif trend == 'bearish' or rsi > 80:
                return 'SELL'
            return 'HOLD'

        # 4. RISK CONTROL: Safeguards
        elif 'Risk' in specialty or 'VaR' in specialty:
            if debt_to_equity > 2.5 or trend == 'bearish':
                 return 'REJECT'
            return 'APPROVED' if confidence > 0.8 else 'CAUTION'
            
        # DEFAULT: Trend Following
        if trend == 'bullish':
            return 'BUY'
        elif trend == 'bearish':
            return 'SELL'
        
        return 'HOLD'

    def coordinate_decision_making(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Compatibility shim for older callers.

        Some entry points (for example `main_enhanced.py`) call
        `coordinate_decision_making`. The canonical implementation in this
        module is `conduct_agent_voting`. Provide a small wrapper so both
        names are supported and deployments that reference the older name
        continue to work.
        """
        result = self.conduct_agent_voting(context)

        # Map canonical keys to older expected keys for backward compatibility
        mapped = dict(result)  # shallow copy

        # `main_enhanced.py` expects `winning_recommendation` (not `winning_signal`)
        if 'winning_signal' in result and 'winning_recommendation' not in result:
            mapped['winning_recommendation'] = result['winning_signal']

        # Provide both names so callers using either schema work
        if 'winning_recommendation' in result and 'winning_signal' not in result:
            mapped['winning_signal'] = result['winning_recommendation']

        # main_enhanced expects counts named `total_votes`
        if 'participating_agents' in result and 'total_votes' not in result:
            # participating_agents is a count of participating agents
            mapped['total_votes'] = result['participating_agents']

        # Some callers expect `total_weight` or `total_votes` — keep both
        if 'total_weight' in result and 'total_weight' not in mapped:
            mapped['total_weight'] = result['total_weight']

        # Ensure consensus_strength is present (same name in both)
        if 'consensus_strength' not in mapped and 'consensus' in result:
            mapped['consensus_strength'] = result['consensus']

        return mapped
    
    def _get_vote_weight(self, role: str) -> float:
        """Get voting weight based on agent role"""
        role_weights = {
            'director': 1.0,
            'senior': 0.8,
            'specialist': 0.6,
            'analyst': 0.4
        }
        return role_weights.get(role, 0.5)
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get comprehensive agent status"""
        
        department_breakdown = {}
        
        for dept in ['market_intelligence', 'trade_operations', 'risk_control', 'performance_lab', 'communications']:
            dept_agents = [(name, data) for name, data in self.enhanced_agents.items() 
                          if data.get('department') == dept]
            
            if dept_agents:
                department_breakdown[dept] = {
                    'agent_count': len(dept_agents),
                    'agents': [{
                        'name': name,
                        'confidence': data['confidence'],
                        'performance': data['performance'],
                        'role': data['role'],
                        'specialty': data['specialty'],
                        'persona': data.get('persona', False)
                    } for name, data in dept_agents],
                    'avg_confidence': round(np.mean([data['confidence'] for _, data in dept_agents]), 3),
                    'avg_performance': round(np.mean([data['performance'] for _, data in dept_agents]), 2)
                }
        
        # Build a flattened list of all agents (compatibility for older callers)
        all_agents_list = []
        for dept, info in department_breakdown.items():
            for agent in info.get('agents', []):
                all_agents_list.append({
                    'name': agent.get('name'),
                    'confidence': agent.get('confidence'),
                    'performance': agent.get('performance'),
                    'department': dept,
                    'role': agent.get('role'),
                    'specialty': agent.get('specialty'),
                    'persona': agent.get('persona', False)
                })

        try:
            # Log diagnostic summary to help remote debugging when unexpected shapes
            # are observed by callers (e.g. Render logs showed ints instead of lists).
            dept_keys = list(department_breakdown.keys())
            self.logger.debug("get_agent_status: total_agents=%d, departments=%s, recent_voting=%d",
                              len(self.enhanced_agents), dept_keys, len(self.voting_sessions))

            # Provide additional compatibility payloads to reduce surprises for
            # older callers that expect simpler shapes (e.g. dept -> list of agents)
            departments_simple = {
                dept: info.get('agents', []) if isinstance(info, dict) else []
                for dept, info in department_breakdown.items()
            }

            departments_counts = {dept: info.get('agent_count', len(info.get('agents', [])))
                                  for dept, info in department_breakdown.items()}

            payload = {
                'total_agents': len(self.enhanced_agents),
                'departments': department_breakdown,
                'departments_simple': departments_simple,     # compatibility: dept -> [agent dicts]
                'departments_counts': departments_counts,     # compatibility: dept -> count
                'recent_voting_sessions': len(self.voting_sessions),
                'personas_active': len([a for a in self.enhanced_agents.values() if a.get('persona', False)]),
                # Compatibility: include a list value so legacy callers can count enhanced agents
                'all_agents': all_agents_list
            }

            # Also include a short sample of the first agent in each department for diagnostics
            sample = {}
            for dept, agents in departments_simple.items():
                sample[dept] = agents[0] if isinstance(agents, list) and agents else None

            payload['sample_agents'] = sample

            return payload
        except Exception:
            # If anything unexpected happens, log and return a safe minimal payload
            self.logger.exception("agent_manager.get_agent_status unexpected error")
            return {
                'total_agents': len(self.enhanced_agents),
                'departments': {},
                'recent_voting_sessions': len(self.voting_sessions),
                'personas_active': 0,
                'all_agents': []
            }
