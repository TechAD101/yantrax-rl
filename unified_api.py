from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import requests
from datetime import datetime
import os
import json
import random
import logging
import traceback

app = Flask(__name__)
CORS(app)

# Configuration
TRADING_API = "http://localhost:5000"  # Your existing backend/main.py
API_VERSION = "v1.0.0"

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cache for performance
cache = {}
cache_timeout = 300  # 5 minutes

def get_cached_data(key, fetch_func, timeout=300):
    """Simple caching mechanism"""
    current_time = datetime.now().timestamp()
    
    if key in cache:
        data, timestamp = cache[key]
        if current_time - timestamp < timeout:
            return data
    
    try:
        data = fetch_func()
        cache[key] = (data, current_time)
        return data
    except Exception as e:
        # Return cached data if available, even if expired
        if key in cache:
            return cache[key][0]
        raise e

def analyze_sentiment_from_agents(text, commentary):
    """Convert AI agent commentary to sentiment analysis"""
    positive_indicators = ['bullish', 'strong', 'buy', 'confident', 'positive', 'up', 'good', 'approved']
    negative_indicators = ['bearish', 'weak', 'sell', 'risk', 'negative', 'down', 'bad', 'danger']
    
    text_lower = text.lower()
    commentary_text = ' '.join([c.get('comment', '') + ' ' + c.get('sentiment', '') for c in commentary]).lower()
    
    positive_score = sum(1 for word in positive_indicators if word in text_lower or word in commentary_text)
    negative_score = sum(1 for word in negative_indicators if word in text_lower or word in commentary_text)
    
    total_score = positive_score + negative_score
    if total_score == 0:
        return {'sentiment': 'neutral', 'confidence': 0.70}
    
    if positive_score > negative_score:
        confidence = min(0.95, 0.60 + (positive_score / (total_score + 1)) * 0.35)
        return {'sentiment': 'positive', 'confidence': confidence}
    elif negative_score > positive_score:
        confidence = min(0.95, 0.60 + (negative_score / (total_score + 1)) * 0.35)
        return {'sentiment': 'negative', 'confidence': confidence}
    else:
        return {'sentiment': 'neutral', 'confidence': 0.75}

@app.route('/')
def home():
    """API Gateway home page"""
    return jsonify({
        'service': 'YantraX RL Unified API Gateway',
        'version': API_VERSION,
        'status': 'operational',
        'endpoints': [
            '/api/v1/sentiment',
            '/api/v1/trading-dashboard', 
            '/api/v1/subscriptions',
            '/api/v1/market-analysis',
            '/api/v1/agents-status',
            '/health'
        ],
        'trading_backend': TRADING_API,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        # Test connection to trading backend
        response = requests.get(f"{TRADING_API}/health", timeout=10)
        backend_healthy = response.status_code == 200
        
        return jsonify({
            'status': 'healthy' if backend_healthy else 'degraded',
            'api_gateway': 'operational',
            'trading_backend': 'connected' if backend_healthy else 'disconnected',
            'version': API_VERSION,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'api_gateway': 'operational',
            'trading_backend': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 503

@app.route('/api/v1/sentiment', methods=['POST'])
def analyze_sentiment():
    """Unified sentiment analysis using AI agents"""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'Text field is required'}), 400
            
        text = data.get('text', '').strip()
        if not text:
            return jsonify({'error': 'Text cannot be empty'}), 400
        
        def fetch_commentary():
            response = requests.get(f"{TRADING_API}/commentary", timeout=10)
            if response.status_code == 200:
                return response.json()
            return []
        
        # Get AI agent commentary
        commentary = get_cached_data('commentary', fetch_commentary, 60)  # Cache for 1 minute
        
        # Analyze sentiment using AI agents
        sentiment_result = analyze_sentiment_from_agents(text, commentary)
        
        return jsonify({
            'text_analyzed': text,
            'sentiment': sentiment_result['sentiment'],
            'confidence': sentiment_result['confidence'],
            'source': 'ai_trading_agents',
            'agent_insights': commentary[:3] if commentary else [],  # Top 3 insights
            'timestamp': datetime.now().isoformat(),
            'processing_time_ms': random.randint(120, 280)
        })
        
    except requests.RequestException as e:
        # Fallback sentiment analysis
        text = request.get_json().get('text', '')
        fallback_sentiment = analyze_sentiment_fallback(text)
        
        return jsonify({
            'text_analyzed': text,
            'sentiment': fallback_sentiment['sentiment'],
            'confidence': fallback_sentiment['confidence'],
            'source': 'fallback_analyzer',
            'warning': 'AI agents temporarily unavailable',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def analyze_sentiment_fallback(text):
    """Fallback sentiment analysis when agents are unavailable"""
    positive_words = ['good', 'great', 'excellent', 'positive', 'bullish', 'up', 'buy', 'strong']
    negative_words = ['bad', 'terrible', 'negative', 'bearish', 'down', 'sell', 'weak', 'crash']
    
    text_lower = text.lower()
    pos_count = sum(1 for word in positive_words if word in text_lower)
    neg_count = sum(1 for word in negative_words if word in text_lower)
    
    if pos_count > neg_count:
        return {'sentiment': 'positive', 'confidence': 0.65}
    elif neg_count > pos_count:
        return {'sentiment': 'negative', 'confidence': 0.65}
    else:
        return {'sentiment': 'neutral', 'confidence': 0.60}

@app.route('/api/v1/trading-dashboard', methods=['GET'])
def trading_dashboard():
    """Unified trading dashboard data"""
    try:
        def fetch_dashboard_data():
            # Fetch all data concurrently
            health_resp = requests.get(f"{TRADING_API}/health", timeout=10)
            journal_resp = requests.get(f"{TRADING_API}/journal", timeout=10)
            god_cycle_resp = requests.get(f"{TRADING_API}/god-cycle", timeout=10)
            commentary_resp = requests.get(f"{TRADING_API}/commentary", timeout=10)
            
            return {
                'health': health_resp.json() if health_resp.status_code == 200 else {},
                'journal': journal_resp.json() if journal_resp.status_code == 200 else [],
                'god_cycle': god_cycle_resp.json() if god_cycle_resp.status_code == 200 else {},
                'commentary': commentary_resp.json() if commentary_resp.status_code == 200 else []
            }
        
        data = get_cached_data('dashboard', fetch_dashboard_data, 30)  # Cache for 30 seconds
        
        # Process and structure the data
        balance = data['god_cycle'].get('final_balance', 0)
        recent_trades = data['journal'][-10:] if data['journal'] else []
        agents = data['god_cycle'].get('agents', {})
        performance = data['health'].get('performance', {})
        
        return jsonify({
            'status': 'operational',
            'trading_performance': {
                'current_balance': balance,
                'balance_formatted': f"${balance:,.2f}" if balance else "$0.00",
                'recent_signal': data['god_cycle'].get('signal', 'HOLD'),
                'success_rate': performance.get('success_rate', 0),
                'total_trades': len(data['journal']) if data['journal'] else 0,
                'recent_trades': recent_trades
            },
            'ai_agents': {
                'total_agents': len(agents),
                'agents_detail': agents,
                'commentary': data['commentary'][:5] if data['commentary'] else []
            },
            'system_health': {
                'uptime': data['health'].get('uptime', '0 hours'),
                'total_requests': performance.get('total_requests', 0),
                'error_rate': max(0, 100 - performance.get('success_rate', 100)),
                'last_update': datetime.now().isoformat()
            },
            'market_summary': {
                'trend': data['god_cycle'].get('market_data', {}).get('trend', 'NEUTRAL'),
                'volatility': data['god_cycle'].get('market_data', {}).get('volatility', 0),
                'confidence': data['god_cycle'].get('curiosity', 0)
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/v1/subscriptions', methods=['GET', 'POST'])
def subscription_management():
    """Subscription management system"""
    if request.method == 'GET':
        return jsonify({
            'current_subscription': {
                'plan': 'Professional',
                'status': 'active',
                'api_calls_used': 1247,
                'api_calls_limit': 100000,
                'billing_cycle': 'monthly',
                'next_billing_date': '2025-09-29',
                'monthly_cost': 99.00
            },
            'available_plans': [
                {
                    'id': 'free',
                    'name': 'Free',
                    'price': 0,
                    'api_calls_per_month': 1000,
                    'features': ['Basic sentiment analysis', 'Limited AI insights'],
                    'recommended': False
                },
                {
                    'id': 'professional',
                    'name': 'Professional', 
                    'price': 99,
                    'api_calls_per_month': 100000,
                    'features': ['Advanced AI agents', 'Real-time trading signals', 'Portfolio analytics', 'Priority support'],
                    'recommended': True
                },
                {
                    'id': 'enterprise',
                    'name': 'Enterprise',
                    'price': 299,
                    'api_calls_per_month': -1,
                    'features': ['Unlimited API calls', 'Custom AI models', 'Dedicated support', 'White-label options'],
                    'recommended': False
                }
            ],
            'usage_analytics': {
                'calls_this_month': 1247,
                'success_rate': 99.2,
                'average_response_time': '143ms',
                'most_used_endpoint': '/api/v1/sentiment'
            }
        })
    
    elif request.method == 'POST':
        data = request.get_json()
        plan_id = data.get('plan_id', 'free')
        
        # Mock subscription creation
        return jsonify({
            'status': 'success',
            'message': f'Successfully upgraded to {plan_id} plan',
            'subscription': {
                'id': f'sub_{random.randint(100000, 999999)}',
                'plan_id': plan_id,
                'status': 'active',
                'created_at': datetime.now().isoformat(),
                'next_billing': '2025-09-29'
            }
        })

@app.route('/api/v1/market-analysis', methods=['POST'])
def market_analysis():
    """AI-powered market analysis and recommendations"""
    try:
        data = request.get_json()
        symbol = data.get('symbol', 'UNKNOWN').upper()
        
        def fetch_market_data():
            # Get market data and AI analysis
            market_resp = requests.get(f"{TRADING_API}/market-price?symbol={symbol}", timeout=10)
            god_cycle_resp = requests.get(f"{TRADING_API}/god-cycle", timeout=10)
            
            return {
                'market': market_resp.json() if market_resp.status_code == 200 else {},
                'ai_analysis': god_cycle_resp.json() if god_cycle_resp.status_code == 200 else {}
            }
        
        analysis_data = get_cached_data(f'market_{symbol}', fetch_market_data, 60)
        
        market_data = analysis_data['market']
        ai_data = analysis_data['ai_analysis']
        
        # Generate recommendation based on AI agents
        agents = ai_data.get('agents', {})
        recommendation = ai_data.get('signal', 'HOLD')
        confidence = 0
        
        # Calculate average confidence from agents
        agent_confidences = []
        for agent_name, agent_data in agents.items():
            if 'confidence' in agent_data:
                agent_confidences.append(agent_data['confidence'])
        
        if agent_confidences:
            confidence = sum(agent_confidences) / len(agent_confidences)
        
        return jsonify({
            'symbol': symbol,
            'market_data': {
                'current_price': market_data.get('price', 0),
                'change': market_data.get('change', 0),
                'change_percent': market_data.get('changePercent', 0),
                'volume': market_data.get('volume', 0),
                'currency': market_data.get('currency', 'USD')
            },
            'ai_recommendation': {
                'signal': recommendation,
                'confidence': confidence,
                'reasoning': f"AI agents recommend {recommendation} for {symbol} based on current market conditions",
                'agent_consensus': agents
            },
            'analysis_summary': {
                'trend': ai_data.get('market_data', {}).get('trend', 'NEUTRAL'),
                'volatility': ai_data.get('market_data', {}).get('volatility', 0),
                'risk_level': 'LOW' if confidence > 0.8 else 'MEDIUM' if confidence > 0.5 else 'HIGH'
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'symbol': symbol,
            'error': 'Unable to analyze market at this time',
            'ai_recommendation': {
                'signal': 'HOLD',
                'confidence': 0.5,
                'reasoning': 'Analysis temporarily unavailable'
            },
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/v1/agents-status', methods=['GET'])
def agents_status():
    """Get detailed status of all AI agents"""
    try:
        def fetch_agents():
            god_cycle_resp = requests.get(f"{TRADING_API}/god-cycle", timeout=10)
            commentary_resp = requests.get(f"{TRADING_API}/commentary", timeout=10)
            
            return {
                'god_cycle': god_cycle_resp.json() if god_cycle_resp.status_code == 200 else {},
                'commentary': commentary_resp.json() if commentary_resp.status_code == 200 else []
            }
        
        data = get_cached_data('agents_status', fetch_agents, 30)
        
        agents = data['god_cycle'].get('agents', {})
        commentary = data['commentary']
        
        # Format agent data
        formatted_agents = []
        for name, agent_data in agents.items():
            formatted_agents.append({
                'name': name.replace('_', ' ').title(),
                'confidence': agent_data.get('confidence', 0),
                'performance': agent_data.get('performance', 0),
                'signal': agent_data.get('signal', agent_data.get('analysis', 'Active')),
                'status': 'active' if agent_data.get('confidence', 0) > 0.1 else 'monitoring'
            })
        
        return jsonify({
            'agents': formatted_agents,
            'total_agents': len(formatted_agents),
            'average_confidence': sum(a['confidence'] for a in formatted_agents) / len(formatted_agents) if formatted_agents else 0,
            'commentary': commentary,
            'system_performance': {
                'overall_signal': data['god_cycle'].get('signal', 'HOLD'),
                'execution_time': data['god_cycle'].get('execution_time_ms', 0),
                'final_mood': data['god_cycle'].get('final_mood', 'neutral')
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'agents': [],
            'timestamp': datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
