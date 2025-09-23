"""Enhanced Agent Manager for YantraX RL

Integrates with existing Flask structure while adding 20+ agent coordination
"""

import json
import uuid
import numpy as np
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum

# Export all classes for proper importing
__all__ = ['Agent', 'AgentDecision', 'AgentManager', 'DecisionType']

class DecisionType(Enum):
    """Types of decisions an agent can make"""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    STRONG_BUY = "strong_buy"
    HIGH_CONVICTION_BUY = "high_conviction_buy"
    APPROVED = "approved"
    CAUTION = "caution"
    
@dataclass
class AgentDecision:
    """Individual agent decision with reasoning and confidence"""
    agent_id: str
    agent_name: str
    decision_type: DecisionType
    confidence: float
    reasoning: str
    timestamp: datetime
    context: Dict[str, Any]
    performance_score: float = 0.0
    risk_assessment: str = "medium"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert decision to dictionary"""
        return {
            'agent_id': self.agent_id,
            'agent_name': self.agent_name,
            'decision_type': self.decision_type.value,
            'confidence': self.confidence,
            'reasoning': self.reasoning,
            'timestamp': self.timestamp.isoformat(),
            'context': self.context,
            'performance_score': self.performance_score,
            'risk_assessment': self.risk_assessment
        }
    
    def __str__(self) -> str:
        return f"AgentDecision({self.agent_name}: {self.decision_type.value}, confidence={self.confidence:.2f})"

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
        
    def make_decision(self, context: Dict[str, Any]) -> AgentDecision:
        """Make a trading decision based on context"""
        
        # Generate decision type based on agent specialty
        decision_type = self._determine_decision_type()
        
        # Generate reasoning
        reasoning = self._generate_reasoning(context)
        
        # Create decision
        decision = AgentDecision(
            agent_id=self.id,
            agent_name=self.name,
            decision_type=decision_type,
            confidence=self.confidence,
            reasoning=reasoning,
            timestamp=datetime.now(),
            context=context,
            performance_score=self.performance,
            risk_assessment=self._assess_risk()
        )
        
        return decision
        
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
    
    def _determine_decision_type(self) -> DecisionType:
        """Determine decision type based on specialty and confidence"""
        
        if 'Value' in self.specialty or self.name == 'warren':
            return DecisionType.BUY if self.confidence > 0.8 else DecisionType.HOLD
        elif 'Innovation' in self.specialty or self.name == 'cathie':
            return DecisionType.HIGH_CONVICTION_BUY if self.confidence > 0.85 else DecisionType.BUY
        elif 'Risk' in self.specialty:
            return DecisionType.APPROVED if self.confidence > 0.8 else DecisionType.CAUTION
        else:
            # Default decision logic
            if self.confidence > 0.8:
                return DecisionType.STRONG_BUY
            elif self.confidence > 0.6:
                return DecisionType.BUY
            else:
                return DecisionType.HOLD
    
    def _generate_reasoning(self, context: Dict[str, Any]) -> str:
        """Generate reasoning for the decision"""
        
        reasoning_parts = []
        
        # Specialty-based reasoning
        if 'Value' in self.specialty:
            reasoning_parts.append(f"Value analysis shows {self.specialty.lower()} metrics are favorable")
        elif 'Innovation' in self.specialty:
            reasoning_parts.append(f"Innovation indicators suggest strong disruption potential")
        elif 'Risk' in self.specialty:
            reasoning_parts.append(f"Risk assessment indicates {self.specialty.lower()} within acceptable parameters")
        else:
            reasoning_parts.append(f"Analysis of {self.specialty.lower()} shows positive signals")
        
        # Confidence-based reasoning
        if self.confidence > 0.8:
            reasoning_parts.append("High confidence in analysis")
        elif self.confidence > 0.6:
            reasoning_parts.append("Moderate confidence with acceptable risk")
        else:
            reasoning_parts.append("Lower confidence suggests cautious approach")
        
        # Market context
        if context.get('market_trend') == 'bullish':
            reasoning_parts.append("Market conditions support positive positioning")
        elif context.get('market_trend') == 'bearish':
            reasoning_parts.append("Market headwinds suggest defensive positioning")
        
        return ". ".join(reasoning_parts) + "."
    
    def _assess_risk(self) -> str:
        """Assess risk level based on agent characteristics"""
        
        if 'Risk' in self.specialty:
            return 'low'  # Risk specialists are conservative
        elif self.confidence > 0.85:
            return 'low'
        elif self.confidence > 0.65:
            return 'medium'
        else:
            return 'high'
    
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
        self.decision_history = []
        
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
        """Conduct weighted voting across all agents with detailed decisions"""
        
        vote_tally = {}
        total_weight = 0
        participating_agents = []
        agent_decisions = []
        
        # Include all enhanced agents in voting
        for agent_name, agent in self.enhanced_agents.items():
            # Generate decision
            decision = agent.make_decision(context)
            agent_decisions.append(decision)
            
            # Generate signal for voting
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
                'department': agent.department,
                'decision': decision.to_dict()
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
            'timestamp': datetime.now().isoformat(),
            'agent_decisions': agent_decisions,
            'detailed_votes': participating_agents
        }
        
        # Store voting session
        self.voting_sessions.append(voting_result)
        self.decision_history.extend(agent_decisions)
        
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
            'personas_active': len([a for a in self.enhanced_agents.values() if a.persona]),
            'total_decisions_made': len(self.decision_history),
            'operational_status': 'fully_active'
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
    
    def get_decision_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent decision history"""
        recent_decisions = sorted(self.decision_history, key=lambda d: d.timestamp, reverse=True)[:limit]
        return [decision.to_dict() for decision in recent_decisions]
    
    def get_department_performance(self) -> Dict[str, Dict[str, float]]:
        """Get performance metrics by department"""
        performance = {}
        
        for dept in ['market_intelligence', 'trade_operations', 'risk_control', 'performance_lab', 'communications']:
            dept_agents = [agent for agent in self.enhanced_agents.values() if agent.department == dept]
            
            if dept_agents:
                performance[dept] = {
                    'avg_confidence': np.mean([agent.confidence for agent in dept_agents]),
                    'avg_performance': np.mean([agent.performance for agent in dept_agents]),
                    'agent_count': len(dept_agents)
                }
        
        return performance