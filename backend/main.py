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

# ==================== CRITICAL DIAGNOSTIC ====================

logger.info("\n" + "="*80)
logger.info("🔍 YANTRAX RL v4.6 - DIAGNOSTIC MODE")
logger.info("="*80)

# Log all environment variables
logger.info("📋 ENVIRONMENT VARIABLES CHECK:")

def _get_fmp_key() -> str:
    """Return the FinancialModelingPrep key from commonly used env var names."""
    return (
        os.getenv('FMP_API_KEY') or
        os.getenv('FMP_KEY') or
        os.getenv('FMP') or
        ''
    )

fmp_key_env = _get_fmp_key()
alpaca_key_env = os.getenv('ALPACA_API_KEY', '')
alpaca_secret_env = os.getenv('ALPACA_SECRET_KEY', '')

logger.info(f"  FMP_API_KEY present: {bool(fmp_key_env)} (first 10 chars: {fmp_key_env[:10] if fmp_key_env else 'EMPTY'})")
logger.info(f"  ALPACA_API_KEY present: {bool(alpaca_key_env)} (first 10 chars: {alpaca_key_env[:10] if alpaca_key_env else 'EMPTY'})")
logger.info(f"  ALPACA_SECRET_KEY present: {bool(alpaca_secret_env)} (first 10 chars: {alpaca_secret_env[:10] if alpaca_secret_env else 'EMPTY'})")

# FIXED: Properly import and instantiate MarketDataService v2
MARKET_SERVICE_READY = False
market_data = None
MARKET_DATA_CONFIG = None
MARKET_SERVICE_INIT_ERROR = None

try:
    from services.market_data_service_v2 import MarketDataService, MarketDataConfig
    # Massive market data client (supports equities, crypto, indices, forex)
    from services.market_data_service_massive import MassiveMarketDataService
    
    logger.info("✅ MarketDataService v2 imported successfully")
    
    # Get API keys from environment (accept many common names)
    fmp_key_env = _get_fmp_key()
    alpaca_key = os.getenv('ALPACA_API_KEY', '')
    alpaca_secret = os.getenv('ALPACA_SECRET_KEY', '')

    logger.info(f"\n🔑 API KEYS CHECK:")
    logger.info(f"  FMP: {'✅ SET' if fmp_key_env else '❌ MISSING'}")
    logger.info(f"  Alpaca API Key: {'✅ SET' if alpaca_key else '❌ MISSING'}")
    logger.info(f"  Alpaca Secret: {'✅ SET' if alpaca_secret else '❌ MISSING'}")
    
    # Use FinancialModelingPrep (FMP) as the single, authoritative provider
    fmp_key = os.getenv('FMP_API_KEY') or os.getenv('FMP_KEY') or os.getenv('FMP') or '14uTc09TMyUVJEuFKriHayCTnLcyGhyy'

    if fmp_key:
        logger.info("\n🔨 CREATING MarketDataConfig (FMP-only)...")

        config = MarketDataConfig(
            fmp_api_key=fmp_key,
            cache_ttl_seconds=5,
            rate_limit_calls=300,
            rate_limit_period=60,
            batch_size=50
        )

        logger.info(f"  Config created:")
        logger.info(f"    - fmp_api_key: {'✅ SET' if config.fmp_api_key else '❌ MISSING'}")
        logger.info(f"    - cache_ttl_seconds: {config.cache_ttl_seconds}")
        MARKET_DATA_CONFIG = config

        logger.info("\n🚀 INITIALIZING MarketDataService (FMP-only)...")
        market_data = MarketDataService(config)

        MARKET_SERVICE_READY = True
        logger.info(f"✅ MarketDataService initialized successfully")
        logger.info(f"📊 Available providers: {[p.value for p in market_data.providers]}")
        logger.info("📡 Data Pipeline: FinancialModelingPrep (FMP) - batch quote API")
    else:
        logger.error("❌ NO FMP API KEY FOUND! Set FMP_API_KEY in environment or pass via MarketDataConfig.")
        MARKET_SERVICE_READY = False

except ImportError as e:
    logger.error(f"❌ MarketDataService v2 import failed: {e}")
    logger.error(f"   Import error details: {str(e)}")
    MARKET_SERVICE_INIT_ERROR = str(e)
    MARKET_SERVICE_READY = False
except Exception as e:
    logger.error(f"❌ MarketDataService v2 initialization failed: {e}")
    logger.error(f"   Traceback: {str(e)}")
    MARKET_SERVICE_INIT_ERROR = str(e)
    MARKET_SERVICE_READY = False

logger.info("="*80 + "\n")

# AI Firm imports with enhanced error handling
AI_FIRM_READY = False
try:
    from ai_firm.ceo import AutonomousCEO, CEOPersonality
    from ai_agents.personas.warren import WarrenAgent
    from ai_agents.personas.cathie import CathieAgent
    from ai_firm.agent_manager import AgentManager
    AI_FIRM_READY = True
    logger.info("🏢 AI FIRM ARCHITECTURE LOADED SUCCESSFULLY!")
    logger.info("🚀 20+ AGENT COORDINATION SYSTEM ACTIVE")
except ImportError as e:
    logger.warning(f"⚠️ AI Firm primary import failed: {e}")
    logger.info("🔍 Attempting alternate import paths...")
    try:
        import ai_firm.ceo as ceo_module
        import ai_agents.personas.warren as warren_module 
        import ai_agents.personas.cathie as cathie_module
        import ai_firm.agent_manager as agent_manager_module
        
        AutonomousCEO = ceo_module.AutonomousCEO
        CEOPersonality = ceo_module.CEOPersonality
        WarrenAgent = warren_module.WarrenAgent
        CathieAgent = cathie_module.CathieAgent
        AgentManager = agent_manager_module.AgentManager
        
        AI_FIRM_READY = True
        logger.info("🔧 AI FIRM loaded via alternate path - SUCCESS!")
    except ImportError as e2:
        logger.error(f"❌ AI Firm fallback also failed: {e2}")
        logger.info("📋 Running in legacy 4-agent mode")
        AI_FIRM_READY = False

# RL Core imports
RL_ENV_READY = False
try:
    from rl_core.env_market_sim import MarketSimEnv
    RL_ENV_READY = True
    logger.info("🎮 RL CORE: MarketSimEnv loaded successfully!")
except ImportError as e:
    logger.warning(f"⚠️ RL Core not available: {e}")
    RL_ENV_READY = False

app = Flask(__name__)
CORS(app, origins=['*'])


def _get_git_version() -> Dict[str, str]:
    """Return git short sha and branch if available."""
    try:
        import subprocess
        sha = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'], text=True).strip()
        branch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], text=True).strip()
        return {'sha': sha, 'branch': branch}
    except Exception:
        return {'sha': 'unknown', 'branch': 'unknown'}

# Error tracking
error_counts = {
    'total_requests': 0,
    'successful_requests': 0, 
    'api_call_errors': 0
}

# Simple Prometheus-like metrics registry (lightweight)
metrics_registry = {
    'yantrax_requests_total': 0,
    'yantrax_agent_latency_seconds_count': 0,
    'yantrax_agent_latency_seconds_sum': 0.0
}

def handle_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        error_counts['total_requests'] += 1
        try:
            metrics_registry['yantrax_requests_total'] += 1
        except Exception:
            pass
        try:
            result = func(*args, **kwargs)
            error_counts['successful_requests'] += 1
            return result
        except Exception as e:
            error_counts['api_call_errors'] += 1
            logger.exception("API error occurred")
            return jsonify({
                'error': 'internal_server_error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            }), 500
    return wrapper

# Initialize AI Firm components
if AI_FIRM_READY:
    try:
        ceo = AutonomousCEO(personality=CEOPersonality.BALANCED)
        warren = WarrenAgent()
        cathie = CathieAgent()
        agent_manager = AgentManager()
        logger.info("🏢 AI FIRM FULLY OPERATIONAL!")
        logger.info(f"🤖 CEO ACTIVE: {ceo.personality.value}")
        logger.info("📊 WARREN & CATHIE PERSONAS LOADED")
        logger.info("🔄 20+ AGENT COORDINATION READY")
    except Exception as e:
        logger.error(f"⚠️ AI Firm initialization error: {e}")
        AI_FIRM_READY = False
        logger.info("🔄 Falling back to legacy mode")

# FIXED #3: Market Data Service initialization with safety check
market_data = None
if MARKET_SERVICE_READY:
    try:
        # Build config from environment variables (alpha vantage key, etc.)
        try:
            from services.market_data_service_v2 import MarketDataConfig
            # Use the robust key detection to pick the alpha key and include alpaca creds
            av_key = _get_alpha_vantage_key() or os.getenv('ALPHA_VANTAGE') or ''
            alpaca_key_env = os.getenv('ALPACA_API_KEY') or os.getenv('ALPACA_KEY')
            alpaca_secret_env = os.getenv('ALPACA_SECRET_KEY') or os.getenv('ALPACA_SECRET')
            polygon = os.getenv('POLYGON_KEY') or os.getenv('POLYGON') or None
            finnhub = os.getenv('FINNHUB_KEY') or os.getenv('FINNHUB') or None
            cfg = MarketDataConfig(
                alpha_vantage_key=av_key,
                alpaca_key=alpaca_key_env,
                alpaca_secret=alpaca_secret_env,
                polygon_key=polygon,
                finnhub_key=finnhub,
                fallback_to_mock=False
            )
            market_data = MarketDataService(cfg)
            logger.info("✅ MarketDataService v2 initialized with config from env")
            logger.info("📊 Providers in use: %s", [p.value for p in market_data.providers])
        except Exception as e_cfg:
            logger.error(f"⚠️  Failed to initialize MarketDataService with config: {e_cfg}")
            MARKET_SERVICE_INIT_ERROR = str(e_cfg)
            market_data = None
    except Exception as e:
        logger.error(f"⚠️  MarketDataService v2 init failed: {e}")
        MARKET_SERVICE_INIT_ERROR = str(e)
        MARKET_SERVICE_READY = False
        market_data = None
else:
    logger.info("📊 Using fallback market data (MarketDataService v2 not available)")


def unified_get_market_price(symbol: str) -> Dict[str, Any]:
    """Get current market price for a symbol using configured provider (FMP-first).

    If FMP fails or returns no usable price, attempt Massive (polygon) as a fallback
    if `MASSIVE_API_KEY` is configured.
    """
    symbol = symbol.upper()

    # 1) Attempt primary FMP provider (via MarketDataService)
    if MARKET_SERVICE_READY and market_data:
        try:
            res = market_data.get_stock_price(symbol)
            if res and res.get('price') and res.get('price') > 0:
                return res
            logger.warning(f"FMP returned no usable price for {symbol}: {res}")
        except Exception as e:
            logger.error(f"MarketDataService lookup failed for {symbol}: {e}")

    # 2) Fallback: Massive / Polygon if configured
    massive_key = os.getenv('MASSIVE_API_KEY') or os.getenv('POLYGON_API_KEY') or os.getenv('POLYGON_KEY')
    if massive_key:
        try:
            msvc = MassiveMarketDataService(api_key=massive_key, base_url=os.getenv('MASSIVE_BASE_URL'))
            data = msvc.fetch_quote(symbol)
            if data and data.get('price'):
                logger.info(f"✅ MASSIVE provider success for {symbol}: {data.get('price')}")
                return data
            else:
                logger.warning(f"MASSIVE returned no usable price for {symbol}: {data}")
        except Exception as e:
            logger.error(f"MASSIVE provider lookup failed for {symbol}: {e}")

    # 3) No providers available or call failed
    return {
        'error': 'no_market_data',
        'message': 'No market data providers available or all providers failed',
        'symbol': symbol,
        'timestamp': datetime.now().isoformat()
    }
class YantraXEnhancedSystem:
    """Enhanced trading system with AI Firm + RL Core integration"""
    
    def __init__(self):
        from typing import Any, Optional

        self.portfolio_balance = 132240.84
        self.trade_history = []
        # `env` may be unavailable in some deployments; annotate to quiet static checks
        self.env: Optional[Any] = None
        self.current_state: Optional[Dict[str, Any]] = None
        
        # Initialize RL environment if available
        if RL_ENV_READY:
            try:
                self.env = MarketSimEnv()
                self.current_state = self.env.reset()
                logger.info("✅ RL Environment initialized successfully")
            except Exception as e:
                logger.error(f"RL env init error: {e}")
                self.env = None
                self.current_state = None
        else:
            self.env = None
            self.current_state = None
        
        # Legacy 4-agent compatibility layer
        self.legacy_agents = {
            'macro_monk': {'confidence': 0.829, 'performance': 15.2, 'strategy': 'TREND_FOLLOWING'},
            'the_ghost': {'confidence': 0.858, 'performance': 18.7, 'signal': 'CONFIDENT_BUY'},
            'data_whisperer': {'confidence': 0.990, 'performance': 12.9, 'analysis': 'BULLISH_BREAKOUT'},
            'degen_auditor': {'confidence': 0.904, 'performance': 22.1, 'audit': 'LOW_RISK_APPROVED'}
        }
    
    def _map_signal_to_action(self, signal: str) -> str:
        """Map trading signal to RL action"""
        signal_upper = signal.upper()
        if "BUY" in signal_upper:
            return "buy"
        elif "SELL" in signal_upper:
            return "sell"
        else:
            return "hold"
    
    def execute_god_cycle(self) -> Dict[str, Any]:
        """Execute god cycle with appropriate integration level"""
        if AI_FIRM_READY and RL_ENV_READY:
            return self._execute_integrated_cycle()
        elif AI_FIRM_READY:
            return self._execute_ai_firm_cycle()
        else:
            return self._execute_legacy_cycle()
    
    def _execute_integrated_cycle(self) -> Dict[str, Any]:
        """Fully integrated: AI Firm → RL Environment"""
        try:
            # Guard: ensure RL env and current state present
            if not self.env or not self.current_state:
                logger.warning("RL environment not ready; falling back to AI Firm cycle")
                return self._execute_ai_firm_cycle()
            # For static analyzers, make explicit we're not None beyond this point
            assert self.current_state is not None
            context = {
                'decision_type': 'trading',
                'market_price': self.current_state['price'],
                'market_volatility': self.current_state['volatility'],
                'market_mood': self.current_state['mood'],
                'balance': self.current_state['balance'],
                'position': self.current_state['position'],
                'cycle': self.current_state['cycle'],
                'timestamp': datetime.now().isoformat()
            }
            
            voting_result = agent_manager.conduct_agent_voting(context)
            ceo_context = {
                'type': 'strategic_trading_decision',
                'agent_recommendation': voting_result['winning_signal'],
                'consensus_strength': voting_result['consensus_strength'],
                'market_state': self.current_state,
                'agent_participation': voting_result['participating_agents']
            }
            ceo_decision = ceo.make_strategic_decision(ceo_context)
            
            final_signal = voting_result['winning_signal']
            rl_action = self._map_signal_to_action(final_signal)
            next_state, reward, done = self.env.step(rl_action)
            
            self.current_state = next_state
            self.portfolio_balance = next_state['balance']
            
            self.trade_history.append({
                'cycle': next_state['cycle'],
                'action': rl_action,
                'signal': final_signal,
                'price': next_state['price'],
                'reward': reward,
                'balance': next_state['balance'],
                'timestamp': datetime.now().isoformat()
            })
            
            if done:
                logger.info(f"Episode complete at cycle {next_state['cycle']}")
                self.current_state = self.env.reset()
            
            return {
                'status': 'success',
                'signal': final_signal,
                'action': rl_action,
                'market_state': {
                    'price': next_state['price'],
                    'volatility': next_state['volatility'],
                    'mood': next_state['mood'],
                    'balance': next_state['balance'],
                    'position': next_state['position'],
                    'cycle': next_state['cycle']
                },
                'ai_firm_coordination': {
                    'mode': 'fully_integrated',
                    'total_agents': voting_result['participating_agents'],
                    'consensus_strength': voting_result['consensus_strength'],
                    'ceo_confidence': ceo_decision.confidence,
                    'ceo_reasoning': ceo_decision.reasoning
                },
                'rl_metrics': {
                    'reward': round(reward, 2),
                    'cycle': next_state['cycle'],
                    'done': done
                },
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Integrated cycle error: {e}")
            return self._execute_legacy_cycle()
    
    def _execute_ai_firm_cycle(self) -> Dict[str, Any]:
        """AI Firm coordination without RL environment"""
        try:
            context = {
                'decision_type': 'trading',
                'market_volatility': np.random.uniform(0.1, 0.3),
                'timestamp': datetime.now().isoformat()
            }
            
            voting_result = agent_manager.conduct_agent_voting(context)
            
            ceo_context = {
                'type': 'strategic_trading_decision',
                'agent_recommendation': voting_result['winning_signal'],
                'consensus_strength': voting_result['consensus_strength'],
                'agent_participation': voting_result['participating_agents']
            }
            ceo_decision = ceo.make_strategic_decision(ceo_context)
            
            reward = np.random.normal(950, 300)
            self.portfolio_balance += reward
            
            return {
                'status': 'success',
                'signal': voting_result['winning_signal'],
                'strategy': 'AI_FIRM_24_AGENTS',
                'final_balance': round(self.portfolio_balance, 2),
                'total_reward': round(reward, 2),
                'ai_firm_coordination': {
                    'mode': 'ai_firm_only',
                    'total_agents': voting_result['participating_agents'],
                    'consensus_strength': voting_result['consensus_strength'],
                    'ceo_confidence': ceo_decision.confidence
                },
                'agents': self._get_agent_status(),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"AI Firm cycle error: {e}")
            return self._execute_legacy_cycle()
    
    def _execute_legacy_cycle(self) -> Dict[str, Any]:
        """Legacy 4-agent fallback"""
        for state in self.legacy_agents.values():
            variation = np.random.normal(0, 0.05)
            state['confidence'] = np.clip(state['confidence'] + variation, 0.1, 0.99)
        
        signal = np.random.choice(['BUY', 'SELL', 'HOLD'], p=[0.4, 0.2, 0.4])
        reward = np.random.normal(500, 200)
        self.portfolio_balance += reward
        
        return {
            'status': 'success',
            'signal': signal,
            'strategy': 'LEGACY_4_AGENTS',
            'final_balance': round(self.portfolio_balance, 2),
            'total_reward': round(reward, 2),
            'agents': {
                name: {
                    'confidence': round(state['confidence'], 3),
                    'performance': state['performance']
                }
                for name, state in self.legacy_agents.items()
            },
            'timestamp': datetime.now().isoformat(),
            'note': 'Legacy mode - AI Firm & RL not loaded'
        }
    
    def _get_agent_status(self) -> Dict[str, Any]:
        """Get agent status with defensive handling"""
        if not AI_FIRM_READY:
            return {
                name: {
                    'confidence': round(state['confidence'], 3),
                    'performance': state['performance']
                }
                for name, state in self.legacy_agents.items()
            }
        
        all_agents = {}
        
        for name, state in self.legacy_agents.items():
            all_agents[name] = {
                'confidence': round(state['confidence'], 3),
                'performance': state['performance'],
                'department': 'legacy',
                'status': 'operational'
            }
        
        try:
            enhanced = agent_manager.get_agent_status()
            
            if isinstance(enhanced, dict):
                for name, data in enhanced.items():
                    if isinstance(data, dict):
                        all_agents[name] = {
                            'confidence': round(data.get('confidence', 0.75), 3),
                            'performance': data.get('performance', 75.0),
                            'department': data.get('department', 'ai_firm'),
                            'status': 'operational'
                        }
                    elif isinstance(data, (int, float)):
                        all_agents[name] = {
                            'confidence': 0.75,
                            'count': data,
                            'department': 'ai_firm',
                            'status': 'operational'
                        }
            elif isinstance(enhanced, int):
                all_agents['total_enhanced_agents'] = {
                    'count': enhanced,
                    'status': 'operational'
                }
        except Exception as e:
            logger.warning(f"Agent status retrieval error: {e}")
        
        return all_agents

# Initialize system
yantrax_system = YantraXEnhancedSystem()

# ==================== API ENDPOINTS ====================

@app.route('/', methods=['GET'])
@handle_errors
def health_check():
    return jsonify({
        'message': 'YantraX RL Backend v4.6 - DIAGNOSTIC MODE',
        'status': 'operational',
        'version': '4.6.0',
        'integration': {
            'ai_firm': AI_FIRM_READY,
            'rl_core': RL_ENV_READY,
            'market_service_v2': MARKET_SERVICE_READY,
            'mode': 'fully_integrated' if (AI_FIRM_READY and RL_ENV_READY) else (
                'ai_firm_only' if AI_FIRM_READY else 'legacy'
            )
        },
        'data_sources': {
            'primary': 'FMP (batch quote API)' if MARKET_SERVICE_READY else 'None',
            'secondary': 'Alpaca (optional)' if MARKET_SERVICE_READY else 'None',
            'fallback': 'Disabled'
        },
        'components': {
            'total_agents': 24 if AI_FIRM_READY else 4,
            'ceo_active': AI_FIRM_READY,
            'personas_active': AI_FIRM_READY,
            'rl_environment': 'MarketSimEnv' if RL_ENV_READY else 'None'
        },
        'stats': error_counts,
        'timestamp': datetime.now().isoformat()
    })

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

        params = {'apikey': fmp_key}

        # Try v3 quote endpoint first
        url_v3 = f"https://financialmodelingprep.com/api/v3/quote/{symbol}"
        logger.info(f"  Trying v3 URL: {url_v3}")
        response = requests.get(url_v3, params=params, timeout=10)
        logger.info(f"  Status: {response.status_code}")
        logger.info(f"  Response: {response.text[:200]}")

        # If 403 with Legacy Endpoint message, try v4
        if response.status_code == 403 and 'Legacy Endpoint' in (response.text or ''):
            url_v4 = f"https://financialmodelingprep.com/api/v4/quote/{symbol}"
            logger.warning(f"  FMP v3 legacy detected; trying v4 URL: {url_v4}")
            response = requests.get(url_v4, params=params, timeout=10)
            logger.info(f"  v4 Status: {response.status_code}")
            logger.info(f"  v4 Response: {response.text[:200]}")

        # If still not ok, try quote-short
        if not response.ok:
            url_qs = f"https://financialmodelingprep.com/api/v3/quote-short/{symbol}"
            logger.info(f"  Trying quote-short URL: {url_qs}")
            response = requests.get(url_qs, params=params, timeout=10)
            logger.info(f"  quote-short Status: {response.status_code}")
            logger.info(f"  quote-short Response: {response.text[:200]}")

        # As a final single-symbol fallback, try real-time price
        if not response.ok:
            url_rt = f"https://financialmodelingprep.com/api/v3/stock/real-time-price/{symbol}"
            logger.info(f"  Trying real-time URL: {url_rt}")
            response = requests.get(url_rt, params=params, timeout=10)
            logger.info(f"  real-time Status: {response.status_code}")
            logger.info(f"  real-time Response: {response.text[:200]}")

        # If FMP returned non-2xx, treat as error so callers get a clear failure
        if not response.ok:
            try:
                payload = response.json()
            except Exception:
                payload = {'error': 'invalid_response', 'text': response.text}
            return jsonify({
                'status': 'error',
                'symbol': symbol,
                'response_status': response.status_code,
                'response': payload,
                'timestamp': datetime.now().isoformat()
            }), response.status_code

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
        }), 500

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
        # Allow using POLYGON_* env var aliases or explicit MASSIVE_API_KEY
        massive_key = os.getenv('MASSIVE_API_KEY') or os.getenv('POLYGON_API_KEY') or os.getenv('POLYGON_KEY')
        base_url = os.getenv('MASSIVE_BASE_URL')
        if not massive_key:
            logger.error('MASSIVE/POLYGON API key not configured')
            return jsonify({'status': 'error', 'message': 'MASSIVE/POLYGON API key not configured'}), 400

        logger.info(f"Using Massive provider key (first 8 chars): {massive_key[:8]}")
        msvc = MassiveMarketDataService(api_key=massive_key, base_url=base_url)
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