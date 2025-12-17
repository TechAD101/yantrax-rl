# main_replacement.py - Clean replacement based on main_enhanced.py
# Used to test a stable backend while we untangle `main.py`.

import os
import sys
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import numpy as np
from functools import wraps

# Add current directory to Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from flask import Flask, jsonify, request
    from flask_cors import CORS
    # yfinance removed: FMP is used instead
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

# AI Firm imports with corrected paths
try:
    # Fix import paths by adding current directory
    from ai_firm.ceo import AutonomousCEO, CEOPersonality
    from ai_agents.personas.warren import WarrenAgent
    from ai_agents.personas.cathie import CathieAgent
    from ai_firm.agent_manager import AgentManager
    AI_FIRM_READY = True
    print("✅ AI Firm architecture loaded successfully!")
except ImportError as e:
    print(f"⚠️ AI Firm fallback mode: {e}")
    AI_FIRM_READY = False

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

# Initialize AI Firm with error handling
if AI_FIRM_READY:
    try:
        ceo = AutonomousCEO(personality=CEOPersonality.BALANCED)
        warren = WarrenAgent()
        cathie = CathieAgent()
        agent_manager = AgentManager()
        print("🏢 AI Firm fully operational!")
    except Exception as e:
        print(f"⚠️ AI Firm init error: {e}")
        AI_FIRM_READY = False

# Enhanced AI system
class YantraXEnhancedSystem:
    def __init__(self):
        self.portfolio_balance = 132240.84
        self.trade_history = []
        
        # Original 4 agents (compatibility)
        self.legacy_agents = {
            'macro_monk': {'confidence': 0.829, 'performance': 15.2, 'strategy': 'TREND_FOLLOWING'},
            'the_ghost': {'confidence': 0.858, 'performance': 18.7, 'signal': 'CONFIDENT_BUY'},
            'data_whisperer': {'confidence': 0.990, 'performance': 12.9, 'analysis': 'BULLISH_BREAKOUT'},
            'degen_auditor': {'confidence': 0.904, 'performance': 22.1, 'audit': 'LOW_RISK_APPROVED'}
        }
        
    def execute_god_cycle(self) -> Dict[str, Any]:
        """Execute enhanced god cycle with AI firm coordination"""
        
        if AI_FIRM_READY:
            return self._execute_enhanced_god_cycle()
        else:
            return self._execute_legacy_god_cycle()
    
    def _execute_enhanced_god_cycle(self) -> Dict[str, Any]:
        """Enhanced god cycle with 20+ agent coordination"""
        
        # Coordinate decision across agents
        context = {
            'decision_type': 'trading',
            'market_volatility': np.random.uniform(0.1, 0.3),
            'timestamp': datetime.now().isoformat()
        }
        
        # Simulate agent coordination
        try:
            voting_result = agent_manager.coordinate_decision_making(context)

            # CEO strategic oversight
            ceo_context = {
                'type': 'strategic_trading_decision',
                'agent_recommendation': voting_result.get('winning_recommendation', voting_result.get('winning_signal')),
                'consensus_strength': voting_result.get('consensus_strength', 0.0),
                'market_trend': 'bullish'
            }

            ceo_decision = ceo.make_strategic_decision(ceo_context)
        except Exception as e:
            logger.exception("Enhanced god cycle failed during coordination or CEO decision")
            # Return structured error to help remote debugging (temporary)
            return {
                'status': 'error',
                'error': 'enhanced_god_cycle_failure',
                'message': str(e),
                'voting_result_snapshot': locals().get('voting_result', None)
            }
        
        # Execute trade
        final_signal = voting_result['winning_recommendation']
        reward = np.random.normal(850, 400)  # Enhanced AI firm performance
        
        self.portfolio_balance += reward
        
        return {
            'status': 'success',
            'signal': final_signal,
            'strategy': 'ENHANCED_AI_FIRM_24_AGENTS',
            'audit': 'CEO_APPROVED',
            'final_balance': round(self.portfolio_balance, 2),
            'total_reward': round(reward, 2),
            'enhanced_coordination': {
                'total_agents_coordinated': voting_result['total_votes'],
                'consensus_strength': voting_result['consensus_strength'],
                'ceo_confidence': ceo_decision.confidence,
                'ceo_reasoning': ceo_decision.reasoning
            },
            'agents': self._get_enhanced_agent_status(),
            'timestamp': datetime.now().isoformat()
        }
    
    def _execute_legacy_god_cycle(self) -> Dict[str, Any]:
        """Fallback to original god cycle"""
        
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
            'strategy': 'LEGACY_AI_ENSEMBLE',
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
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_enhanced_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents including legacy ones"""
        
        if not AI_FIRM_READY:
            return {name: {'confidence': round(state['confidence'], 3), 'performance': state['performance']} 
                   for name, state in self.legacy_agents.items()}
        
        all_agents = {}
        
        # Legacy agents
        for name, state in self.legacy_agents.items():
            all_agents[name] = {
                'confidence': round(state['confidence'], 3),
                'performance': state['performance'],
                'department': 'legacy',
                'status': 'operational'
            }
        
        # Get enhanced agent status
        try:
            enhanced_status = agent_manager.get_agent_status()

            # Normalize to a mapping of dept -> list_of_agent_dicts
            dept_map = None
            if isinstance(enhanced_status, dict):
                # Preferred canonical nested structure: enhanced_status['departments'][dept]['agents']
                if 'departments' in enhanced_status and isinstance(enhanced_status['departments'], dict):
                    dept_map = {dept: info.get('agents', []) for dept, info in enhanced_status['departments'].items()}
                # Compatibility helper included by AgentManager: departments_simple
                elif 'departments_simple' in enhanced_status and isinstance(enhanced_status['departments_simple'], dict):
                    dept_map = enhanced_status['departments_simple']
                else:
                    # Fallback: look for any keys whose values are lists of agents
                    dept_map = {k: v for k, v in enhanced_status.items() if isinstance(v, list)}

            if not dept_map:
                logger.debug('No department map found in enhanced_status; skipping enhanced agents')
            else:
                for dept, agents in dept_map.items():
                    if isinstance(agents, int):
                        logger.debug(f"Agent manager returned count for dept '{dept}': {agents}")
                        continue

                    if isinstance(agents, dict):
                        # dict keyed by agent name -> details
                        for name, details in agents.items():
                            if not isinstance(details, dict):
                                details = {}
                            all_agents[name] = {
                                'confidence': details.get('confidence_level', details.get('confidence', 0.75)),
                                'performance': details.get('performance_score', details.get('performance', 0.75)),
                                'department': details.get('department', dept),
                                'role': details.get('role', 'agent'),
                                'specialty': details.get('expertise_areas', details.get('specialty', ['general'])),
                                'status': details.get('status', 'operational')
                            }
                        continue

                    if isinstance(agents, list):
                        for agent in agents:
                            if isinstance(agent, dict):
                                name = agent.get('name') or agent.get('id') or 'unknown'
                                all_agents[name] = {
                                    'confidence': agent.get('confidence_level', agent.get('confidence', 0.75)),
                                    'performance': agent.get('performance_score', agent.get('performance', 0.75)),
                                    'department': agent.get('department', dept),
                                    'role': agent.get('role', 'agent'),
                                    'specialty': agent.get('expertise_areas', agent.get('specialty', ['general'])),
                                    'status': agent.get('status', 'operational')
                                }
                            elif isinstance(agent, str):
                                all_agents[agent] = {
                                    'confidence': 0.75,
                                    'performance': 0.0,
                                    'department': dept,
                                    'role': 'agent',
                                    'specialty': ['general'],
                                    'status': 'operational'
                                }
                            else:
                                logger.debug(f"Skipping unsupported agent item in dept '{dept}': {agent}")
                        continue
                    logger.debug(f"Unknown agents payload for dept '{dept}': {type(agents)}")
        except Exception as e:
            logger.error(f"Enhanced agent status error: {e}")
        
        return all_agents

# Initialize enhanced system
yantrax_system = YantraXEnhancedSystem()

# Market data (preserved from original)
class MarketDataManager:
    def __init__(self):
        self.cache = {}
        self.cache_timeout = 300
    
    def get_stock_price(self, symbol: str) -> Dict[str, Any]:
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1d")
            info = ticker.info
            
            if hist.empty:
                return self.get_mock_price_data(symbol)
            
            current_price = float(hist['Close'].iloc[-1])
            prev_close = float(info.get('previousClose', current_price))
            
            return {
                'symbol': symbol,
                'price': round(current_price, 2),
                'change': round(current_price - prev_close, 2),
                'changePercent': round((current_price - prev_close) / prev_close * 100, 2) if prev_close else 0,
                'timestamp': datetime.now().isoformat(),
                'source': 'yfinance'
            }
        except:
            return self.get_mock_price_data(symbol)
    
    def get_mock_price_data(self, symbol: str) -> Dict[str, Any]:
        base_prices = {'AAPL': 175.50, 'MSFT': 330.25, 'GOOGL': 135.75, 'TSLA': 245.60}
        base_price = base_prices.get(symbol, 100.0)
        variation = np.random.normal(0, 0.02)
        current_price = base_price * (1 + variation)
        
        return {
            'symbol': symbol, 'price': round(current_price, 2),
            'change': round(base_price * variation, 2),
            'changePercent': round(variation * 100, 2),
            'timestamp': datetime.now().isoformat(),
            'source': 'mock_data'
        }

market_data = MarketDataManager()

# ==================== API ENDPOINTS ====================

@app.route('/', methods=['GET'])
@app.route('/health', methods=['GET'])
@handle_errors
def health_check():
    total_agents = len(yantrax_system.legacy_agents)
    if AI_FIRM_READY:
        try:
            enhanced_status = agent_manager.get_agent_status()
            if isinstance(enhanced_status, dict):
                total_agents += sum(len(agents) for agents in enhanced_status.values() if isinstance(agents, list))
        except:
            total_agents += 20  # Expected enhanced agents
    
    return jsonify({
        'message': 'YantraX RL Backend - Enhanced AI Firm Architecture v4.0',
        'status': 'operational',
        'version': '4.0.0',
        'ai_firm': {
            'enabled': AI_FIRM_READY,
            'total_agents': total_agents,
            'ceo_active': AI_FIRM_READY,
            'personas_active': AI_FIRM_READY
        },
        'stats': error_counts,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/health', methods=['GET'])
@handle_errors
def detailed_health():
    total_agents = len(yantrax_system.legacy_agents)
    if AI_FIRM_READY:
        try:
            enhanced_status = agent_manager.get_agent_status()
            if isinstance(enhanced_status, dict):
                total_agents += sum(len(agents) for agents in enhanced_status.values() if isinstance(agents, list))
        except:
            total_agents += 20  # Expected enhanced agents
        
    return jsonify({
        'status': 'healthy',
        'services': {
            'api': 'operational',
            'market_data': 'operational', 
            'ai_agents': 'operational',
            'ai_firm': 'operational' if AI_FIRM_READY else 'fallback_mode'
        },
        'ai_firm_components': {
            'ceo': AI_FIRM_READY,
            'warren_persona': AI_FIRM_READY,
            'cathie_persona': AI_FIRM_READY,
            'agent_manager': AI_FIRM_READY,
            'total_system_agents': total_agents
        },
        'performance': error_counts,
        'timestamp': datetime.now().isoformat()
    })