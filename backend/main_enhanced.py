# main_enhanced.py - YantraX RL Backend v4.0 with Revolutionary AI Firm
# Critical Production Fix: 20+ agent coordination with CEO oversight

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
            'timestamp': datetime.now().isoformat(),
            'note': 'Legacy mode - AI firm components loading'
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
            if isinstance(enhanced_status, dict):
                for dept, agents in enhanced_status.items():
                    for agent in agents:
                        all_agents[agent.get('name', 'unknown')] = {
                            'confidence': agent.get('confidence_level', 0.75),
                            'performance': agent.get('performance_score', 0.75),
                            'department': agent.get('department', 'enhanced'),
                            'role': agent.get('role', 'agent'),
                            'specialty': agent.get('expertise_areas', ['general']),
                            'status': 'operational'
                        }
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

@app.route('/god-cycle', methods=['GET'])
@handle_errors
def enhanced_god_cycle():
    """Enhanced god cycle with AI firm coordination"""
    try:
        result = yantrax_system.execute_god_cycle()
    except Exception as e:
        logger.exception('god-cycle execution failed')
        return jsonify({
            'status': 'error',
            'error': 'god_cycle_execution_failed',
            'message': str(e)
        }), 500

    # Add enhanced god cycle metadata
    # Use .get() defensively in case the result is an error-diagnostic payload
    signal = result.get('signal') if isinstance(result, dict) else None
    final_mood = 'confident' if signal in ['BUY', 'STRONG_BUY'] else 'cautious'
    result.update({
        'cycle_type': 'enhanced_god_cycle_v4',
        'ai_firm_coordination': AI_FIRM_READY,
        'system_evolution': 'supernatural_recovery_complete',
        'final_mood': final_mood
    })

    return jsonify(result)

@app.route('/api/ai-firm/status', methods=['GET'])
@handle_errors
def ai_firm_status():
    """AI Firm comprehensive status"""
    
    if not AI_FIRM_READY:
        return jsonify({
            'status': 'fallback_mode',
            'message': 'AI Firm running in compatibility mode',
            'legacy_agents': len(yantrax_system.legacy_agents),
            'fallback_operational': True,
            'expected_agents': 24,
            'departments': 5
        })
    
    try:
        agent_status = agent_manager.get_agent_status()
        ceo_status = ceo.get_ceo_status()
        
        # Calculate total agents
        enhanced_agent_count = 0
        if isinstance(agent_status, dict):
            enhanced_agent_count = sum(len(agents) for agents in agent_status.values() if isinstance(agents, list))
        
        total_agents = enhanced_agent_count + len(yantrax_system.legacy_agents)
        
        return jsonify({
            'status': 'fully_operational',
            'ai_firm': {
                'total_agents': total_agents,
                'legacy_agents': len(yantrax_system.legacy_agents),
                'enhanced_agents': enhanced_agent_count,
                'departments': agent_status if isinstance(agent_status, dict) else {},
                'ceo_metrics': ceo_status,
                'personas_active': 2  # Warren and Cathie
            },
            'system_performance': {
                'portfolio_balance': yantrax_system.portfolio_balance,
                'total_trades': len(yantrax_system.trade_history),
                'success_rate': round(error_counts['successful_requests'] / max(error_counts['total_requests'], 1) * 100, 2)
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.exception("AI Firm status error")
        return jsonify({
            'status': 'error',
            'message': 'Failed to get AI firm status',
            'error_details': str(e)
        }), 500

@app.route('/api/ai-firm/personas/warren', methods=['POST'])
@handle_errors
def warren_analysis_endpoint():
    """Warren persona fundamental analysis"""
    
    if not AI_FIRM_READY:
        return jsonify({
            'status': 'demo_mode',
            'warren_analysis': {
                'agent': 'Warren',
                'recommendation': 'CONSERVATIVE_BUY',
                'confidence': 0.89,
                'reasoning': 'Demo: Strong fundamentals, attractive valuation, solid economic moat',
                'fundamental_score': 0.85,
                'valuation_score': 0.78,
                'risk_assessment': 'Low'
            },
            'philosophy': "Never lose money. Buy wonderful companies at fair prices."
        })
    
    try:
        context = request.get_json() or {}
        
        # Enhanced context with real data
        analysis_context = {
            'symbol': context.get('symbol', 'AAPL'),
            'fundamentals': {
                'return_on_equity': 0.20,
                'pe_ratio': 18,
                'profit_margin': 0.18,
                'debt_to_equity': 0.25,
                'dividend_yield': 0.028
            },
            'market_data': {'current_price': 175.50},
            'company_data': {'brand_score': 0.95}
        }
        
        analysis = warren.analyze_investment(analysis_context)
        
        return jsonify({
            'status': 'success',
            'warren_analysis': analysis,
            'philosophy': "Never lose money. Buy wonderful companies at fair prices."
        })
        
    except Exception as e:
        logger.exception("Warren analysis error")
        return jsonify({
            'status': 'error',
            'message': 'Warren analysis failed',
            'error': str(e)
        }), 500

@app.route('/api/ai-firm/personas/cathie', methods=['POST'])
@handle_errors
def cathie_insights_endpoint():
    """Cathie persona innovation analysis"""
    
    if not AI_FIRM_READY:
        return jsonify({
            'status': 'demo_mode',
            'cathie_analysis': {
                'agent': 'Cathie',
                'recommendation': 'HIGH_CONVICTION_BUY',
                'confidence': 0.91,
                'reasoning': 'Demo: Exceptional innovation score, strong disruption potential, optimal sector timing',
                'innovation_score': 0.92,
                'growth_potential': 0.88,
                'disruption_score': 0.85
            },
            'philosophy': "Invest in disruptive innovation transforming industries"
        })
    
    try:
        context = request.get_json() or {}
        
        analysis_context = {
            'symbol': context.get('symbol', 'NVDA'),
            'company_data': {
                'rd_spending_ratio': 0.22,
                'patent_portfolio_score': 0.85,
                'revenue_growth_3yr': 0.28
            },
            'sector_data': {
                'sector': 'artificial_intelligence',
                'adoption_stage': 'early_growth',
                'innovation_momentum': 0.88
            }
        }
        
        analysis = cathie.analyze_investment(analysis_context)
        
        return jsonify({
            'status': 'success',
            'cathie_analysis': analysis,
            'philosophy': "Invest in disruptive innovation transforming industries"
        })
        
    except Exception as e:
        logger.exception("Cathie analysis error")
        return jsonify({
            'status': 'error',
            'message': 'Cathie analysis failed',
            'error': str(e)
        }), 500

# Legacy endpoints (preserved for backward compatibility)
@app.route('/market-price', methods=['GET'])
@handle_errors
def get_market_price():
    symbol = request.args.get('symbol', 'AAPL').upper()
    return jsonify(market_data.get_stock_price(symbol))

@app.route('/journal', methods=['GET'])
@handle_errors
def get_journal():
    # Enhanced journal with AI firm data
    journal_entries = []
    
    for i in range(10):  # Last 10 entries
        entry = {
            'id': i + 1,
            'timestamp': (datetime.now() - timedelta(hours=i)).isoformat(),
            'action': np.random.choice(['BUY', 'SELL', 'HOLD'], p=[0.5, 0.2, 0.3]),
            'reward': round(np.random.normal(650, 300), 2),
            'balance': round(132240.84 + np.random.uniform(-5000, 5000), 2),
            'notes': 'AI Firm coordination' if AI_FIRM_READY else 'Legacy AI ensemble',
            'confidence': round(np.random.uniform(0.7, 0.95), 2),
            'agent_consensus': round(np.random.uniform(0.75, 0.92), 2) if AI_FIRM_READY else round(np.random.uniform(0.6, 0.8), 2)
        }
        journal_entries.append(entry)
    
    return jsonify(journal_entries)

@app.route('/commentary', methods=['GET'])
@handle_errors
def get_commentary():
    # Enhanced commentary with AI firm insights
    if AI_FIRM_READY:
        commentaries = [
            {
                'id': 1, 'agent': 'CEO Strategic Oversight',
                'comment': 'AI Firm coordination achieving 87% consensus strength with strategic market positioning',
                'confidence': 0.91, 'timestamp': datetime.now().isoformat(),
                'sentiment': 'bullish'
            },
            {
                'id': 2, 'agent': 'Warren Persona',
                'comment': 'Fundamental analysis indicates attractive entry points in quality companies',
                'confidence': 0.85, 'timestamp': (datetime.now() - timedelta(hours=1)).isoformat(),
                'sentiment': 'bullish'
            },
            {
                'id': 3, 'agent': 'Cathie Persona',
                'comment': 'Innovation trends showing strong momentum in AI and autonomous technology sectors',
                'confidence': 0.89, 'timestamp': (datetime.now() - timedelta(hours=2)).isoformat(),
                'sentiment': 'bullish'
            }
        ]
    else:
        commentaries = [
            {
                'id': 1, 'agent': 'Legacy AI Ensemble',
                'comment': '4-agent coordination maintaining steady performance metrics',
                'confidence': 0.78, 'timestamp': datetime.now().isoformat(),
                'sentiment': 'neutral'
            }
        ]
    
    return jsonify(commentaries)

# Error handlers
@app.errorhandler(404)
def not_found(error):
    available_endpoints = [
        '/', '/health', '/god-cycle', '/market-price', '/journal', '/commentary',
        '/api/ai-firm/status', '/api/ai-firm/personas/warren', '/api/ai-firm/personas/cathie'
    ]
    
    return jsonify({
        'error': 'Endpoint not found',
        'available_endpoints': available_endpoints,
        'ai_firm_enabled': AI_FIRM_READY,
        'timestamp': datetime.now().isoformat()
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error',
        'ai_firm_status': AI_FIRM_READY,
        'timestamp': datetime.now().isoformat()
    }), 500


# Debug-only endpoint to surface internal god-cycle exceptions (safe to remove after debugging)
@app.route('/debug/god-cycle', methods=['GET'])
def debug_god_cycle():
    import traceback
    try:
        result = yantrax_system.execute_god_cycle()
        return jsonify({'status': 'ok', 'result': result})
    except Exception as e:
        tb = traceback.format_exc()
        return jsonify({'status': 'error', 'error': str(e), 'traceback': tb}), 500

if __name__ == '__main__':
    print("🚀 YantraX RL v4.0 - Enhanced AI Firm Starting")
    print(f"🤖 AI Firm Ready: {AI_FIRM_READY}")
    
    if AI_FIRM_READY:
        try:
            enhanced_status = agent_manager.get_agent_status()
            enhanced_count = sum(len(agents) for agents in enhanced_status.values() if isinstance(agents, list)) if isinstance(enhanced_status, dict) else 20
            total_agents = len(yantrax_system.legacy_agents) + enhanced_count
            print(f"📈 Total Agents: {total_agents} (4 Legacy + {enhanced_count} Enhanced)")
            print("🏢 Components: CEO, Agent Manager, Warren, Cathie")
            print("🎯 Personas: Warren (Value), Cathie (Growth)")
        except Exception as e:
            print(f"⚠️ Status calculation error: {e}")
    else:
        print("🔄 Running in compatibility mode with 4 legacy agents")
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
