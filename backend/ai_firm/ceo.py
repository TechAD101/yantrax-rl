"""Autonomous CEO Module

Implements the autonomous CEO with memory system, strategic oversight,
and decision-making authority over the 20+ agent AI firm.
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib

class CEOPersonality(Enum):
    CONSERVATIVE = "conservative"
    AGGRESSIVE = "aggressive"
    BALANCED = "balanced"
    ADAPTIVE = "adaptive"

@dataclass
class CEODecision:
    """CEO decision record with reasoning and impact assessment"""
    id: str
    timestamp: datetime
    decision_type: str
    context: Dict[str, Any]
    reasoning: str
    confidence: float
    expected_impact: str
    agent_overrides: List[str]
    memory_references: List[str]
    
class AutonomousCEO:
    """Autonomous CEO with memory and decision-making capabilities"""
    
    def __init__(self, personality: CEOPersonality = CEOPersonality.BALANCED):
        self.personality = personality
        self.memory_system = CEOMemorySystem()
        self.decision_history = []
        self.learning_rate = 0.1
        self.confidence_threshold = 0.75
        self.created_at = datetime.now()
        
    def make_strategic_decision(self, context: Dict[str, Any]) -> CEODecision:
        """Make strategic decision based on context and memory"""
        
        # Analyze context with memory
        memory_insights = self.memory_system.recall_relevant_memories(context)
        
        # Apply personality-based decision making
        confidence = self._calculate_confidence(context, memory_insights)
        reasoning = self._generate_reasoning(context, memory_insights)
        
        # Create decision
        decision = CEODecision(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            decision_type=context.get('type', 'strategic'),
            context=context,
            reasoning=reasoning,
            confidence=confidence,
            expected_impact=self._assess_impact(context, confidence),
            agent_overrides=self._determine_overrides(context, confidence),
            memory_references=[m['id'] for m in memory_insights]
        )
        
        # Store decision
        self.decision_history.append(decision)
        
        # Update memory with decision outcome
        self.memory_system.store_decision_memory(decision)
        
        return decision
    
    def evaluate_agent_performance(self, agent_reports: List[Dict]) -> Dict[str, Any]:
        """Evaluate multi-agent performance and provide feedback"""
        
        performance_analysis = {
            'overall_score': 0.0,
            'agent_scores': {},
            'recommendations': [],
            'strategy_adjustments': [],
            'risk_concerns': []
        }
        
        total_score = 0
        for report in agent_reports:
            agent_name = report.get('name', 'unknown')
            score = self._evaluate_agent_report(report)
            performance_analysis['agent_scores'][agent_name] = score
            total_score += score
            
        performance_analysis['overall_score'] = total_score / len(agent_reports) if agent_reports else 0
        
        # Generate CEO recommendations
        if performance_analysis['overall_score'] < 0.6:
            performance_analysis['recommendations'].append(
                "Consider rebalancing agent weights and strategies"
            )
            
        # Store performance memory
        self.memory_system.store_performance_memory(performance_analysis)
        
        return performance_analysis
    
    def _calculate_confidence(self, context: Dict, memories: List[Dict]) -> float:
        """Calculate confidence based on context and historical memory"""
        base_confidence = 0.5
        
        # Adjust based on personality
        if self.personality == CEOPersonality.CONSERVATIVE:
            base_confidence *= 0.8
        elif self.personality == CEOPersonality.AGGRESSIVE:
            base_confidence *= 1.2
            
        # Adjust based on memory relevance
        memory_boost = min(0.3, len(memories) * 0.05)
        
        # Adjust based on market conditions
        market_volatility = context.get('volatility', 0.1)
        volatility_penalty = market_volatility * 0.2
        
        confidence = min(1.0, max(0.1, base_confidence + memory_boost - volatility_penalty))
        
        return confidence
    
    def _generate_reasoning(self, context: Dict, memories: List[Dict]) -> str:
        """Generate human-readable reasoning for decision"""
        reasoning_parts = []
        
        # Context analysis
        if context.get('market_trend') == 'bullish':
            reasoning_parts.append("Market shows bullish signals")
        elif context.get('market_trend') == 'bearish':
            reasoning_parts.append("Market conditions indicate caution")
            
        # Memory insights
        if memories:
            reasoning_parts.append(f"Historical analysis of {len(memories)} similar situations")
            
        # Personality influence
        personality_reasoning = {
            CEOPersonality.CONSERVATIVE: "Prioritizing capital preservation",
            CEOPersonality.AGGRESSIVE: "Focusing on growth opportunities",
            CEOPersonality.BALANCED: "Balancing risk and opportunity",
            CEOPersonality.ADAPTIVE: "Adapting strategy to current conditions"
        }
        
        reasoning_parts.append(personality_reasoning[self.personality])
        
        return ". ".join(reasoning_parts) + "."
    
    def _assess_impact(self, context: Dict, confidence: float) -> str:
        """Assess expected impact of decision"""
        if confidence > 0.8:
            return "High positive impact expected"
        elif confidence > 0.6:
            return "Moderate positive impact expected"
        elif confidence > 0.4:
            return "Neutral to slight positive impact"
        else:
            return "Low confidence - monitor closely"
            
    def _determine_overrides(self, context: Dict, confidence: float) -> List[str]:
        """Determine which agents to override based on decision"""
        overrides = []
        
        if confidence < 0.3:
            overrides.append("Risk_Auditor_Override")
            
        if context.get('emergency', False):
            overrides.extend(["All_Agent_Override", "Emergency_Protocol"])
            
        return overrides
    
    def _evaluate_agent_report(self, report: Dict) -> float:
        """Evaluate individual agent performance"""
        # Base score from confidence
        score = report.get('confidence', 0.5)
        
        # Adjust for accuracy if available
        if 'accuracy' in report:
            score = (score + report['accuracy']) / 2
            
        # Penalty for excessive risk
        if report.get('risk_level', 'medium') == 'high':
            score *= 0.8
            
        return min(1.0, max(0.0, score))
    
    def get_ceo_status(self) -> Dict[str, Any]:
        """Get current CEO status and metrics"""
        recent_decisions = [d for d in self.decision_history if 
                          (datetime.now() - d.timestamp).days < 7]
        
        return {
            'personality': self.personality.value,
            'total_decisions': len(self.decision_history),
            'recent_decisions': len(recent_decisions),
            'average_confidence': sum(d.confidence for d in recent_decisions) / len(recent_decisions) if recent_decisions else 0,
            'memory_items': len(self.memory_system.memories),
            'uptime_days': (datetime.now() - self.created_at).days
        }

class CEOMemorySystem:
    """Memory system for CEO learning and decision making"""
    
    def __init__(self):
        self.memories = []
        self.memory_index = {}
        
    def store_decision_memory(self, decision: CEODecision):
        """Store decision in memory for future reference"""
        memory_item = {
            'id': str(uuid.uuid4()),
            'type': 'decision',
            'timestamp': decision.timestamp,
            'content': {
                'decision_type': decision.decision_type,
                'confidence': decision.confidence,
                'context_hash': self._hash_context(decision.context),
                'reasoning': decision.reasoning
            },
            'tags': self._extract_tags(decision.context)
        }
        
        self.memories.append(memory_item)
        self._update_index(memory_item)
        
    def store_performance_memory(self, performance: Dict[str, Any]):
        """Store performance evaluation in memory"""
        memory_item = {
            'id': str(uuid.uuid4()),
            'type': 'performance',
            'timestamp': datetime.now(),
            'content': performance,
            'tags': ['performance', 'evaluation']
        }
        
        self.memories.append(memory_item)
        self._update_index(memory_item)
        
    def recall_relevant_memories(self, context: Dict) -> List[Dict]:
        """Recall memories relevant to current context"""
        context_tags = self._extract_tags(context)
        relevant_memories = []
        
        for memory in self.memories:
            relevance_score = self._calculate_relevance(memory, context_tags)
            if relevance_score > 0.3:
                memory_copy = memory.copy()
                memory_copy['relevance'] = relevance_score
                relevant_memories.append(memory_copy)
                
        # Sort by relevance and recency
        relevant_memories.sort(
            key=lambda m: (m['relevance'], m['timestamp']), 
            reverse=True
        )
        
        return relevant_memories[:5]  # Return top 5 most relevant
    
    def _hash_context(self, context: Dict) -> str:
        """Create hash of context for similarity matching"""
        context_str = json.dumps(context, sort_keys=True, default=str)
        return hashlib.md5(context_str.encode()).hexdigest()[:8]
    
    def _extract_tags(self, context: Dict) -> List[str]:
        """Extract relevant tags from context"""
        tags = []
        
        # Market condition tags
        if 'market_trend' in context:
            tags.append(f"trend_{context['market_trend']}")
            
        # Volatility tags
        volatility = context.get('volatility', 0)
        if volatility > 0.3:
            tags.append('high_volatility')
        elif volatility < 0.1:
            tags.append('low_volatility')
            
        # Decision type tags
        if 'type' in context:
            tags.append(context['type'])
            
        return tags
    
    def _calculate_relevance(self, memory: Dict, context_tags: List[str]) -> float:
        """Calculate relevance score between memory and context"""
        memory_tags = memory.get('tags', [])
        
        # Tag overlap score
        common_tags = set(memory_tags) & set(context_tags)
        tag_score = len(common_tags) / max(len(memory_tags), len(context_tags), 1)
        
        # Recency score (newer memories slightly more relevant)
        days_old = (datetime.now() - memory['timestamp']).days
        recency_score = max(0, 1 - (days_old / 365))  # Decay over a year
        
        # Combine scores
        relevance = (tag_score * 0.7) + (recency_score * 0.3)
        
        return relevance
    
    def _update_index(self, memory_item: Dict):
        """Update memory index for faster retrieval"""
        for tag in memory_item.get('tags', []):
            if tag not in self.memory_index:
                self.memory_index[tag] = []
            self.memory_index[tag].append(memory_item['id'])
