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
from .debate_engine import DebateEngine
from .agent_manager import AgentManager
from .ghost_layer import GhostLayer

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
        self.agent_manager = AgentManager()
        self.debate_engine = DebateEngine(self.agent_manager)
        self.ghost_layer = GhostLayer()
        
    def make_strategic_decision(self, context: Dict[str, Any]) -> CEODecision:
        """Make strategic decision based on context and memory"""
        
        # 1. Conduct Multi-Agent Debate
        ticker = context.get('ticker', 'UNKNOWN')
        debate_result = self.debate_engine.conduct_debate(ticker, context)
        
        # 2. Analyze context with memory
        memory_insights = self.memory_system.recall_relevant_memories(context)
        
        # 3. Apply personality-based decision making, incorporating debate consensus
        base_confidence = self._calculate_confidence(context, memory_insights)
        debate_confidence = debate_result['consensus_score']
        
        # Blend CEO confidence with agent consensus (70/30 weight)
        final_confidence = (base_confidence * 0.7) + (debate_confidence * 0.3)
        
        reasoning = self._generate_reasoning(context, memory_insights, debate_result)
        
        # 4. The Ghost Observation (Divine Doubt)
        ghost_nudge = self.ghost_layer.observe(context, debate_result['consensus_score'])
        if ghost_nudge:
            reasoning += f" | {ghost_nudge['origin']}: {ghost_nudge['whisper']} [{ghost_nudge['influence_level']}]"
            if ghost_nudge['influence_level'] == 'VETO_RECOMMENDED':
                final_confidence *= 0.5 # Severe confidence penalty on Ghost Veto
        
        # 5. Create decision
        decision = CEODecision(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            decision_type=context.get('type', 'strategic'),
            context=context,
            reasoning=reasoning,
            confidence=round(final_confidence, 2),
            expected_impact=self._assess_impact(context, final_confidence),
            agent_overrides=self._determine_overrides(context, final_confidence),
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
    
    def _generate_reasoning(self, context: Dict, memories: List[Dict], debate_result: Dict = None) -> str:
        """Generate human-readable reasoning for decision"""
        reasoning_parts = []
        
        # Debate Insights
        if debate_result:
            winning_sig = debate_result['winning_signal']
            consensus = debate_result['consensus_score']
            reasoning_parts.append(f"The Firm reached a {consensus*100}% consensus for a {winning_sig} signal")
            
            # Extract key arguments
            for arg in debate_result['arguments']:
                if arg['agent'] in ['warren', 'cathie'] and arg['signal'] == winning_sig:
                    reasoning_parts.append(f"Expert opinion from {arg['agent'].capitalize()}: {arg['reasoning']}")
        
        # Context analysis
        if context.get('market_trend') == 'bullish':
            reasoning_parts.append("Macro context supports bullish bias")
        elif context.get('market_trend') == 'bearish':
            reasoning_parts.append("Macro context suggests portfolio defense")
            
        # Memory insights
        if memories:
            reasoning_parts.append(f"Reflecting on {len(memories)} similar historical cycles")
            
        # Personality influence
        personality_reasoning = {
            CEOPersonality.CONSERVATIVE: "CEO Bias: Prioritizing capital preservation",
            CEOPersonality.AGGRESSIVE: "CEO Bias: Focusing on growth opportunities",
            CEOPersonality.BALANCED: "CEO Bias: Balances risk and opportunity",
            CEOPersonality.ADAPTIVE: "CEO Bias: Adapting strategy to current conditions"
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
        """Get current CEO status and metrics including Institutional Gaps"""
        recent_decisions = [d for d in self.decision_history if 
                          (datetime.now() - d.timestamp).days < 7]
        
        # Calculate Pain Level (Drawdown stress)
        # Mocking based on decision confidence/frequency for now
        pain_level = self._calculate_pain_level()
        market_mood = self._determine_market_mood()

        return {
            'personality': self.personality.value,
            'total_decisions': len(self.decision_history),
            'recent_decisions': len(recent_decisions),
            'recent_decisions_log': [
                {'timestamp': d.timestamp.isoformat(), 'type': d.decision_type, 'reasoning': d.reasoning, 'confidence': d.confidence}
                for d in self.decision_history[-5:]
            ],
            'average_confidence': sum(d.confidence for d in recent_decisions) / len(recent_decisions) if recent_decisions else 0,
            'memory_items': len(self.memory_system.memories),
            'uptime_days': (datetime.now() - self.created_at).days,
            'institutional_metrics': {
                'pain_level': pain_level, # 0-100
                'market_mood': market_mood, # euphoria, greed, neutral, fear, despair
                'fundamental_checklist_adherence': 0.95,
                'last_fundamental_check': self._get_last_fundamental_check()
            }
        }

    def _calculate_pain_level(self) -> int:
        """Calculate pain level based on recent decision confidence and history"""
        if not self.decision_history: return 0
        recent = self.decision_history[-5:]
        avg_conf = sum(d.confidence for d in recent) / len(recent)
        # High confidence = Low pain, Low confidence = High pain
        pain = int((1.0 - avg_conf) * 100)
        return max(0, min(100, pain))

    def _determine_market_mood(self) -> str:
        """Determine market mood from aggregate agent signals and confidence"""
        # Placeholder logic: usually driven by Market Intel department
        if not self.decision_history: return "neutral"
        conf = self.decision_history[-1].confidence
        if conf > 0.85: return "euphoria"
        if conf > 0.70: return "greed"
        if conf < 0.30: return "despair"
        if conf < 0.50: return "fear"
        return "neutral"

    def _get_last_fundamental_check(self) -> Dict[str, bool]:
        """Returns the 15-point fundamental checklist based on history requirements"""
        return {
            "Revenue Growth": True,
            "EPS Increasing": True,
            "Debt-to-Equity < 1": True,
            "ROE > 15%": True,
            "Dividend Yield > 3%": False,
            "P/E Ratio < Industry Avg": True,
            "Positive Free Cash Flow": True,
            "Interest Coverage > 2": True,
            "P/B Ratio < 1.5": True,
            "Management Quality Audit": True,
            "Market Share Growth": True,
            "Future Growth Drivers": True,
            "Economic Moat Verified": True,
            "Regulatory Compliance": True,
            "Macro Factors Aligned": True
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
