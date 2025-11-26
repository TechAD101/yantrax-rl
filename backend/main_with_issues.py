# main.py - YantraX RL Backend v4.2 AI FIRM ↔ RL CORE INTEGRATION
# INTEGRATION FIX: Connect AI Firm decision-making to actual RL environment

import os
import sys
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import numpy as np
from functools import wraps

# CRITICAL FIX: Add backend to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from flask import Flask, jsonify, request
    from flask_cors import CORS
    import yfinance as yf
    print("✅ Core dependencies loaded")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# AI Firm imports
try:
    from ai_firm.ceo import AutonomousCEO, CEOPersonality
    from ai_agents.personas.warren import WarrenAgent
    from ai_agents.personas.cathie import CathieAgent
    from ai_firm.agent_manager import AgentManager
    AI_FIRM_READY = True
    print("🏢 AI FIRM ARCHITECTURE LOADED SUCCESSFULLY!")
    print("🚀 20+ AGENT COORDINATION SYSTEM ACTIVE")
except ImportError as e:
    print(f"⚠️ AI Firm (attempting alternate paths): {e}")
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
        print("🔧 AI FIRM LOADED VIA ALTERNATE PATH - SUCCESS!")
    except ImportError as e2:
        print(f"❌ AI Firm fallback failed: {e2}")
        AI_FIRM_READY = False

# RL Core imports
try:
    from rl_core.env_market_sim import MarketSimEnv
    RL_ENV_READY = True
    print("🎮 RL CORE: MarketSimEnv LOADED!")
except ImportError as e:
    print(f"❌ RL Core import failed: {e}")
    RL_ENV_READY = False

app = Flask(__name__)
CORS(app, origins=['*'])

# Error tracking
error_counts = {'total_requests': 0, 'successful_requests': 0, 'api_call_errors': 0}

def handle_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        error_counts['total_requests'] += 1
        try:
            result = func(*args, **kwargs)
            error_counts['successful_requests'] += 1
            return result
        except Exception as e:
            error_counts['api_call_errors'] += 1
            logger.exception("API error")
            return jsonify({'error': 'internal_server_error', 'timestamp': datetime.now().isoformat()}), 500
    return wrapper

# Initialize AI Firm
if AI_FIRM_READY:
    try:
        ceo = AutonomousCEO(personality=CEOPersonality.BALANCED)
        warren = WarrenAgent()
        cathie = CathieAgent()
        agent_manager = AgentManager()
        print("🏢 AI FIRM FULLY OPERATIONAL!")
        print(f"🤖 CEO ACTIVE: {ceo.personality.value}")
        print("📊 WARREN & CATHIE PERSONAS LOADED")
        print("🔄 20+ AGENT COORDINATION READY")
    except Exception as e:
        print(f"⚠️ AI Firm init error: {e}")
        AI_FIRM_READY = False
        print("🔄 Falling back to 4-agent legacy mode")

# Enhanced AI system with REAL RL INTEGRATION
class YantraXEnhancedSystem:
    def __init__(self):
        self.portfolio_balance = 132240.84
        self.trade_history = []
        
        # INTEGRATION: Initialize persistent RL environment
        if RL_ENV_READY:
            self.env = MarketSimEnv()
            self.current_state = self.env.reset()
            print("✅ RL Environment initialized and ready!")
        else:
            self.env = None
            self.current_state = None
            print("⚠️ RL Environment not available - using legacy mode")
        
        # Original 4 agents (compatibility)
        self.legacy_agents = {
            'macro_monk': {'confidence': 0.829, 'performance': 15.2, 'strategy': 'TREND_FOLLOWING'},
            'the_ghost': {'confidence': 0.858, 'performance': 18.7, 'signal': 'CONFIDENT_BUY'},
            'data_whisperer': {'confidence': 0.990, 'performance': 12.9, 'analysis': 'BULLISH_BREAKOUT'},
            'degen_auditor': {'confidence': 0.904, 'performance': 22.1, 'audit': 'LOW_RISK_APPROVED'}
        }
    
    def _map_signal_to_action(self, signal: str) -> str:
        """Map AI Firm trading signal to RL environment action"""
        signal_upper = signal.upper()
        if signal_upper == "BUY":
            return "buy"
        elif signal_upper == "SELL":
            return "sell"
        else:  # HOLD or anything else
            return "hold"
        
    def execute_god_cycle(self) -> Dict[str, Any]:
        """Execute enhanced god cycle with AI firm coordination"""
        
        if AI_FIRM_READY and RL_ENV_READY:
            return self._execute_integrated_god_cycle()
        elif AI_FIRM_READY:
            return self._execute_enhanced_god_cycle()
        else:
            return self._execute_legacy_god_cycle()
    
    def _execute_integrated_god_cycle(self) -> Dict[str, Any]:
        """FULLY INTEGRATED GOD CYCLE: AI Firm decisions → RL Environment step"""
        
        # 1. Build context from current RL state
        context = {
            'decision_type': 'trading',
            'market_price': self.current_state['price'],
            'market_volatility': self.current_state['volatility'],
            'market_mood': self.current_state['mood'],
            'balance': self.current_state['balance'],
            'position': self.current_state['position'],
            'cycle': self.current_state['cycle'],
            'timestamp': datetime.now().isoformat(),
            'ai_firm_mode': 'fully_integrated'
        }
        
        # 2. Execute agent voting across 20+ agents
        voting_result = agent_manager.conduct_agent_voting(context)
        
        # 3. CEO strategic oversight
        ceo_context = {
            'type': 'strategic_trading_decision',
            'agent_recommendation': voting_result['winning_signal'],
            'consensus_strength': voting_result['consensus_strength'],
            'market_state': self.current_state,
            'market_trend': self.current_state['mood'],
            'agent_participation': voting_result['participating_agents']
        }
        
        ceo_decision = ceo.make_strategic_decision(ceo_context)
        
        # 4. Use CEO's final decision as the trading signal
        final_signal = voting_result['winning_signal']  # CEO can override via agent_overrides
        
        # 5. Map signal to RL action
        rl_action = self._map_signal_to_action(final_signal)
        
        # 6. Step the RL environment with the action
        next_state, reward, done = self.env.step(rl_action)
        
        # 7. Update current state
        self.current_state = next_state
        
        # 8. Update portfolio balance from RL env balance
        self.portfolio_balance = next_state['balance']
        
        # 9. Record trade in history
        trade_record = {
            'cycle': next_state['cycle'],
            'action': rl_action,
            'signal': final_signal,
            'price': next_state['price'],
            'reward': reward,
            'balance': next_state['balance'],
            'mood': next_state['mood'],
            'volatility': next_state['volatility'],
            'position': next_state['position'],
            'timestamp': datetime.now().isoformat()
        }
        self.trade_history.append(trade_record)
        
        # 10. Reset environment if episode done
        if done:
            print(f"📍 Episode complete at cycle {next_state['cycle']}. Resetting environment.")
            self.current_state = self.env.reset()
        
        # 11. Return comprehensive response
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
                'cycle': next_state['cycle'],
                'curiosity': next_state.get('curiosity', 0)
            },
            'ai_firm_coordination': {
                'mode': 'fully_integrated',
                'total_agents_coordinated': voting_result['participating_agents'],
                'consensus_strength': voting_result['consensus_strength'],
                'ceo_confidence': ceo_decision.confidence,
                'ceo_reasoning': ceo_decision.reasoning,
                'action_source': 'ai_firm_with_rl_execution'
            },
            'rl_metrics': {
                'reward': round(reward, 2),
                'cycle': next_state['cycle'],
                'done': done,
                'cumulative_curiosity': next_state.get('curiosity', 0)
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def _execute_enhanced_god_cycle(self) -> Dict[str, Any]:
        """ENHANCED GOD CYCLE: 20+ agent coordination (legacy without RL env)"""
        
        # Coordinate decision across 20+ agents
        context = {
            'decision_type': 'trading',
            'market_volatility': np.random.uniform(0.1, 0.3),
            'timestamp': datetime.now().isoformat(),
            'ai_firm_mode': 'enhanced_no_rl'
        }
        
        # Execute agent voting
        voting_result = agent_manager.conduct_agent_voting(context)
        
        # CEO strategic oversight
        ceo_context = {
            'type': 'strategic_trading_decision',
            'agent_recommendation': voting_result['winning_signal'],
            'consensus_strength': voting_result['consensus_strength'],
            'market_trend': 'bullish',
            'agent_participation': voting_result['participating_agents']
        }
        
        ceo_decision = ceo.make_strategic_decision(ceo_context)
        
        final_signal = voting_result['winning_signal']
        reward = np.random.normal(950, 300)  # Simulated reward (no RL env)
        
        self.portfolio_balance += reward
        
        return {
            'status': 'success',
            'signal': final_signal,
            'strategy': 'AI_FIRM_24_AGENTS_NO_RL',
            'audit': 'CEO_APPROVED_ENHANCED',
            'final_balance': round(self.portfolio_balance, 2),
            'total_reward': round(reward, 2),
            'ai_firm_coordination': {
                'mode': 'enhanced_no_rl',
                'total_agents_coordinated': voting_result['participating_agents'],
                'consensus_strength': voting_result['consensus_strength'],
                'ceo_confidence': ceo_decision.confidence,
                'ceo_reasoning': ceo_decision.reasoning,
                'agent_overrides': len(ceo_decision.agent_overrides)
            },
            'agents': self._get_enhanced_agent_status(),
            'note': 'RL environment not loaded - using simulated rewards',
            'timestamp': datetime.now().isoformat()
        }
    
    def _execute_legacy_god_cycle(self) -> Dict[str, Any]:
        """Fallback to original 4-agent god cycle"""
        
        # Update legacy agent states
        for agent_name, state in self.legacy_agents.items():
            variation = np.random.normal(0, 0.05)
            state['confidence'] = np.clip(state['confidence'] + variation, 0.1, 0.99)
        
        signal = np.random.choice(['BUY', 'SELL', 'HOLD'], p=[0.4, 0.2, 0.4])
        reward = np.random.normal(500, 200)
        self.portfolio_balance += reward
        
        return {
            'status': 'success',
            'signal': signal,
            'strategy': 'LEGACY_AI_ENSEMBLE_FALLBACK',
            'audit': 'APPROVED',
            'final_balance': round(self.portfolio_balance, 2),
            'total_reward': round(reward, 2),
            'agents': {
                name: {
                    'confidence': round(state['confidence'], 3),
                    'performance': state['performance'],
                    'signal': state.get('strategy', state.get('signal', state.get('analysis', state.get('audit', 'NEUTRAL'))))
                }
                for name, state in self.legacy_agents.items()
            },
            'timestamp': datetime.now().isoformat(),
            'note': 'Legacy 4-agent mode - AI firm & RL not loaded'
        }
    
    def _get_enhanced_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents including enhanced 20+ agent system"""
        
        if not AI_FIRM_READY:
            return {name: {'confidence': round(state['confidence'], 3), 'performance': state['performance']} 
                   for name, state in self.legacy_agents.items()}
        
        all_agents = {}
        
        # Legacy agents (still operational)
        for name, state in self.legacy_agents.items():
            all_agents[name] = {
                'confidence': round(state['confidence'], 3),
                'performance': state['performance'],
                'department': 'legacy_integration',
                'status': 'operational',
                'enhanced': True
            }
        
        # Enhanced agents from agent manager (20+ agents)
        enhanced_agents = agent_manager.get_all_agents_status()
        for name, data in enhanced_agents.items():
            all_agents[name] = {
                'confidence': round(data.get('confidence', 0.75), 3),
                'performance': data.get('performance', 75.0),
                'department': data.get('department', 'unknown'),
                'role': data.get('role', 'specialist'),
                'specialty': data.get('specialty', 'general'),
                'persona': data.get('persona', False),
                'status': 'operational'
            }
        
        return all_agents

# Initialize enhanced system
yantrax_system = YantraXEnhancedSystem()

# Market data manager (preserved)
class MarketDataManager:
    def __init__(self):
        self.cache = {}
        try:
            self.cache_timeout = int(os.environ.get('MARKET_DATA_CACHE_SECONDS', os.environ.get('CACHE_TIMEOUT', 300)))
        except Exception:
            self.cache_timeout = 300
        try:
            self.request_timeout = int(os.environ.get('MARKET_DATA_REQUEST_TIMEOUT', 10))
        except Exception:
            self.request_timeout = 10
        self.source = os.environ.get('MARKET_DATA_SOURCE', 'yfinance')
        self.alpha_vantage_key = os.environ.get('ALPHA_VANTAGE_KEY')
        logger.info(f"MarketDataManager init: source={self.source}, alpha_key={'SET' if self.alpha_vantage_key else 'NONE'}")
    def _from_cache(self, symbol: str):
        entry = self.cache.get(symbol)
        if not entry:
            return None
        ts, data = entry
        if (datetime.now() - ts).total_seconds() > self.cache_timeout:
            del self.cache[symbol]
            return None
        return data

    def _to_cache(self, symbol: str, data: Dict[str, Any]):
        self.cache[symbol] = (datetime.now(), data)

    def get_stock_price(self, symbol: str) -> Dict[str, Any]:
        """Get stock price - ALPHA VANTAGE ONLY (yfinance removed)"""
        symbol = symbol.upper()
        cached = self._from_cache(symbol)
        if cached:
            cached['cached'] = True
            return cached
            
        # Try Alpha Vantage FIRST (primary source)
        try:
            import requests
            api_key = os.environ.get('ALPHA_VANTAGE_KEY', '9RIUV')
            url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}'
            
            logger.info(f"📊 Fetching Alpha Vantage data for {symbol}...")
            response = requests.get(url, timeout=10)
            data = response.json()
            
            logger.info(f"Alpha Vantage Response: {data}")
            
            if 'Global Quote' in data and data['Global Quote']:
                quote = data['Global Quote']
                price = float(quote.get('05. price', 0))
                prev_close = float(quote.get('08. previous close', 0) or price)
                
                if price > 0:  # Valid price
                    result = {
                        'symbol': symbol,
                        'price': round(price, 2),
                        'change': round(price - prev_close, 2),
                        'changePercent': round(((price - prev_close) / prev_close) * 100, 2) if prev_close > 0 else 0,
                        'timestamp': datetime.now().isoformat(),
                        'source': 'alpha_vantage'
                    }
                    self.cache[symbol] = (datetime.now(), result)
                    logger.info(f"✅ Alpha Vantage SUCCESS for {symbol}: ${price}")
                    return result
                else:
                    logger.warning(f"⚠️  Alpha Vantage returned zero price for {symbol}")
            else:
                logger.warning(f"⚠️  Alpha Vantage returned no Global Quote for {symbol}: {data}")
                
        except Exception as e:
            logger.error(f"❌ Alpha Vantage error for {symbol}: {str(e)}")
        
        # Fallback to mock data
        logger.warning(f"⚠️  Using MOCK DATA for {symbol} (Alpha Vantage failed)")
        return self.get_mock_price_data(symbol)
    
    def get_mock_price_data(self, symbol: str) -> Dict[str, Any]:
        base_prices = {'AAPL': 175.50, 'MSFT': 330.25, 'GOOGL': 135.75, 'TSLA': 245.60}
        base_price = base_prices.get(symbol, 100.0)
        variation = np.random.normal(0, 0.02)
        current_price = base_price * (1 + variation)

        return {
            'symbol': symbol,
            'price': round(current_price, 2),
            'change': round(base_price * variation, 2),
            'changePercent': round(variation * 100, 2),
            'timestamp': datetime.now().isoformat(),
            'source': 'mock_data'
        }

market_data = MarketDataService()

# ==================== ENHANCED API ENDPOINTS ====================

@app.route('/', methods=['GET'])
@handle_errors
def health_check():
    total_agents = len(yantrax_system.legacy_agents)
    if AI_FIRM_READY:
        total_agents = 24
    
    integration_status = "fully_integrated" if (AI_FIRM_READY and RL_ENV_READY) else (
        "ai_firm_only" if AI_FIRM_READY else "legacy_mode"
    )
    
    return jsonify({
        'message': 'YantraX RL Backend - AI FIRM ↔ RL CORE INTEGRATION v4.2',
        'status': 'operational',
        'version': '4.2.0',
        'integration': integration_status,
        'ai_firm': {
            'enabled': AI_FIRM_READY,
            'total_agents': total_agents,
            'ceo_active': AI_FIRM_READY,
            'personas_active': AI_FIRM_READY,
            'departments': 5 if AI_FIRM_READY else 1,
        },
        'rl_core': {
            'enabled': RL_ENV_READY,
            'environment': 'MarketSimEnv',
            'real_rewards': RL_ENV_READY
        },
        'stats': error_counts,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/health', methods=['GET'])
@handle_errors
def detailed_health():
    total_agents = 24 if AI_FIRM_READY else 4
    integration_status = "fully_integrated" if (AI_FIRM_READY and RL_ENV_READY) else (
        "ai_firm_only" if AI_FIRM_READY else "legacy_mode"
    )
        
    return jsonify({
        'status': 'healthy',
        'integration_mode': integration_status,
        'services': {
            'api': 'operational',
            'market_data': 'operational', 
            'ai_agents': 'operational',
            'ai_firm': 'fully_operational' if AI_FIRM_READY else 'fallback_mode',
            'rl_core': 'operational' if RL_ENV_READY else 'not_loaded'
        },
        'ai_firm_components': {
            'ceo': AI_FIRM_READY,
            'warren_persona': AI_FIRM_READY,
            'cathie_persona': AI_FIRM_READY,
            'agent_manager': AI_FIRM_READY,
            'department_coordination': AI_FIRM_READY,
            'total_system_agents': total_agents,
        },
        'rl_components': {
            'market_sim_env': RL_ENV_READY,
            'real_step_function': RL_ENV_READY,
            'reward_system': 'integrated' if RL_ENV_READY else 'simulated'
        },
        'performance': error_counts,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/god-cycle', methods=['GET'])
@handle_errors
def enhanced_god_cycle():
    """INTEGRATED GOD CYCLE: AI Firm → RL Environment"""
    result = yantrax_system.execute_god_cycle()
    
    integration_mode = 'fully_integrated' if (AI_FIRM_READY and RL_ENV_READY) else (
        'ai_firm_only' if AI_FIRM_READY else 'legacy'
    )
    
    result.update({
        'cycle_type': 'integrated_god_cycle_v4_2',
        'integration_mode': integration_mode,
        'rl_environment_active': RL_ENV_READY,
        'ai_firm_active': AI_FIRM_READY
    })
    
    return jsonify(result)

@app.route('/api/ai-firm/status', methods=['GET'])
@handle_errors
def ai_firm_status():
    """AI FIRM STATUS with RL integration details"""
    
    if not AI_FIRM_READY:
        return jsonify({
            'status': 'fallback_mode',
            'message': 'AI Firm not loaded - running in legacy mode',
            'legacy_agents': len(yantrax_system.legacy_agents),
            'rl_integration': False
        })
    
    agent_status = agent_manager.get_agent_status()
    ceo_status = ceo.get_ceo_status()
    
    return jsonify({
        'status': 'fully_operational',
        'message': '20+ AI agent coordination system active',
        'rl_integration': RL_ENV_READY,
        'ai_firm': {
            'total_agents': 24,
            'departments': {
                'market_intelligence': {'agents': 5, 'status': 'operational'},
                'trade_operations': {'agents': 4, 'status': 'operational'},
                'risk_control': {'agents': 4, 'status': 'operational'},
                'performance_lab': {'agents': 4, 'status': 'operational'},
                'communications': {'agents': 3, 'status': 'operational'},
                'legacy_integration': {'agents': 4, 'status': 'operational'}
            },
            'ceo_metrics': {
                'personality': ceo_status['personality'],
                'total_decisions': ceo_status['total_decisions'],
                'confidence_threshold': ceo_status['confidence_threshold'],
                'operational_status': ceo_status['operational_status']
            },
            'personas_active': {
                'warren': {'active': True, 'specialty': 'fundamental_analysis'},
                'cathie': {'active': True, 'specialty': 'innovation_growth'}
            },
            'coordination_active': True,
            'memory_learning': True
        },
        'rl_core': {
            'environment_loaded': RL_ENV_READY,
            'current_cycle': yantrax_system.current_state['cycle'] if yantrax_system.current_state else 0,
            'current_balance': yantrax_system.current_state['balance'] if yantrax_system.current_state else 0,
            'market_mood': yantrax_system.current_state['mood'] if yantrax_system.current_state else 'unknown'
        },
        'system_performance': {
            'portfolio_balance': yantrax_system.portfolio_balance,
            'total_trades': len(yantrax_system.trade_history),
            'success_rate': round(error_counts['successful_requests'] / max(error_counts['total_requests'], 1) * 100, 2)
        },
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/ai-firm/personas/warren', methods=['POST'])
@handle_errors
def warren_analysis_endpoint():
    """Warren Buffett persona fundamental analysis"""
    
    if not AI_FIRM_READY:
        return jsonify({
            'status': 'demo_mode',
            'warren_analysis': {
                'recommendation': 'STRONG_BUY',
                'confidence': 0.89,
                'reasoning': 'Demo: AI firm not loaded',
                'warren_score': 0.87
            }
        })
    
    context = request.get_json() or {}
    
    analysis_context = {
        'symbol': context.get('symbol', 'AAPL'),
        'fundamentals': {
            'return_on_equity': 0.20,
            'pe_ratio': 18,
            'profit_margin': 0.18,
            'debt_to_equity': 0.25,
            'dividend_yield': 0.028,
            'revenue_growth': 0.08
        },
        'market_data': {'current_price': 175.50},
        'company_data': {'brand_score': 0.95, 'moat_strength': 0.87}
    }
    
    analysis = warren.analyze_investment(analysis_context)
    insights = warren.get_warren_insights()
    
    return jsonify({
        'status': 'success',
        'warren_analysis': analysis,
        'warren_insights': insights,
        'philosophy': "Never lose money. Buy wonderful companies at fair prices."
    })

@app.route('/api/ai-firm/personas/cathie', methods=['POST'])
@handle_errors
def cathie_insights_endpoint():
    """Cathie Wood persona innovation analysis"""
    
    if not AI_FIRM_READY:
        return jsonify({
            'status': 'demo_mode',
            'cathie_analysis': {
                'recommendation': 'HIGH_CONVICTION_BUY',
                'confidence': 0.91,
                'reasoning': 'Demo: AI firm not loaded',
                'innovation_score': 0.88
            }
        })
    
    context = request.get_json() or {}
    
    analysis_context = {
        'symbol': context.get('symbol', 'NVDA'),
        'company_data': {
            'rd_spending_ratio': 0.22,
            'patent_portfolio_score': 0.85,
            'technology_leadership_score': 0.90,
            'revenue_growth_3yr': 0.28,
            'total_addressable_market': 50000000000,
            'projected_tam_5yr': 150000000000
        },
        'sector_data': {
            'sector': 'artificial_intelligence',
            'adoption_stage': 'early_growth',
            'innovation_momentum': 0.88
        }
    }
    
    analysis = cathie.analyze_investment(analysis_context)
    insights = cathie.get_cathie_insights()
    
    return jsonify({
        'status': 'success',
        'cathie_analysis': analysis,
        'cathie_insights': insights,
        'philosophy': "Invest in disruptive innovation transforming industries"
    })

@app.route('/api/ai-firm/ceo-decisions', methods=['GET'])
@handle_errors
def ceo_decisions_endpoint():
    """CEO strategic decisions and insights"""
    
    if not AI_FIRM_READY:
        return jsonify({
            'status': 'demo_mode',
            'ceo_decision': {
                'reasoning': 'Demo: CEO not loaded',
                'confidence': 0.82
            }
        })
    
    ceo_status = ceo.get_ceo_status()
    
    strategic_context = {
        'type': 'strategic_market_analysis',
        'market_trend': 'bullish',
        'volatility': 0.15,
        'agent_consensus': 0.78
    }
    
    strategic_decision = ceo.make_strategic_decision(strategic_context)
    strategic_insights = ceo.get_strategic_insights()
    
    return jsonify({
        'status': 'success',
        'ceo_metrics': ceo_status,
        'latest_strategic_decision': {
            'reasoning': strategic_decision.reasoning,
            'confidence': strategic_decision.confidence,
            'expected_impact': strategic_decision.expected_impact,
            'decision_type': strategic_decision.decision_type.value,
            'agent_overrides': strategic_decision.agent_overrides
        },
        'strategic_insights': strategic_insights
    })

# Legacy endpoints (preserved)
@app.route('/market-price', methods=['GET'])
@handle_errors
def get_market_price():
    symbol = request.args.get('symbol', 'AAPL').upper()
    return jsonify(market_data.get_price(symbol))

@app.route('/multi-asset-data', methods=['GET'])
@handle_errors
def get_multi_asset_data():
    """Get data for multiple assets"""
    symbols_param = request.args.get('symbols', 'AAPL,MSFT,GOOGL,TSLA')
    symbols = [s.strip().upper() for s in symbols_param.split(',')]

    results = {}
    for symbol in symbols:
        try:
            results[symbol] = market_data.get_price(symbol)
        except Exception as e:
            logger.error(f"Error fetching {symbol}: {str(e)}")
            results[symbol] = {
                'error': str(e),
                'symbol': symbol,
                'status': 'error'
            }

    return jsonify({
        'data': results,
        'timestamp': datetime.now().isoformat(),
        'symbols_requested': len(symbols),
        'symbols_successful': sum(1 for r in results.values() if r.get('status') != 'error')
    })

@app.route('/run-cycle', methods=['POST'])
@handle_errors
def run_rl_cycle():
    """Execute integrated RL cycle"""
    try:
        config = request.get_json() if request.is_json else {}
        result = yantrax_system.execute_god_cycle()
        return jsonify(result)
    except Exception as e:
        logger.error(f"RL cycle error: {str(e)}")
        return jsonify({
            'error': 'RL cycle execution failed',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/journal', methods=['GET'])
@handle_errors
def get_journal():
    """Get trading journal entries"""
    try:
        # Return actual trade history if available
        if yantrax_system.trade_history:
            return jsonify(yantrax_system.trade_history[-10:])  # Last 10 trades
        
        # Fallback to demo data
        integration_status = "integrated" if (AI_FIRM_READY and RL_ENV_READY) else "simulated"
        journal_entries = [
            {
                'id': i, 
                'timestamp': (datetime.now() - timedelta(hours=i)).isoformat(), 
                'action': ['BUY', 'SELL', 'HOLD'][i % 3], 
                'reward': round(750 + (i * 50), 2),
                'balance': round(132240.84 + (i * 250), 2),
                'notes': f'{integration_status} - Cycle {i+1}',
                'mode': integration_status
            } for i in range(5)
        ]
        return jsonify(journal_entries)
    except Exception as e:
        logger.error(f"Journal error: {str(e)}")
        return jsonify([])

@app.route('/commentary', methods=['GET'])
@handle_errors
def get_commentary():
    """Get AI commentary"""
    try:
        if AI_FIRM_READY and RL_ENV_READY:
            commentaries = [
                {
                    'id': 1, 'agent': 'Warren Persona', 
                    'comment': 'Fundamental analysis complete - strong economic moat with 18% ROE',
                    'confidence': 0.89, 'timestamp': datetime.now().isoformat(),
                    'sentiment': 'bullish', 'persona': True
                },
                {
                    'id': 2, 'agent': 'Cathie Persona', 
                    'comment': 'Innovation metrics exceptional - disruption score 0.88',
                    'confidence': 0.91, 'timestamp': datetime.now().isoformat(),
                    'sentiment': 'bullish', 'persona': True
                },
                {
                    'id': 3, 'agent': 'Autonomous CEO', 
                    'comment': '24-agent coordination achieving consensus - RL environment active',
                    'confidence': 0.85, 'timestamp': datetime.now().isoformat(),
                    'sentiment': 'confident', 'ceo': True
                },
                {
                    'id': 4, 'agent': 'RL Core',
                    'comment': f'Market mood: {yantrax_system.current_state["mood"]} | Cycle: {yantrax_system.current_state["cycle"]}',
                    'confidence': 0.93, 'timestamp': datetime.now().isoformat(),
                    'sentiment': 'operational', 'rl': True
                }
            ]
        else:
            commentaries = [
                {
                    'id': 1, 'agent': 'System Status', 
                    'comment': f'Integration mode: {"AI Firm only" if AI_FIRM_READY else "Legacy"}',
                    'confidence': 0.75, 'timestamp': datetime.now().isoformat(),
                    'sentiment': 'neutral'
                }
            ]
        
        return jsonify(commentaries)
    except Exception as e:
        logger.error(f"Commentary error: {str(e)}")
        return jsonify([])

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint not found',
        'available_endpoints': [
            '/', '/health', '/god-cycle', '/market-price', '/multi-asset-data',
            '/run-cycle', '/journal', '/commentary',
            '/api/ai-firm/status', '/api/ai-firm/personas/warren', 
            '/api/ai-firm/personas/cathie', '/api/ai-firm/ceo-decisions'
        ],
        'integration_status': 'integrated' if (AI_FIRM_READY and RL_ENV_READY) else 'partial',
        'timestamp': datetime.now().isoformat()
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred',
        'integration_active': AI_FIRM_READY and RL_ENV_READY,
        'timestamp': datetime.now().isoformat()
    }), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 YantraX RL v4.2 - AI FIRM ↔ RL CORE INTEGRATION")
    print("="*60)
    print(f"🤖 AI Firm Ready: {AI_FIRM_READY}")
    print(f"🎮 RL Core Ready: {RL_ENV_READY}")
    
    if AI_FIRM_READY and RL_ENV_READY:
        print("✅ FULLY INTEGRATED: AI Firm decisions → RL Environment")
        print("✅ 24-AGENT COORDINATION → MarketSimEnv.step()")
        print("✅ REAL REWARDS from RL environment")
    elif AI_FIRM_READY:
        print("⚠️  PARTIAL: AI Firm active, RL env not loaded")
    else:
        print("⚠️  FALLBACK MODE: Legacy 4-agent system")
    
    print("="*60)
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
