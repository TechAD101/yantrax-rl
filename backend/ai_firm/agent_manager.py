"""Enhanced Agent Manager for YantraX RL

Integrates with existing Flask structure while adding 20+ agent coordination
"""

import json
import uuid
import numpy as np
from datetime import datetime
from typing import Dict, List, Any

class Agent:
    """Individual agent class for the AI firm"""
    
    def __init__(self, name: str, confidence: float, performance: float, 
                 specialty: str, department: str, role: str, persona: bool = False):
        self.name = name
        self.confidence = confidence
        self.performance = performance
        self.specialty = specialty
        self.department = department
        self.role = role
        self.persona = persona
        self.id = str(uuid.uuid4())
        
    def generate_signal(self) -> str:
        """Generate trading signal based on agent specialty"""
        
        # Specialty-based signal generation
        if 'Value' in self.specialty or self.name == 'warren':
            return 'BUY' if self.confidence > 0.8 else 'HOLD'
        elif 'Innovation' in self.specialty or self.name == 'cathie':
            return 'HIGH_CONVICTION_BUY' if self.confidence > 0.85 else 'BUY'
        elif 'Risk' in self.specialty or 'VaR' in self.specialty:
            return 'APPROVED' if self.confidence > 0.8 else 'CAUTION'
        else:
            # Default signal generation
            if self.confidence > 0.8:
                return np.random.choice(['BUY', 'STRONG_BUY'], p=[0.6, 0.4])
            elif self.confidence > 0.6:
                return np.random.choice(['BUY', 'HOLD'], p=[0.7, 0.3])
            else:
                return 'HOLD'
    
    def get_vote_weight(self) -> float:
        """Get voting weight based on agent role"""
        role_weights = {
            'director': 1.0,
            'senior': 0.8,
            'specialist': 0.6,
            'analyst': 0.4
        }
        return role_weights.get(self.role, 0.5)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert agent to dictionary"""
        return {
            'name': self.name,
            'confidence': self.confidence,
            'performance': self.performance,
            'specialty': self.specialty,
            'department': self.department,
            'role': self.role,
            'persona': self.persona,
            'id': self.id
        }

class AgentManager:
    """Manages enhanced agent coordination for YantraX"""
    
    def __init__(self):
        self.enhanced_agents = self._initialize_20_plus_agents()
        self.voting_sessions = []
        
    def _initialize_20_plus_agents(self) -> Dict[str, Agent]:
        """Initialize 20+ agent ecosystem"""
        
        agents = {}
        
        # Market Intelligence Department (5 agents)
        agents['warren'] = Agent(
            'warren', 0.88, 24.5, 'Value Analysis', 'market_intelligence', 'director', True
        )
        agents['cathie'] = Agent(
            'cathie', 0.82, 21.8, 'Innovation Scouting', 'market_intelligence', 'senior', True
        )
        agents['quant'] = Agent(
            'quant', 0.90, 26.3, 'Statistical Modeling', 'market_intelligence', 'senior', False
        )
        agents['sentiment_analyzer'] = Agent(
            'sentiment_analyzer', 0.84, 22.1, 'Market Sentiment', 'market_intelligence', 'specialist', False
        )
        agents['news_interpreter'] = Agent(
            'news_interpreter', 0.79, 19.6, 'News Analysis', 'market_intelligence', 'analyst', False
        )
        
        # Trade Operations Department (4 agents)
        agents['trade_executor'] = Agent(
            'trade_executor', 0.91, 28.1, 'Order Execution', 'trade_operations', 'director', False
        )
        agents['portfolio_optimizer'] = Agent(
            'portfolio_optimizer', 0.86, 23.7, 'Asset Allocation', 'trade_operations', 'senior', False
        )
        agents['liquidity_hunter'] = Agent(
            'liquidity_hunter', 0.79, 19.4, 'Market Timing', 'trade_operations', 'specialist', False
        )
        agents['arbitrage_scout'] = Agent(
            'arbitrage_scout', 0.75, 17.2, 'Cross-Market Analysis', 'trade_operations', 'analyst', False
        )
        
        # Risk Control Department (4 agents)
        agents['var_guardian'] = Agent(
            'var_guardian', 0.87, 25.6, 'VaR Modeling', 'risk_control', 'senior', False
        )
        agents['correlation_detective'] = Agent(
            'correlation_detective', 0.81, 20.9, 'Systemic Risk', 'risk_control', 'specialist', False
        )
        agents['black_swan_sentinel'] = Agent(
            'black_swan_sentinel', 0.77, 18.3, 'Tail Risk', 'risk_control', 'analyst', False
        )
        agents['stress_tester'] = Agent(
            'stress_tester', 0.83, 21.7, 'Scenario Analysis', 'risk_control', 'specialist', False
        )
        
        # Performance Lab Department (4 agents)
        agents['performance_analyst'] = Agent(
            'performance_analyst', 0.89, 27.4, 'Performance Attribution', 'performance_lab', 'director', False
        )
        agents['alpha_hunter'] = Agent(
            'alpha_hunter', 0.84, 22.8, 'Alpha Generation', 'performance_lab', 'senior', False
        )
        agents['backtesting_engine'] = Agent(
            'backtesting_engine', 0.88, 25.1, 'Strategy Validation', 'performance_lab', 'specialist', False
        )
        agents['ml_optimizer'] = Agent(
            'ml_optimizer', 0.86, 24.3, 'ML Model Optimization', 'performance_lab', 'specialist', False
        )
        
        # Communications Department (3 agents)
        agents['report_generator'] = Agent(
            'report_generator', 0.85, 23.2, 'Report Generation', 'communications', 'director', False
        )
        agents['market_narrator'] = Agent(
            'market_narrator', 0.80, 19.8, 'Market Storytelling', 'communications', 'senior', False
        )
        agents['alert_coordinator'] = Agent(
            'alert_coordinator', 0.83, 21.5, 'Alert Management', 'communications', 'specialist', False
        )
        
        return agents
    
    def conduct_agent_voting(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Conduct weighted voting across all agents"""
        
        vote_tally = {}
        total_weight = 0
        participating_agents = []
        
        # Include all enhanced agents in voting
        for agent_name, agent in self.enhanced_agents.items():
            # Generate signal based on agent specialty and confidence
            signal = agent.generate_signal()
            weight = agent.get_vote_weight() * agent.confidence
            
            if signal not in vote_tally:
                vote_tally[signal] = 0
                
            vote_tally[signal] += weight
            total_weight += weight
            
            participating_agents.append({
                'name': agent_name,
                'signal': signal,
                'confidence': agent.confidence,
                'weight': weight,
                'department': agent.department
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
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get comprehensive agent status"""
        
        department_breakdown = {}
        
        for dept in ['market_intelligence', 'trade_operations', 'risk_control', 'performance_lab', 'communications']:
            dept_agents = [(name, agent) for name, agent in self.enhanced_agents.items() 
                          if agent.department == dept]
            
            if dept_agents:
                department_breakdown[dept] = {
                    'agent_count': len(dept_agents),
                    'agents': [agent.to_dict() for _, agent in dept_agents],
                    'avg_confidence': round(np.mean([agent.confidence for _, agent in dept_agents]), 3),
                    'avg_performance': round(np.mean([agent.performance for _, agent in dept_agents]), 2)
                }
        
        return {
            'total_agents': len(self.enhanced_agents),
            'departments': department_breakdown,
            'recent_voting_sessions': len(self.voting_sessions),
            'personas_active': len([a for a in self.enhanced_agents.values() if a.persona])
        }
    
    def get_all_agents_status(self) -> Dict[str, Dict[str, Any]]:
        """Get all agents status in the format expected by the main application"""
        
        return {name: {
            'confidence': agent.confidence,
            'performance': agent.performance,
            'department': agent.department,
            'role': agent.role,
            'specialty': agent.specialty,
            'persona': agent.persona
        } for name, agent in self.enhanced_agents.items()}