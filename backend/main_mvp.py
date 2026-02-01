"""
YANTRAX MVP Backend - Clean, Focused, Production-Ready
v6.0 - Portfolio Creation + AI Debate + Paper Trading Foundation
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from functools import wraps

# ==================== SETUP ====================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
except ImportError:
    logger.warning("python-dotenv not installed, relying on environment variables")

# ==================== FLASK SETUP ====================
from flask import Flask, jsonify, request, Response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ==================== DATABASE SETUP ====================
sys.path.insert(0, os.path.dirname(__file__))

try:
    from db import get_session, init_db
    from models import Portfolio, PortfolioPosition, StrategyProfile, Strategy, User, JournalEntry
    init_db()  # Initialize database on startup
    logger.info("✓ Database initialized")
except Exception as e:
    logger.error(f"✗ Database initialization failed: {e}")
    sys.exit(1)

# ==================== MARKET DATA SERVICE ====================
try:
    from services.market_data_service_waterfall import WaterfallMarketDataService
    market_provider = WaterfallMarketDataService()
    logger.info("✓ Market data service initialized")
except Exception as e:
    logger.error(f"✗ Market data service failed: {e}")
    market_provider = None

# ==================== AI FIRM SETUP ====================
try:
    from ai_firm.agent_manager import AgentManager
    from ai_firm.debate_engine import DebateEngine
    from ai_firm.memory_system import FirmMemorySystem
    
    agent_manager = AgentManager()
    memory_system = FirmMemorySystem()
    debate_engine = DebateEngine(agent_manager)
    
    logger.info(f"✓ AI Firm initialized with {len(agent_manager.agents)} agents")
    AI_FIRM_READY = True
except Exception as e:
    logger.warning(f"⚠ AI Firm initialization warning: {e}")
    # Don't fail - MVP can work without full AI Firm
    AI_FIRM_READY = False

# ==================== HEALTH CHECK ====================

@app.route('/', methods=['GET'])
def health_check():
    """Root endpoint with system status"""
    return jsonify({
        'status': 'online',
        'version': '6.0',
        'timestamp': datetime.now().isoformat(),
        'components': {
            'database': 'ok',
            'market_data': 'ok' if market_provider else 'offline',
            'ai_firm': 'ok' if AI_FIRM_READY else 'offline'
        }
    }), 200


# ==================== PORTFOLIO API ====================

@app.route('/api/portfolio/create', methods=['POST'])
def create_portfolio():
    """
    Create a new portfolio with risk profile and initial capital
    
    POST /api/portfolio/create
    {
        "name": "My Investment Portfolio",
        "risk_profile": "moderate",  # conservative, moderate, aggressive, custom
        "initial_capital": 50000,
        "strategy_preference": "balanced"  # optional
    }
    """
    try:
        data = request.get_json() or {}
        
        # Validate required fields
        name = data.get('name', 'My Portfolio')
        risk_profile = data.get('risk_profile', 'moderate').lower()
        initial_capital = float(data.get('initial_capital', 50000))
        
        # Validate inputs
        if not name:
            return jsonify({'error': 'Portfolio name is required'}), 400
        if risk_profile not in ['conservative', 'moderate', 'aggressive', 'custom']:
            return jsonify({'error': 'Invalid risk profile'}), 400
        if initial_capital <= 0:
            return jsonify({'error': 'Initial capital must be positive'}), 400
        
        # Create portfolio in database
        session = get_session()
        try:
            portfolio = Portfolio(
                name=name,
                risk_profile=risk_profile,
                initial_capital=initial_capital,
                current_value=initial_capital,
                meta={
                    'created_via': 'api',
                    'strategy_preference': data.get('strategy_preference', 'balanced')
                }
            )
            session.add(portfolio)
            session.commit()
            
            logger.info(f"✓ Portfolio created: {name} (${initial_capital})")
            
            return jsonify({
                'success': True,
                'portfolio': portfolio.to_dict(),
                'message': 'Portfolio created successfully'
            }), 201
            
        finally:
            session.close()
            
    except ValueError as e:
        return jsonify({'error': f'Invalid input: {str(e)}'}), 400
    except Exception as e:
        logger.error(f"✗ Portfolio creation failed: {e}")
        return jsonify({'error': 'Failed to create portfolio'}), 500


@app.route('/api/portfolio/<int:portfolio_id>', methods=['GET'])
def get_portfolio(portfolio_id: int):
    """Get portfolio details by ID"""
    session = get_session()
    try:
        portfolio = session.query(Portfolio).get(portfolio_id)
        if not portfolio:
            return jsonify({'error': 'Portfolio not found'}), 404
        
        return jsonify({
            'portfolio': portfolio.to_dict()
        }), 200
    finally:
        session.close()


@app.route('/api/portfolios', methods=['GET'])
def list_portfolios():
    """List all portfolios (pagination support)"""
    session = get_session()
    try:
        limit = int(request.args.get('limit', 20))
        offset = int(request.args.get('offset', 0))
        
        portfolios = session.query(Portfolio).limit(limit).offset(offset).all()
        total = session.query(Portfolio).count()
        
        return jsonify({
            'portfolios': [p.to_dict() for p in portfolios],
            'total': total,
            'limit': limit,
            'offset': offset
        }), 200
    finally:
        session.close()


# ==================== MARKET DATA API ====================

@app.route('/api/market-price', methods=['GET'])
def get_market_price():
    """
    Get current market price for a symbol
    
    GET /api/market-price?symbol=AAPL
    """
    symbol = request.args.get('symbol', '').upper()
    
    if not symbol:
        return jsonify({'error': 'symbol parameter required'}), 400
    
    if not market_provider:
        return jsonify({'error': 'Market data service unavailable'}), 503
    
    try:
        price_data = market_provider.get_price(symbol)
        return jsonify(price_data), 200
    except Exception as e:
        logger.error(f"✗ Failed to get price for {symbol}: {e}")
        return jsonify({'error': f'Failed to fetch price for {symbol}'}), 500


@app.route('/api/market-search', methods=['GET'])
def search_market():
    """
    Search for symbols and market data
    
    GET /api/market-search?query=APPLE&limit=5
    """
    query = request.args.get('query', '').upper()
    limit = int(request.args.get('limit', 5))
    
    if not query or len(query) < 1:
        return jsonify({'error': 'query parameter required'}), 400
    
    # TODO: Implement symbol search via market data service
    # For now, return mock data
    mock_results = [
        {'symbol': 'AAPL', 'name': 'Apple Inc.', 'type': 'stock'},
        {'symbol': 'MSFT', 'name': 'Microsoft Corporation', 'type': 'stock'},
    ]
    
    return jsonify({
        'results': mock_results[:limit],
        'query': query
    }), 200


# ==================== AI DEBATE / COUNCIL API ====================

@app.route('/api/strategy/ai-debate', methods=['POST'])
def ai_debate():
    """
    Trigger AI council debate on a symbol
    
    POST /api/strategy/ai-debate
    {
        "symbol": "AAPL",
        "context": {
            "price": 175.50,
            "market_cap": 2500000000000,
            "pe_ratio": 28.5,
            ...
        }
    }
    
    Response:
    {
        "debate_id": "...",
        "symbol": "AAPL",
        "arguments": [
            {
                "agent": "Warren",
                "signal": "BUY",
                "reasoning": "...",
                "confidence": 0.85,
                "quote": "..."
            },
            ...
        ],
        "winning_signal": "BUY",
        "consensus_score": 0.73
    }
    """
    if not AI_FIRM_READY:
        return jsonify({'error': 'AI Firm not initialized'}), 503
    
    try:
        data = request.get_json() or {}
        symbol = data.get('symbol', '').upper()
        context = data.get('context', {})
        
        if not symbol:
            return jsonify({'error': 'symbol required'}), 400
        
        # Run debate
        debate_result = debate_engine.conduct_debate(symbol, context)
        
        return jsonify(debate_result), 200
    except Exception as e:
        logger.error(f"✗ AI debate failed: {e}")
        return jsonify({'error': 'Debate failed'}), 500


@app.route('/api/ai-firm/status', methods=['GET'])
def ai_firm_status():
    """Get AI firm system status"""
    if not AI_FIRM_READY:
        return jsonify({'error': 'AI Firm offline'}), 503
    
    try:
        return jsonify({
            'status': 'online',
            'total_agents': len(agent_manager.agents),
            'departments': list(agent_manager.departments.keys()),
            'memory_items': memory_system.get_total_memories(),
            'last_debate': debate_engine.debate_history[-1] if debate_engine.debate_history else None
        }), 200
    except Exception as e:
        logger.error(f"✗ Status check failed: {e}")
        return jsonify({'error': 'Status check failed'}), 500


# ==================== PAPER TRADING API ====================

@app.route('/api/portfolio/<int:portfolio_id>/trade', methods=['POST'])
def execute_trade(portfolio_id: int):
    """
    Execute a paper trade (BUY/SELL simulation)
    
    POST /api/portfolio/{portfolio_id}/trade
    {
        "action": "BUY",  # or "SELL"
        "symbol": "AAPL",
        "quantity": 10,
        "price": 175.50,
        "reasoning": "AI consensus BUY"
    }
    """
    session = get_session()
    try:
        portfolio = session.query(Portfolio).get(portfolio_id)
        if not portfolio:
            return jsonify({'error': 'Portfolio not found'}), 404
        
        data = request.get_json() or {}
        action = data.get('action', '').upper()
        symbol = data.get('symbol', '').upper()
        quantity = float(data.get('quantity', 0))
        price = float(data.get('price', 0))
        
        # Validate
        if action not in ['BUY', 'SELL']:
            return jsonify({'error': 'action must be BUY or SELL'}), 400
        if not symbol or quantity <= 0 or price <= 0:
            return jsonify({'error': 'Invalid parameters'}), 400
        
        total_value = quantity * price
        
        # Execute trade
        if action == 'BUY':
            if portfolio.current_value < total_value:
                return jsonify({'error': 'Insufficient capital'}), 400
            
            portfolio.current_value -= total_value
            position = session.query(PortfolioPosition).filter_by(
                portfolio_id=portfolio_id, symbol=symbol
            ).first()
            
            if position:
                position.quantity += quantity
                position.avg_price = (position.avg_price * (position.quantity - quantity) + price * quantity) / position.quantity
            else:
                position = PortfolioPosition(
                    portfolio_id=portfolio_id,
                    symbol=symbol,
                    quantity=quantity,
                    avg_price=price
                )
                session.add(position)
        
        elif action == 'SELL':
            position = session.query(PortfolioPosition).filter_by(
                portfolio_id=portfolio_id, symbol=symbol
            ).first()
            
            if not position or position.quantity < quantity:
                return jsonify({'error': 'Insufficient position to sell'}), 400
            
            position.quantity -= quantity
            portfolio.current_value += total_value
            
            if position.quantity == 0:
                session.delete(position)
        
        # Log trade to journal
        journal_entry = JournalEntry(
            action=action,
            reward=total_value if action == 'SELL' else -total_value,
            balance=portfolio.current_value,
            notes=f"{action} {quantity} {symbol} @ ${price} - {data.get('reasoning', 'Manual trade')}"
        )
        session.add(journal_entry)
        session.commit()
        
        logger.info(f"✓ Trade executed: {action} {quantity} {symbol} @ ${price}")
        
        return jsonify({
            'success': True,
            'trade': {
                'action': action,
                'symbol': symbol,
                'quantity': quantity,
                'price': price,
                'total_value': total_value,
                'timestamp': datetime.now().isoformat()
            },
            'portfolio_value': portfolio.current_value
        }), 200
        
    except Exception as e:
        session.rollback()
        logger.error(f"✗ Trade failed: {e}")
        return jsonify({'error': 'Trade execution failed'}), 500
    finally:
        session.close()


# ==================== JOURNAL API ====================

@app.route('/api/journal', methods=['GET'])
def get_journal():
    """Get trading journal entries"""
    session = get_session()
    try:
        limit = int(request.args.get('limit', 50))
        entries = session.query(JournalEntry).order_by(JournalEntry.timestamp.desc()).limit(limit).all()
        
        return jsonify({
            'entries': [e.to_dict() for e in entries],
            'total': len(entries)
        }), 200
    finally:
        session.close()


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500


# ==================== STARTUP ====================

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV', 'production') == 'development'
    
    logger.info("\n" + "="*60)
    logger.info("🚀 YANTRAX MVP v6.0 Starting")
    logger.info("="*60)
    logger.info(f"Port: {port}")
    logger.info(f"Debug: {debug}")
    logger.info(f"AI Firm: {'✓ Online' if AI_FIRM_READY else '✗ Offline'}")
    logger.info("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
