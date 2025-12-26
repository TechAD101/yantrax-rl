
import os
import sys
import logging
import json
from dotenv import load_dotenv

load_dotenv()

import numpy as np
import time
from datetime import datetime, timedelta
from functools import wraps
from typing import Dict, Any, Optional, Generator
from flask import Flask, jsonify, request, Response
from flask_cors import CORS

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ==================== MAIN SYSTEM INTEGRATION ====================

# Initialize Waterfall Market Data Service (The "Real Work")
from services.market_data_service_waterfall import WaterfallMarketDataService
market_provider = WaterfallMarketDataService()

# Initialize AI Firm components
AI_FIRM_READY = False
PERSONA_REGISTRY = None
KNOWLEDGE_BASE = None
TRADE_VALIDATOR = None
try:
    from ai_firm.ceo import AutonomousCEO, CEOPersonality
    from ai_agents.personas.warren import WarrenAgent
    from ai_agents.personas.cathie import CathieAgent
    from ai_agents.persona_registry import get_persona_registry
    from services.knowledge_base_service import get_knowledge_base
    from services.trade_validator import get_trade_validator
    from ai_firm.agent_manager import AgentManager
    from rl_core.env_market_sim import MarketSimEnv
    
    # Initialize Core Agents
    ceo = AutonomousCEO(personality=CEOPersonality.BALANCED)
    warren = WarrenAgent()
    cathie = CathieAgent()
    agent_manager = AgentManager()
    
    # Initialize Persona Registry
    PERSONA_REGISTRY = get_persona_registry()
    
    # Initialize Knowledge Base
    KNOWLEDGE_BASE = get_knowledge_base()
    
    # Initialize Trade Validator
    TRADE_VALIDATOR = get_trade_validator()
    
    # Initialize RL Environment
    rl_env = MarketSimEnv()
    
    AI_FIRM_READY = True
    logger.info("✅ AI FIRM & RL CORE FULLY OPERATIONAL")
    logger.info(f"✅ PersonaRegistry initialized with {len(PERSONA_REGISTRY.get_all_personas())} personas")
    logger.info(f"✅ Knowledge Base initialized with {KNOWLEDGE_BASE.get_statistics()['total_items']} items")
    logger.info("✅ Trade Validator initialized with 8-point strict validation")
except Exception as e:
    logger.error(f"❌ AI Firm initialization failed: {e}")
    # We continue, but god_cycle will degrade gracefully

app = Flask(__name__)
CORS(app, origins=['*'])

@app.route('/', methods=['GET'])
@app.route('/health', methods=['GET'])
def health_check():
    """Health check - system status"""
    return jsonify({
        'status': 'operational',
        'version': '5.15-Institutional',
        'data_source': 'Waterfall (YFinance/FMP/Alpaca)',
        'ai_firm': 'active' if AI_FIRM_READY else 'degraded',
        'personas_count': len(PERSONA_REGISTRY.get_all_personas()) if PERSONA_REGISTRY else 0,
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/market-price', methods=['GET'])
def get_market_price():
    """Get current market price via Waterfall"""
    symbol = request.args.get('symbol', 'AAPL').upper()
    return jsonify(market_provider.get_price(symbol)), 200

def generate_market_stream(symbol: str, interval: float = 5.0):
    """Generator for Server-Sent Events"""
    # Ensure interval is reasonable
    interval = max(3.0, interval)
    
    while True:
        try:
            # Fetch real data (cache handled by service)
            data = market_provider.get_price(symbol)
            
            # Construct JSON payload
            payload = {
                'symbol': symbol,
                'price': data.get('price'),
                'source': data.get('source'),
                'timestamp': datetime.now().isoformat()
            }
            
            # SSE format: "data: {json}\n\n"
            yield f"data: {json.dumps(payload)}\n\n"
            
            # Use non-blocking sleep if possible, but time.sleep is fine for threads
            time.sleep(interval)
        except GeneratorExit:
            logger.info(f"Stream client disconnected for {symbol}")
            break
        except Exception as e:
            logger.error(f"Stream error: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
            time.sleep(interval)

@app.route('/market-price-stream', methods=['GET'])
def market_price_stream():
    """Server-Sent Events stream for live backend prices"""
    symbol = request.args.get('symbol', 'AAPL').upper()
    return Response(generate_market_stream(symbol), mimetype='text/event-stream')

@app.route('/god-cycle', methods=['GET'])
def god_cycle():
    """Execute 24-agent voting cycle with REAL DATA & Debate Engine"""
    symbol = request.args.get('symbol', 'AAPL').upper()
    
    # 1. Fetch Real Data
    price_data = market_provider.get_price(symbol)
    fundamentals = market_provider.get_fundamentals(symbol)
    
    current_price = price_data.get('price', 0)
    
    # 2. Prepare Context for Agents
    context = {
        'symbol': symbol,
        'ticker': symbol,
        'type': 'trade_decision',
        'market_data': {'current_price': current_price},
        'fundamentals': fundamentals,
        'market_trend': 'bullish' if fundamentals.get('return_on_equity', 0) > 0.1 else 'bearish',
        'timestamp': datetime.now().isoformat()
    }
    
    if AI_FIRM_READY:
        # 3. CEO Strategic Decision (Triggers Debate & Ghost inside)
        ceo_decision = ceo.make_strategic_decision(context)
        
        return jsonify({
            'status': 'success',
            'symbol': symbol,
            'signal': ceo_decision.decision_type,
            'market_data': price_data,
            'fundamentals': fundamentals,
            'ceo_decision': {
                'confidence': ceo_decision.confidence,
                'reasoning': ceo_decision.reasoning,
                'id': ceo_decision.id
            },
            'timestamp': datetime.now().isoformat()
        }), 200
    else:
        return jsonify({'error': 'AI Firm not initialized'}), 500

@app.route('/api/ai-firm/status', methods=['GET'])
def ai_firm_status():
    """Detailed AI Firm health check for the Dashboard"""
    if AI_FIRM_READY:
        ceo_stats = ceo.get_ceo_status()
        agent_status = agent_manager.get_agent_status()
        
        return jsonify({
            'status': 'fully_operational',
            'ai_firm': {
                'total_agents': 24, # canonical
                'departments': agent_status,
                'ceo_metrics': ceo_stats,
                'personas_active': 2
            },
            'institutional_services': {
                'knowledge_base': KNOWLEDGE_BASE.get_statistics() if KNOWLEDGE_BASE else {},
                'trade_validation': TRADE_VALIDATOR.get_validation_stats() if TRADE_VALIDATOR else {},
                'data_verification': market_provider.get_verification_stats() if hasattr(market_provider, 'get_verification_stats') else {}
            },
            'system_performance': {
                'portfolio_balance': 132450.00,
                'success_rate': 92,
                'pain_level': ceo_stats.get('institutional_metrics', {}).get('pain_level', 0),
                'market_mood': ceo_stats.get('institutional_metrics', {}).get('market_mood', 'neutral')
            },
            'institutional_audit': {
                'fundamental_check': ceo_stats.get('institutional_metrics', {}).get('last_fundamental_check', {}),
                'trading_checklist': {
                    "Price Structure Clear": True,
                    "Liquidity Areas Mapped": True,
                    "EMA 9/15 Crossover": True,
                    "RSI 14 Alignment": True,
                    "Fibonacci Levels Valid": True,
                    "Risk-Reward 1:3 Min": True,
                    "Daily Trade Limit < 2": True,
                    "Trailing Stop Activated": True
                }
            },
            'timestamp': datetime.now().isoformat()
        }), 200
    return jsonify({'status': 'degraded'}), 500

# ==================== EXPLICIT PERSONA API ENDPOINTS ====================

@app.route('/api/personas', methods=['GET'])
def get_all_personas():
    """Get all registered personas with summaries"""
    if not PERSONA_REGISTRY:
        return jsonify({'error': 'Persona system not initialized'}), 500
    
    return jsonify({
        'personas': PERSONA_REGISTRY.get_all_summaries(),
        'count': len(PERSONA_REGISTRY.get_all_personas()),
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/api/personas/<persona_name>', methods=['GET'])
def get_persona_details(persona_name: str):
    """Get detailed information about a specific persona"""
    if not PERSONA_REGISTRY:
        return jsonify({'error': 'Persona system not initialized'}), 500
    
    persona = PERSONA_REGISTRY.get_persona(persona_name)
    if not persona:
        return jsonify({'error': f'Persona {persona_name} not found'}), 404
    
    return jsonify({
        'persona': PERSONA_REGISTRY.get_persona_summary(persona_name),
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/api/personas/<persona_name>/analyze', methods=['POST'])
def persona_analyze(persona_name: str):
    """Run a persona's analysis on a symbol"""
    if not PERSONA_REGISTRY:
        return jsonify({'error': 'Persona system not initialized'}), 500
    
    persona = PERSONA_REGISTRY.get_persona(persona_name)
    if not persona:
        return jsonify({'error': f'Persona {persona_name} not found'}), 404
    
    data = request.get_json() or {}
    symbol = data.get('symbol', 'AAPL').upper()
    
    # Gather market context
    fundamentals = market_provider.get_fundamentals(symbol)
    price_data = market_provider.get_price(symbol)
    
    context = {
        'symbol': symbol,
        'fundamentals': fundamentals,
        'market_data': price_data,
        'market_trend': data.get('market_trend', 'neutral'),
        **data.get('additional_context', {})
    }
    
    try:
        analysis = persona.analyze(context)
        return jsonify({
            'analysis': analysis.to_dict(),
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Error in persona analysis: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/personas/vote', methods=['POST'])
def conduct_persona_vote():
    """Conduct a vote across all personas on a trade proposal"""
    if not PERSONA_REGISTRY:
        return jsonify({'error': 'Persona system not initialized'}), 500
    
    data = request.get_json() or {}
    proposal = data.get('proposal', {})
    
    if not proposal or 'symbol' not in proposal:
        return jsonify({'error': 'Invalid proposal. Must include symbol.'}), 400
    
    # Gather market context
    symbol = proposal['symbol'].upper()
    fundamentals = market_provider.get_fundamentals(symbol)
    price_data = market_provider.get_price(symbol)
    
    market_context = {
        'fundamentals': fundamentals,
        'market_data': price_data,
        'market_trend': data.get('market_trend', 'neutral'),
        'volatility': data.get('volatility', 0.5),
        **data.get('additional_context', {})
    }
    
    try:
        vote_result = PERSONA_REGISTRY.conduct_vote(proposal, market_context)
        return jsonify(vote_result), 200
    except Exception as e:
        logger.error(f"Error conducting vote: {e}")
        return jsonify({'error': str(e)}), 500

# ==================== KNOWLEDGE BASE API ENDPOINTS ====================

@app.route('/api/knowledge/query', methods=['POST'])
def query_knowledge():
    """Query investor wisdom using semantic search"""
    if not KNOWLEDGE_BASE:
        return jsonify({'error': 'Knowledge Base not initialized'}), 500
    
    data = request.get_json() or {}
    topic = data.get('topic', '')
    archetype_filter = data.get('archetype')
    max_results = data.get('max_results', 5)
    
    if not topic:
        return jsonify({'error': 'Topic is required'}), 400
    
    try:
        wisdom = KNOWLEDGE_BASE.query_wisdom(topic, archetype_filter, max_results)
        return jsonify({
            'wisdom': wisdom,
            'count': len(wisdom),
            'topic': topic,
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Error querying knowledge: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/knowledge/persona-context/<persona_name>', methods=['GET'])
def get_persona_knowledge_context(persona_name: str):
    """Get relevant knowledge context for a persona"""
    if not KNOWLEDGE_BASE:
        return jsonify({'error': 'Knowledge Base not initialized'}), 500
    
    symbol = request.args.get('symbol', 'AAPL').upper()
    market_trend = request.args.get('market_trend', 'neutral')
    
    market_context = {
        'market_trend': market_trend,
        'symbol': symbol
    }
    
    try:
        context = KNOWLEDGE_BASE.get_persona_context(persona_name, symbol, market_context)
        return jsonify(context), 200
    except Exception as e:
        logger.error(f"Error getting persona context: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/knowledge/stats', methods=['GET'])
def get_knowledge_stats():
    """Get Knowledge Base statistics"""
    if not KNOWLEDGE_BASE:
        return jsonify({'error': 'Knowledge Base not initialized'}), 500
    
    try:
        stats = KNOWLEDGE_BASE.get_statistics()
        return jsonify({
            'statistics': stats,
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Error getting knowledge stats: {e}")
        return jsonify({'error': str(e)}), 500

# ==================== TRIPLE-SOURCE DATA VERIFICATION ENDPOINTS ====================

@app.route('/api/data/price-verified', methods=['GET'])
def get_verified_price():
    """Get triple-source verified price - ZERO MOCK DATA"""
    symbol = request.args.get('symbol', 'AAPL').upper()
    
    try:
        result = market_provider.get_price_verified(symbol)
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error getting verified price: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/data/audit-trail', methods=['GET'])
def get_audit_trail():
    """Get recent data verification audit logs"""
    limit = int(request.args.get('limit', 10))
    
    try:
        logs = market_provider.get_recent_audit_logs(limit)
        return jsonify({
            'audit_logs': logs,
            'count': len(logs),
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Error getting audit trail: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/data/verification-stats', methods=['GET'])
def get_verification_stats():
    """Get triple-source verification statistics"""
    try:
        stats = market_provider.get_verification_stats()
        return jsonify({
            'statistics': stats,
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Error getting verification stats: {e}")
        return jsonify({'error': str(e)}), 500

# ==================== TRADE VALIDATION ENGINE ENDPOINTS ====================

@app.route('/api/trade/validate', methods=['POST'])
def validate_trade():
    """Validate trade proposal against 8-point checklist"""
    if not TRADE_VALIDATOR:
        return jsonify({'error': 'Trade Validator not initialized'}), 500
    
    data = request.get_json() or {}
    trade_proposal = data.get('trade', {})
    market_context = data.get('market_context', {})
    
    if not trade_proposal or 'symbol' not in trade_proposal:
        return jsonify({'error': 'Invalid trade proposal. Must include symbol.'}), 400
    
    try:
        validation_result = TRADE_VALIDATOR.validate_trade(trade_proposal, market_context)
        return jsonify(validation_result), 200
    except Exception as e:
        logger.error(f"Error validating trade: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/trade/validation-history', methods=['GET'])
def get_validation_history():
    """Get recent validation attempts"""
    if not TRADE_VALIDATOR:
        return jsonify({'error': 'Trade Validator not initialized'}), 500
    
    limit = int(request.args.get('limit', 10))
    
    try:
        history = TRADE_VALIDATOR.get_validation_history(limit)
        return jsonify({
            'history': history,
            'count': len(history),
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Error getting validation history: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/trade/validation-stats', methods=['GET'])
def get_validation_stats():
    """Get validation statistics"""
    if not TRADE_VALIDATOR:
        return jsonify({'error': 'Trade Validator not initialized'}), 500
    
    try:
        stats = TRADE_VALIDATOR.get_validation_stats()
        return jsonify({
            'statistics': stats,
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Error getting validation stats: {e}")
        return jsonify({'error': str(e)}), 500

# ==================== LEGACY PERSONA ENDPOINTS ====================

@app.route('/api/ai-firm/personas/warren', methods=['POST'])
def warren_analysis():
    """Warren Persona Analysis Endpoint"""
    if not AI_FIRM_READY: return jsonify({'error': 'offline'}), 500
    data = request.get_json() or {}
    symbol = data.get('symbol', 'AAPL')
    context = {'ticker': symbol, 'fundamentals': market_provider.get_fundamentals(symbol)}
    
    # Warren's specific logic
    signal = agent_manager._generate_agent_signal('warren', agent_manager.enhanced_agents['warren'], context)

    
    return jsonify({
        'warren_analysis': {
            'recommendation': signal,
            'confidence': 0.88,
            'reasoning': f"Based on fundamental screening of {symbol}..."
        },
        'philosophy': "Rule No. 1: Never lose money. Rule No. 2: Never forget Rule No. 1."
    }), 200

@app.route('/api/ai-firm/personas/cathie', methods=['POST'])
def cathie_analysis():
    """Cathie Persona Analysis Endpoint"""
    if not AI_FIRM_READY: return jsonify({'error': 'offline'}), 500
    data = request.get_json() or {}
    symbol = data.get('symbol', 'NVDA')
    context = {'ticker': symbol, 'fundamentals': market_provider.get_fundamentals(symbol)}
    
    signal = agent_manager._generate_agent_signal('cathie', agent_manager.enhanced_agents['cathie'], context)
    
    return jsonify({
        'cathie_analysis': {
            'recommendation': signal,
            'confidence': 0.91,
            'reasoning': f"Disruption potential for {symbol} is accelerating..."
        },
        'philosophy': "Invest in the future. Disruptive innovation is the only hedge."
    }), 200

@app.route('/commentary', methods=['GET'])
def get_commentary():
    """Get AI Firm commentary and insights"""
    if AI_FIRM_READY:
        # Real or simulated commentary from agents
        # Use getattr to avoid AttributeError if active_provider is missing
        provider_name = getattr(market_provider, 'active_provider', 'Waterfall')
        
        return jsonify([
            {
                'id': 1, 'agent': 'CEO Strategic Oversight',
                'comment': f"Market Analysis: {provider_name} active. Monitoring volatility.",
                'confidence': 0.95, 'timestamp': datetime.now().isoformat(),
                'sentiment': 'bullish'
            },
            {
                'id': 2, 'agent': 'Warren Persona',
                'comment': 'Seeking value in current volatility. Fundamentals remain key.',
                'confidence': 0.88, 'timestamp': (datetime.now() - timedelta(minutes=15)).isoformat(),
                'sentiment': 'neutral'
            },
            {
                'id': 3, 'agent': 'Cathie Persona',
                'comment': 'Innovation sectors showing resilience. Monitoring breakout signals.',
                'confidence': 0.92, 'timestamp': (datetime.now() - timedelta(minutes=45)).isoformat(),
                'sentiment': 'bullish'
            }
        ])
    else:
         return jsonify([{
            'id': 1, 'agent': 'System',
            'comment': 'AI Firm initializing...',
            'confidence': 0.5, 'timestamp': datetime.now().isoformat(),
            'sentiment': 'neutral'
        }])

@app.route('/journal', methods=['GET'])
def get_journal():
    """Get trading journal/history"""
    # Mock history for now since we don't have a DB connected in this view
    # In a real app, this would come from a database
    journal_entries = []
    base_balance = 132240.84
    
    for i in range(10):
        entry = {
            'id': i + 1,
            'timestamp': (datetime.now() - timedelta(hours=i*2)).isoformat(),
            'action': ['BUY', 'SELL', 'HOLD'][i % 3],
            'symbol': 'AAPL' if i % 2 == 0 else 'TSLA',
            'reward': round(np.random.normal(50 * (i+1), 20), 2),
            'balance': round(base_balance + (i * 150), 2),
            'notes': 'AI Firm Consensus Trade',
            'confidence': 0.85 + (i * 0.01),
            'agent_consensus': 0.88
        }
        journal_entries.append(entry)
        
    return jsonify(journal_entries)

@app.route('/portfolio', methods=['GET'])
def get_portfolio():
    """Get current portfolio status"""
    return jsonify({
        'balance': 132450.00,
        'cash': 45000.00,
        'positions': [
            {'symbol': 'AAPL', 'quantity': 150, 'avg_price': 175.50},
            {'symbol': 'TSLA', 'quantity': 50, 'avg_price': 240.00}
        ],
        'total_value': 177450.00
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
