
import os
import logging
import json
import numpy as np
import time
from datetime import datetime
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
try:
    from ai_firm.ceo import AutonomousCEO, CEOPersonality
    from ai_agents.personas.warren import WarrenAgent
    from ai_agents.personas.cathie import CathieAgent
    from ai_firm.agent_manager import AgentManager
    from rl_core.env_market_sim import MarketSimEnv
    
    # Initialize Core Agents
    ceo = AutonomousCEO(personality=CEOPersonality.BALANCED)
    warren = WarrenAgent()
    cathie = CathieAgent()
    agent_manager = AgentManager()
    
    # Initialize RL Environment
    rl_env = MarketSimEnv()
    
    AI_FIRM_READY = True
    logger.info("✅ AI FIRM & RL CORE FULLY OPERATIONAL")
except Exception as e:
    logger.error(f"❌ AI Firm initialization failed: {e}")
    # We continue, but god_cycle will degrade gracefully

app = Flask(__name__)
CORS(app, origins=['*'])

@app.route('/', methods=['GET'])
def health_check():
    """Health check - system status"""
    return jsonify({
        'status': 'operational',
        'version': '5.2-forced-update',
        'data_source': 'Waterfall (YFinance/FMP/Alpaca)',
        'ai_firm': 'active' if AI_FIRM_READY else 'degraded',
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/market-price', methods=['GET'])
def get_market_price():
    """Get current market price via Waterfall"""
    symbol = request.args.get('symbol', 'AAPL').upper()
    return jsonify(market_provider.get_price(symbol)), 200

def generate_market_stream(symbol: str, interval: float = 5.0):
    """Generator for Server-Sent Events"""
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
            
            time.sleep(interval)
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
    """Execute 24-agent voting cycle with REAL DATA"""
    symbol = request.args.get('symbol', 'AAPL').upper()
    
    # 1. Fetch Real Data (The "Hard" Part)
    price_data = market_provider.get_price(symbol)
    fundamentals = market_provider.get_fundamentals(symbol)
    
    current_price = price_data.get('price', 0)
    
    # 2. Prepare Context for Agents
    context = {
        'symbol': symbol,
        'decision_type': 'trading',
        'market_data': {'current_price': current_price},
        'fundamentals': fundamentals,
        'market_trend': 'bullish' if fundamentals.get('return_on_equity', 0) > 0.1 else 'bearish', # Simplified trend
        'timestamp': datetime.now().isoformat()
    }
    
    expert_opinions = {}
    
    if AI_FIRM_READY:
        # 3. Consult Expert Agents (Deep Analysis)
        # Warren Analysis
        try:
            warren_analysis = warren.analyze_investment(context)
            expert_opinions['warren'] = warren_analysis['recommendation']
        except Exception as e:
            logger.error(f"Warren failed: {e}")
            
        # 4. Conduct General Voting (Broad Consensus)
        voting_result = agent_manager.conduct_agent_voting(context, expert_opinions=expert_opinions)
        
        # 5. CEO Decision
        ceo_context = {
            'type': 'strategic_trading_decision',
            'agent_recommendation': voting_result['winning_signal'],
            'consensus_strength': voting_result['consensus_strength'],
            'fundamentals': fundamentals
        }
        ceo_decision = ceo.make_strategic_decision(ceo_context)
        
        # 6. RL Verification (Simulation)
        # We step the RL env just to keep it alive/training, but don't let it override CEO yet
        try:
            rl_env.step("hold") 
        except:
            pass
            
        return jsonify({
            'status': 'success',
            'symbol': symbol,
            'signal': voting_result['winning_signal'],
            'expert_opinions': expert_opinions,
            'market_data': price_data,
            'fundamentals': fundamentals,
            'vote_summary': voting_result['vote_distribution'],
            'consensus': voting_result['consensus_strength'],
            'ceo_decision': {
                'confidence': ceo_decision.confidence,
                'reasoning': ceo_decision.reasoning
            },
            'timestamp': datetime.now().isoformat()
        }), 200
        
    else:
        return jsonify({'error': 'AI Firm not initialized'}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)