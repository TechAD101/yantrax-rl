"""
AI Firm Core Integration Guide

This document provides code snippets to integrate the new Tier S services
(PersonaRegistry, TradeValidator, KnowledgeBase) into the existing AI Firm Core.

CRITICAL: These integrations ensure the new services are actually USED, not just available.
"""

# ====================================================================================
# INTEGRATION 1: TradeValidator in CEO/Main Trading Flow
# ====================================================================================

# File: backend/main.py or backend/ai_firm/ceo.py
# Location: Wherever trading decisions are executed

"""
BEFORE (No validation):
```python
trade_signal = generate_trade_signal(symbol, context)
if trade_signal['action'] != 'HOLD':
    execute_trade(trade_signal)  # RISKY - no validation!
```

AFTER (With TradeValidator):
```python
trade_signal = generate_trade_signal(symbol, context)

if trade_signal['action'] != 'HOLD':
    # VALIDATE FIRST
    from services.trade_validator import get_trade_validator
    trade_validator = get_trade_validator()
    
    # Prepare trade proposal
    trade_proposal = {
        'symbol': symbol,
        'action': trade_signal['action'],
        'shares': trade_signal.get('shares', 100),
        'entry_price': context.get('current_price'),
        'target_price': trade_signal.get('target_price'),
        'stop_loss': trade_signal.get('stop_loss'),
        'portfolio_value': get_portfolio_value()
    }
    
    # Prepare market context
    market_context = {
        'market_trend': context.get('market_trend', 'neutral'),
        'volatility': context.get('volatility', 0.2),
        'vix': context.get('vix', 20),
        'persona_votes': context.get('persona_votes', []),
        'volume': context.get('volume', 1000000),
        'bid_ask_spread': context.get('bid_ask_spread', 0.005)
    }
    
    # Validate
    validation = trade_validator.validate_trade(trade_proposal, market_context)
    
    if validation['allowed']:
        logger.info(f\"✅ Trade APPROVED: {symbol} {trade_signal['action']}\")
        execute_trade(trade_signal)
    else:
        logger.warning(
            f\"❌ Trade BLOCKED: {symbol}. Failed checks: {validation['failures']}\"
        )
        # Log blocked trade for analysis
        record_blocked_trade(trade_signal, validation)
```
"""

# ====================================================================================
# INTEGRATION 2: PersonaRegistry in DebateEngine
# ====================================================================================

# File: backend/ai_firm/debate_engine.py

"""
BEFORE (Uses AgentManager personas):
```python
for agent_name, agent_data in self.agent_manager.enhanced_agents.items():
    if agent_data.get('persona', False):
        signal = self.agent_manager._generate_agent_signal(agent_name, agent_data, context)
        # ...
```

AFTER (Uses PersonaRegistry for formal voting):
```python
from ai_agents.persona_registry import get_persona_registry

class DebateEngine:
    def __init__(self, agent_manager):
        self.agent_manager = agent_manager
        self.persona_registry = get_persona_registry()  # NEW
        # ...
    
    def conduct_debate_with_personas(self, ticker: str, context: Dict[str, Any]) -> Dict[str, Any]:
        '''Enhanced debate using PersonaRegistry for formal voting'''
        
        # 1. Get persona votes through PersonaRegistry
        proposal = {
            'symbol': ticker,
            'action': context.get('proposed_action', 'BUY')
        }
        
        vote_result = self.persona_registry.conduct_vote(proposal, context)
        
        # 2. Combine with traditional agent signals
        agent_signals = self._gather_agent_signals(ticker, context)
        
        # 3. Merge results
        return {
            'ticker': ticker,
            'persona_consensus': vote_result['consensus'],
            'persona_strength': vote_result['consensus_strength'],
            'persona_votes': vote_result['votes'],
            'agent_signals': agent_signals,
            'combined_confidence': self._blend_confidence(vote_result, agent_signals),
            'reasoning': self._merge_reasoning(vote_result, agent_signals)
        }
```
"""

# ====================================================================================
# INTEGRATION 3: KnowledgeBase in PersonaAgent.analyze()
# ====================================================================================

# File: backend/ai_agents/personas/warren.py or cathie.py

"""
BEFORE (No knowledge context):
```python
def analyze(self, context: Dict[str, Any]) -> PersonaAnalysis:
    symbol = context.get('symbol')
    fundamentals = context.get('fundamentals', {})
    
    # Run analysis logic...
    recommendation = self._evaluate(fundamentals)
    
    return PersonaAnalysis(...)
```

AFTER (With knowledge context enrichment):
```python
from services.knowledge_base_service import get_knowledge_base

def analyze(self, context: Dict[str, Any]) -> PersonaAnalysis:
    symbol = context.get('symbol')
    fundamentals = context.get('fundamentals', {})
    
    # ENRICH with knowledge base
    kb = get_knowledge_base()
    kb_context = kb.get_persona_context(
        persona_name=self.name.lower(),
        symbol=symbol,
        market_context=context
    )
    
    # Run analysis logic...
    recommendation = self._evaluate(fundamentals)
    
    # Enhance reasoning with wisdom
    reasoning = self._generate_reasoning(fundamentals, recommendation)
    if kb_context['context_enriched'] and kb_context['relevant_wisdom']:
        top_wisdom = kb_context['relevant_wisdom'][0]
        reasoning += f\" | Wisdom: '{top_wisdom['content'][:100]}...' - {top_wisdom['source']}\"
    
    return PersonaAnalysis(
        persona_name=self.name,
        symbol=symbol,
        recommendation=recommendation,
        confidence=self._calculate_confidence(fundamentals),
        reasoning=reasoning,  # Now includes wisdom
        scores=self._calculate_scores(fundamentals),
        timestamp=datetime.now()
    )
```
"""

# ====================================================================================
# INTEGRATION 4: Update AgentManager to delegate to PersonaRegistry
# ====================================================================================

# File: backend/ai_firm/agent_manager.py

"""
ADDITION (Delegate persona queries to PersonaRegistry):
```python
from ai_agents.persona_registry import get_persona_registry

class AgentManager:
    def __init__(self):
        # ... existing initialization ...
        self.persona_registry = get_persona_registry()  # NEW
    
    def get_persona_analysis(self, persona_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        '''Get analysis from a specific persona via PersonaRegistry'''
        persona = self.persona_registry.get_persona(persona_name)
        if not persona:
            return {'error': f'Persona {persona_name} not found'}
        
        analysis = persona.analyze(context)
        return analysis.to_dict()
    
    def conduct_persona_vote(self, proposal: Dict[str, Any], market_context: Dict[str, Any]) -> Dict[str, Any]:
        '''Delegate voting to PersonaRegistry'''
        return self.persona_registry.conduct_vote(proposal, market_context)
    
    def get_all_persona_summaries(self) -> List[Dict[str, Any]]:
        '''Get performance summaries of all personas'''
        return self.persona_registry.get_all_summaries()
```
"""

# ====================================================================================
# INTEGRATION 5: Expose Institutional Metrics in /api/ai-firm/status
# ====================================================================================

# File: backend/main.py

"""
ENHANCEMENT (Add new service metrics to status endpoint):
```python
@app.route('/api/ai-firm/status', methods=['GET'])
def ai_firm_status():
    # ... existing code ...
    
    # Add persona summaries
    persona_summaries = PERSONA_REGISTRY.get_all_summaries() if PERSONA_REGISTRY else []
    
    # Add knowledge base stats
    kb_stats = KNOWLEDGE_BASE.get_statistics() if KNOWLEDGE_BASE else {}
    
    # Add validation stats
    validation_stats = TRADE_VALIDATOR.get_validation_stats() if TRADE_VALIDATOR else {}
    
    # Add verification stats
    verification_stats = market_provider.get_verification_stats() if hasattr(market_provider, 'get_verification_stats') else {}
    
    return jsonify({
        'status': 'fully_operational',
        'ai_firm': {
            'total_agents': 24,
            'departments': agent_status,
            'ceo_metrics': ceo_stats,
            'personas_active': len(persona_summaries),
            'personas': persona_summaries  # NEW
        },
        'institutional_services': {  # NEW SECTION
            'knowledge_base': kb_stats,
            'trade_validation': validation_stats,
            'data_verification': verification_stats
        },
        'system_performance': {
            'portfolio_balance': 132450.00,
            'success_rate': 92,
            'pain_level': ceo_stats.get('institutional_metrics', {}).get('pain_level', 0),
            'market_mood': ceo_stats.get('institutional_metrics', {}).get('market_mood', 'neutral')
        },
        'timestamp': datetime.now().isoformat()
    }), 200
```
"""

# ====================================================================================
# SUMMARY OF INTEGRATION POINTS
# ====================================================================================

"""
1. ✅ TradeValidator: Integrate into trading execution flow (CEO or main.py)
2. ✅ PersonaRegistry: Use in DebateEngine for formal voting
3. ✅ KnowledgeBase: Enrich PersonaAgent.analyze() with wisdom context
4. ✅ AgentManager: Delegate persona operations to PersonaRegistry
5. ✅ API Status: Expose institutional metrics in /api/ai-firm/status

These integrations ensure the new services are not just standalone components
but actively used in the trading decision-making flow.
"""
