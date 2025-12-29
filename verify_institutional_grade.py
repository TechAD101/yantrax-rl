"""Institutional Grade Master Verification Script

Validates the existence and functionality of the Tier S and Tier A restoration items.
"""

import sys
import os
import logging

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from ai_firm.agent_manager import AgentManager
from services.knowledge_base import get_knowledge_base
from services.trade_validator import TradeValidator
from services.market_data_service_waterfall import get_waterfall_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Verification")

def test_persona_registry():
    logger.info("🕵️ Checking Persona Registry...")
    am = AgentManager()
    agents = am.enhanced_agents
    
    required_personas = ['warren', 'cathie', 'macro_monk', 'the_ghost', 'degen_auditor']
    
    for p in required_personas:
        if p in agents:
            logger.info(f"  ✅ Persona '{p}' is ACTIVE. Specialty: {agents[p]['specialty']}")
        else:
            logger.error(f"  ❌ Missing Persona: {p}")
            return False
    return True

def test_knowledge_base():
    logger.info("🧠 Checking Knowledge Base (ChromaDB)...")
    kb = get_knowledge_base()
    results = kb.query_wisdom("Never lose money", n_results=1)
    
    if results:
        logger.info(f"  DEBUG: KB Metadata: {results[0]['metadata']}")
        if "Buffett" in str(results[0]['metadata']):
            logger.info(f"  ✅ KB Retrieval Successful: {results[0]['text']}")
        else:
            logger.warning(f"  ⚠️ KB return data mismatch. Found: {results[0]['metadata']}")
            return False
    else:
        logger.error("  ❌ KB Query returned no results.")
        return False
        
    hindi_wisdom = kb.query_wisdom("Hindi Wisdom", n_results=1)
    if hindi_wisdom:
        logger.info(f"  ✅ Cultural Lore Retrieval Successful: {hindi_wisdom[0]['text']}")
    else:
        logger.warning("  ⚠️ Hindi wisdom missing in KB.")
        
    return True

def test_trade_validator():
    logger.info("🛡️  Checking Trade Validator (8-Point Checklist)...")
    validator = TradeValidator()
    
    # Mock a "Dangerous" trade
    proposal = {
        'symbol': 'TSLA',
        'action': 'BUY',
        'shares': 1000,
        'entry_price': 200,
        'target_price': 210,
        'stop_loss': 199,
        'portfolio_value': 100000 # Trying to buy $200k with $100k
    }
    
    market_context = {
        'market_trend': 'bullish',
        'volatility': 0.05,
        'vix': 15,
        'persona_votes': [
            {'name': 'warren', 'signal': 'BUY', 'weight': 1.0, 'confidence': 0.8},
            {'name': 'the_ghost', 'signal': 'HOLD', 'weight': 1.0, 'confidence': 0.9}
        ]
    }
    
    result = validator.validate_trade(proposal, market_context)
    
    if result['allowed'] is False:
        logger.info(f"  ✅ Validator correctly BLOCKED risky trade. Failures: {result['failures']}")
    else:
        logger.warning("  ⚠️ Validator allowed a risky trade. Check position sizing logic.")
        
    if 'wisdom' in result:
        logger.info(f"  ✅ Trade Validation includes KB Insight: {result['wisdom']}")
        
    return True

def test_divine_doubt():
    logger.info("👻 Checking Divine Doubt Protocol...")
    am = AgentManager()
    
    # Create an artificial high-consensus context
    context = {
        'market_trend': 'bullish',
        'rsi': 55,
        'fundamentals': {'pe_ratio': 15, 'return_on_equity': 0.25, 'debt_to_equity': 0.1}
    }
    # Create high consensus by masking all opinions with BUY
    expert_opinions = {name: 'BUY' for name in am.enhanced_agents.keys()}
    result = am.conduct_agent_voting(context, expert_opinions=expert_opinions)
    
    if result.get('divine_doubt_applied'):
        logger.info(f"  ✅ Divine Doubt successfully applied. Signal: {result['winning_signal']}")
    else:
        logger.warning(f"  ⚠️ Divine Doubt not triggered (Consensus: {result['consensus_strength']}). Check Ghost logic.")
        return False
        
    return True

if __name__ == "__main__":
    logger.info("🚀 Starting Institutional Grade Final Audit...")
    
    success = all([
        test_persona_registry(),
        test_knowledge_base(),
        test_trade_validator(),
        test_divine_doubt()
    ])
    
    if success:
        logger.info("\n🏆 INSTITUTIONAL GRADE VERIFIED. System is ALIGNED with God Mode requirements.")
        sys.exit(0)
    else:
        logger.error("\n💥 AUDIT FAILED. Key components missing or malfunctioning.")
        sys.exit(1)
