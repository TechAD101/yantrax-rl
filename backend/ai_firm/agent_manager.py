"""Enhanced Agent Manager for YantraX RL

Integrates with existing Flask structure while adding 20+ agent coordination
"""

import json
import uuid
import numpy as np
from datetime import datetime
from typing import Dict, List, Any

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
        
        # Communications Department (3 agents)
        agents.update({
            'report_generator': {
                'confidence': 0.85, 'performance': 23.2, 'specialty': 'Report Generation',
                'department': 'communications', 'role': 'director', 'persona': False
            },
            'market_narrator': {
                'confidence': 0.80, 'performance': 19.8, 'specialty': 'Market Storytelling',
                'department': 'communications', 'role': 'senior', 'persona': False
            },
            'alert_coordinator': {
                'confidence': 0.83, 'performance': 21.5, 'specialty': 'Alert Management',
                'department': 'communications', 'role': 'specialist', 'persona': False
            }
        })
        
        return agents
    
    def conduct_agent_voting(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Conduct weighted voting across all agents"""
        
        vote_tally = {}
        total_weight = 0
        participating_agents = []
        
        # Include all enhanced agents in voting
        for agent_name, agent_data in self.enhanced_agents.items():
            # Generate signal based on agent specialty and confidence
            signal = self._generate_agent_signal(agent_name, agent_data)
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
        if vote_tally:
            winning_signal = max(vote_tally.items(), key=lambda x: x[1])[0]
            consensus_strength = vote_tally[winning_signal] / total_weight if total_weight > 0 else 0
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
            'timestamp': datetime.now().isoformat()
        }
        
        self.voting_sessions.append(voting_result)
        return voting_result
    
    def _generate_agent_signal(self, agent_name: str, agent_data: Dict) -> str:
        """Generate trading signal based on agent specialty"""
        
        confidence = agent_data['confidence']
        specialty = agent_data.get('specialty', '')
        
        # Specialty-based signal generation
        if 'Value' in specialty or agent_name == 'warren':
            return 'BUY' if confidence > 0.8 else 'HOLD'
        elif 'Innovation' in specialty or agent_name == 'cathie':
            return 'HIGH_CONVICTION_BUY' if confidence > 0.85 else 'BUY'
        elif 'Risk' in specialty or 'VaR' in specialty:
            return 'APPROVED' if confidence > 0.8 else 'CAUTION'
        else:
            # Default signal generation
            if confidence > 0.8:
                return np.random.choice(['BUY', 'STRONG_BUY'], p=[0.6, 0.4])
            elif confidence > 0.6:
                return np.random.choice(['BUY', 'HOLD'], p=[0.7, 0.3])
            else:
                return 'HOLD'

    def coordinate_decision_making(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Compatibility shim for older callers.

        Some entry points (for example `main_enhanced.py`) call
        `coordinate_decision_making`. The canonical implementation in this
        module is `conduct_agent_voting`. Provide a small wrapper so both
        names are supported and deployments that reference the older name
        continue to work.
        """
        return self.conduct_agent_voting(context)
    
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

        return {
            'total_agents': len(self.enhanced_agents),
            'departments': department_breakdown,
            'recent_voting_sessions': len(self.voting_sessions),
            'personas_active': len([a for a in self.enhanced_agents.values() if a.get('persona', False)]),
            # Compatibility: include a list value so legacy callers can count enhanced agents
            'all_agents': all_agents_list
        }
