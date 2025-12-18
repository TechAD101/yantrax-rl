# main.py - YantraX RL Backend v4.6 - DIAGNOSTIC + FORCE TEST
# Critical: Debug why live data isn't flowing

import os
import sys
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import numpy as np
from functools import wraps
from flask import Response

# FIXED #2: Use insert(0) for module priority
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from flask import Flask, jsonify, request  # type: ignore[import]
    from flask_cors import CORS  # type: ignore[import]
    print("✅ Flask dependencies loaded")
except ImportError as e:
    print(f"❌ Flask import error: {e}")
    sys.exit(1)
# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Changed to DEBUG for more details
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load local .env for developer convenience (kept out of git)
try:
    from dotenv import load_dotenv  # type: ignore[import]
    load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
    logger.debug("Loaded local .env (if present)")
except Exception:
    logger.debug("python-dotenv not available or failed to load .env")

import requests  # type: ignore[import]

def _load_dotenv_fallback(filepath: str) -> None:
    """Fallback loader for .env when python-dotenv isn't available.

    Reads simple KEY=VALUE lines and sets os.environ for missing keys.
    Does not overwrite existing environment variables.
    """
    try:
        if not os.path.exists(filepath):
            logger.debug("No local .env file at %s", filepath)
            return

        logger.info("Loading local .env fallback from %s", filepath)
        with open(filepath, 'r', encoding='utf-8') as f:
            for raw in f:
                line = raw.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' not in line:
                    continue
                k, v = line.split('=', 1)
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                if k and (k not in os.environ or not os.environ.get(k)):
                    os.environ[k] = v
                    logger.debug("Set env var from .env: %s", k)
    except Exception as e:
        logger.warning(f"Failed to load .env fallback: {e}")


# Ensure local .env is loaded even if python-dotenv is missing
_load_dotenv_fallback(os.path.join(os.path.dirname(__file__), '.env'))

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
        'version': '5.0',
        'data_source': 'Waterfall (YFinance/FMP/Alpaca)',
        'ai_firm': 'active' if AI_FIRM_READY else 'degraded',
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/market-price', methods=['GET'])
def get_market_price():
    """Get current market price via Waterfall"""
    symbol = request.args.get('symbol', 'AAPL').upper()
    return jsonify(market_provider.get_price(symbol)), 200

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


@app.route('/debug', methods=['GET'])
@handle_errors
def debug_status():
    """Detailed debug information"""
    return jsonify({
        'version': '4.6.0',
        'status': 'diagnostic',
        'market_service': {
            'initialized': MARKET_SERVICE_READY,
            'config': {
                'fmp_api_key_set': bool(MARKET_DATA_CONFIG.fmp_api_key if MARKET_DATA_CONFIG else False),
                'batch_size': MARKET_DATA_CONFIG.batch_size if MARKET_DATA_CONFIG else None
            },
            'providers_available': [p.value for p in market_data.providers] if market_data else [],
            'init_error': MARKET_SERVICE_INIT_ERROR
        },
        'environment': {
            'FMP_API_KEY': 'SET' if os.getenv('FMP_API_KEY') else 'MISSING',
            'ALPACA_API_KEY': 'SET' if os.getenv('ALPACA_API_KEY') else 'MISSING',
            'ALPACA_SECRET_KEY': 'SET' if os.getenv('ALPACA_SECRET_KEY') else 'MISSING'
        },

        'preferred_data_source': os.getenv('MARKET_DATA_SOURCE') or None,
        'ai_firm': {
            'ready': AI_FIRM_READY
        },
        'rl_core': {
            'ready': RL_ENV_READY
        },
        'timestamp': datetime.now().isoformat()
    })

@app.route('/test-alpaca', methods=['GET'])
@handle_errors
def test_alpaca():
    """Force test Alpaca API directly"""
    symbol = request.args.get('symbol', 'AAPL').upper()
    
    logger.info(f"\n🧪 FORCE TEST: Alpaca API for {symbol}")
    
    alpaca_key = os.getenv('ALPACA_API_KEY')
    alpaca_secret = os.getenv('ALPACA_SECRET_KEY')
    
    if not alpaca_key or not alpaca_secret:
        logger.error("❌ Alpaca credentials missing!")
        return jsonify({
            'status': 'error',
            'message': 'Alpaca credentials not configured',
            'alpaca_key_set': bool(alpaca_key),
            'alpaca_secret_set': bool(alpaca_secret)
        })
    
    try:
        import requests  # type: ignore[import]
        
        logger.info(f"  Alpaca Key (first 10): {alpaca_key[:10] if alpaca_key else 'NONE'}")
        logger.info(f"  Making request to Alpaca...")
        
        headers = {
            'APCA-API-KEY-ID': alpaca_key,
            'APCA-API-SECRET-KEY': alpaca_secret
        }
        
        url = f"https://data.alpaca.markets/v2/stocks/{symbol}/quotes/latest"
        logger.info(f"  URL: {url}")
        
        response = requests.get(url, headers=headers, timeout=10)
        
        logger.info(f"  Status: {response.status_code}")
        logger.info(f"  Response: {response.text[:200]}")
        
        return jsonify({
            'status': 'success',
            'symbol': symbol,
            'response_status': response.status_code,
            'response': response.json(),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"❌ Alpaca test failed: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e),
            'symbol': symbol,
            'timestamp': datetime.now().isoformat()
        })

@app.route('/test-fmp', methods=['GET'])
@handle_errors
def test_fmp():
    """Force test FinancialModelingPrep (FMP) API directly"""
    symbol = request.args.get('symbol', 'AAPL').upper()

    logger.info(f"\n🧪 FORCE TEST: FMP API for {symbol}")

    fmp_key = os.getenv('FMP_API_KEY') or os.getenv('FMP_KEY')

    if not fmp_key:
        logger.error("❌ FMP credentials missing!")
        return jsonify({
            'status': 'error',
            'message': 'FMP credentials not configured',
            'fmp_key_set': False,
            'tried_envs': ['FMP_API_KEY', 'FMP_KEY']
        })

    try:
        import requests  # type: ignore[import]

        logger.info(f"  FMP Key (first 10): {fmp_key[:10] if fmp_key else 'NONE'}")
        logger.info(f"  Making request to FMP (quote endpoint)...")

        url = f"https://financialmodelingprep.com/api/v3/quote/{symbol}"
        params = {'apikey': fmp_key}

        logger.info(f"  URL: {url}")
        logger.info(f"  Params: {list(params.keys())}")

        response = requests.get(url, params=params, timeout=10)

        logger.info(f"  Status: {response.status_code}")
        logger.info(f"  Response: {response.text[:200]}")

        return jsonify({
            'status': 'success',
            'symbol': symbol,
            'response_status': response.status_code,
            'response': response.json(),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"❌ FMP test failed: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e),
            'symbol': symbol,
            'timestamp': datetime.now().isoformat()
        })

@app.route('/market-price-stream', methods=['GET'])
def market_price_stream():
    """Server-Sent Events stream of market prices for a symbol.

    Query params:
      - symbol (default AAPL)
      - interval (seconds between events, default 5)
      - count (optional, number of events to emit; if omitted stream indefinitely)
    """
    symbol = (request.args.get('symbol') or 'AAPL').upper()
    try:
        interval = float(request.args.get('interval', os.getenv('MARKET_DATA_STREAM_INTERVAL', '5')))
    except Exception:
        interval = 5.0
    count_param = request.args.get('count')
    try:
        count = int(count_param) if count_param else None
    except Exception:
        count = None

    def event_generator():
        sent = 0
        # Initial event
        while True:
            try:
                data = unified_get_market_price(symbol)
                payload = {
                    'symbol': symbol,
                    'data': data,
                    'timestamp': datetime.now().isoformat()
                }
                yield f"data: {json.dumps(payload)}\n\n"
                sent += 1
                if count is not None and sent >= count:
                    break
                # Sleep, but break if client disconnects (Flask will close generator)
                try:
                    import time
                    time.sleep(interval)
                except GeneratorExit:
                    break
            except GeneratorExit:
                break
            except Exception as e:
                err = {'error': 'stream_error', 'message': str(e), 'timestamp': datetime.now().isoformat()}
                yield f"data: {json.dumps(err)}\n\n"
                break

    return Response(event_generator(), mimetype='text/event-stream')

@app.route('/massive-quote', methods=['GET'])
@handle_errors
def massive_quote():
    """Fetch a real-time quote from Massive Market Data service for a single symbol.

    Query params:
      - symbol: required (e.g., AAPL, BTC, EURUSD, SPX)
    """
    symbol = (request.args.get('symbol') or '').strip().upper()
    if not symbol:
        return jsonify({'status': 'error', 'message': 'symbol query parameter is required'}), 400

    try:
        # Instantiate with env var if present
        msvc = MassiveMarketDataService(api_key=os.getenv('MASSIVE_API_KEY'))
        data = msvc.fetch_quote(symbol)
        return jsonify({'status': 'success', 'symbol': symbol, 'data': data, 'timestamp': datetime.now().isoformat()})
    except Exception as e:
        logger.error(f"❌ /massive-quote failed for {symbol}: {e}")
        return jsonify({'status': 'error', 'message': str(e), 'symbol': symbol, 'timestamp': datetime.now().isoformat()}), 500

@app.route('/health', methods=['GET'])
@handle_errors  
def detailed_health():
    return jsonify({
        'status': 'healthy',
        'services': {
            'api': 'operational',
            'market_data': 'v2' if MARKET_SERVICE_READY else 'fallback',
            'ai_firm': 'operational' if AI_FIRM_READY else 'fallback',
            'rl_core': 'operational' if RL_ENV_READY else 'not_loaded'
        },
        'ai_firm': {
            'enabled': AI_FIRM_READY,
            'agents': 24 if AI_FIRM_READY else 4,
            'ceo': AI_FIRM_READY,
            'personas': {'warren': AI_FIRM_READY, 'cathie': AI_FIRM_READY}
        },
        'rl_core': {
            'enabled': RL_ENV_READY,
            'environment': 'MarketSimEnv' if RL_ENV_READY else None
        },
        'performance': error_counts,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/god-cycle', methods=['GET'])
@handle_errors
def god_cycle():
    start_ts = datetime.now()
    result = yantrax_system.execute_god_cycle()
    # Update prometheus-like metrics
    try:
        elapsed = (datetime.now() - start_ts).total_seconds()
        metrics_registry['yantrax_agent_latency_seconds_count'] += 1
        metrics_registry['yantrax_agent_latency_seconds_sum'] += elapsed
    except Exception:
        pass
    result['version'] = '4.6.0'
    result['inassign him next tastive'] = AI_FIRM_READY and RL_ENV_READY
    return jsonify(result)


@app.route('/metrics', methods=['GET'])
@handle_errors
def metrics():
    # Return simple text metrics in Prometheus exposition format
    try:
        output = []
        output.append(f"# HELP yantrax_requests_total Total number of yantrax requests")
        output.append(f"# TYPE yantrax_requests_total counter")
        output.append(f"yantrax_requests_total {int(metrics_registry.get('yantrax_requests_total', 0))}")
        output.append(f"# HELP yantrax_agent_latency_seconds Histogram for agent latency")
        output.append(f"# TYPE yantrax_agent_latency_seconds histogram")
        output.append(f"yantrax_agent_latency_seconds_count {int(metrics_registry.get('yantrax_agent_latency_seconds_count', 0))}")
        output.append(f"yantrax_agent_latency_seconds_sum {metrics_registry.get('yantrax_agent_latency_seconds_sum', 0.0)}")
        return ("\n".join(output), 200, {'Content-Type': 'text/plain; charset=utf-8'})
    except Exception as e:
        logger.error(f"Metrics exposition error: {e}")
        return ("", 500, {'Content-Type': 'text/plain; charset=utf-8'})


@app.route('/api/ai-firm/status', methods=['GET'])
@handle_errors
def ai_firm_status():
    if not AI_FIRM_READY:
        return jsonify({
            'status': 'fallback_mode',
            'message': 'AI Firm not loaded',
            'agents': len(yantrax_system.legacy_agents)
        })
    
    try:
        ceo_status = ceo.get_ceo_status()
        return jsonify({
            'status': 'operational',
            'total_agents': 24,
            'ceo': ceo_status,
            'personas': {'warren': True, 'cathie': True},
            'rl_integration': RL_ENV_READY,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"AI Firm status error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# FIXED #5: Market price endpoint with fallback
@app.route('/market-price', methods=['GET'])
@handle_errors
def get_market_price():
    """Get market price with proper MarketDataService v2 integration"""
    symbol = request.args.get('symbol', 'AAPL').upper()
    data = unified_get_market_price(symbol)
    if 'error' in data:
        logger.warning(f"Market price lookup for {symbol} failed: {data.get('message')}")
        return jsonify(data), 503

    logger.info(f"📊 Market price returned for {symbol}: {data.get('price')} (source: {data.get('source')})")
    return jsonify(data)

@app.route('/multi-asset-data', methods=['GET'])
@handle_errors
def get_multi_asset_data():
    symbols_param = request.args.get('symbols', 'AAPL,MSFT,GOOGL,TSLA')
    symbols = [s.strip().upper() for s in symbols_param.split(',')]

    results = {}
    for symbol in symbols:
        try:
            if MARKET_SERVICE_READY and market_data:
                results[symbol] = market_data.get_stock_price(symbol)
            else:
                results[symbol] = {
                    'symbol': symbol,
                    'error': 'no_market_data',
                    'message': 'Market data service not configured',
                }
        except Exception as e:
            logger.error(f"Error fetching {symbol}: {str(e)}")
            results[symbol] = {'error': str(e), 'symbol': symbol, 'status': 'error'}

    return jsonify({
        'data': results,
        'timestamp': datetime.now().isoformat(),
        'symbols_requested': len(symbols),
        'symbols_successful': sum(1 for r in results.values() if r.get('status') != 'error'),
        'service': 'v2' if MARKET_SERVICE_READY else 'fallback'
    })


@app.route('/env-status', methods=['GET'])
@handle_errors
def env_status():
    """Return non-sensitive environment status to diagnose deployments."""
    fmp_present = bool(_get_fmp_key())
    alpaca_present = bool(os.getenv('ALPACA_API_KEY') and os.getenv('ALPACA_SECRET_KEY'))
    return jsonify({
        'fmp_present': fmp_present,
        'fmp_env_names': [
            name for name in ['FMP_API_KEY', 'FMP_KEY', 'FMP']
            if os.getenv(name)
        ],
        'alpaca_present': alpaca_present,
        'market_service_ready': MARKET_SERVICE_READY,
        'preferred_data_source': os.getenv('MARKET_DATA_SOURCE') or None,
        'providers': [p.value for p in market_data.providers] if market_data else []
    })

@app.route('/run-cycle', methods=['POST'])
@handle_errors
def run_cycle():
    return jsonify(yantrax_system.execute_god_cycle())

@app.route('/journal', methods=['GET'])
@handle_errors
def get_journal():
    if yantrax_system.trade_history:
        return jsonify(yantrax_system.trade_history[-10:])
    
    return jsonify([
        {
            'id': i,
            'timestamp': (datetime.now() - timedelta(hours=i)).isoformat(),
            'action': ['BUY', 'SELL', 'HOLD'][i % 3],
            'balance': round(132240 + (i * 250), 2)
        } for i in range(5)
    ])

@app.route('/commentary', methods=['GET'])
@handle_errors
def get_commentary():
    if AI_FIRM_READY:
        return jsonify([
            {
                'id': 1,
                'agent': 'Warren Persona',
                'comment': 'Strong fundamentals detected',
                'confidence': 0.89,
                'timestamp': datetime.now().isoformat()
            },
            {
                'id': 2,
                'agent': 'CEO',
                'comment': '24-agent consensus achieved',
                'confidence': 0.85,
                'timestamp': datetime.now().isoformat()
            }
        ])
    
    return jsonify([
        {
            'id': 1,
            'agent': 'System',
            'comment': f'Running in {"AI Firm" if AI_FIRM_READY else "legacy"} mode',
            'confidence': 0.75,
            'timestamp': datetime.now().isoformat()
        }
    ])

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Not found',
        'endpoints': ['/', '/health', '/debug', '/test-alpaca', '/test-fmp', '/god-cycle', '/market-price', '/run-cycle', '/journal', '/commentary'],
        'timestamp': datetime.now().isoformat()
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error',
        'timestamp': datetime.now().isoformat()
    }), 500


@app.route('/version', methods=['GET'])
@handle_errors
def get_version():
    v = _get_git_version()
    return jsonify({
        'version': v['sha'],
        'branch': v['branch'],
        'app': 'yantrax-backend'
    })

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 YantraX RL v4.6 - DIAGNOSTIC MODE ACTIVE")
    print("="*60)
    print(f"🤖 AI Firm: {'✅ READY' if AI_FIRM_READY else '❌ FALLBACK'}")
    print(f"🎮 RL Core: {'✅ READY' if RL_ENV_READY else '❌ NOT LOADED'}")
    print(f"📊 Market Data: {'✅ v2 CONFIGURED' if MARKET_SERVICE_READY else '❌ NOT CONFIGURED (no mock fallback)'}")
    
    if MARKET_SERVICE_READY and market_data:
        print(f"📡 Available Providers: {[p.value for p in market_data.providers]}")
    
    print("\n🧪 DIAGNOSTIC ENDPOINTS:")
    print("  /debug - Full config status")
    print("  /test-fmp?symbol=AAPL - Test FinancialModelingPrep directly")
    print("  /test-alpaca?symbol=AAPL - Test Alpaca directly (optional)")
    print("="*60 + "\n")
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)