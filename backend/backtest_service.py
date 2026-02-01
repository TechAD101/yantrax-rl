"""Backtester service - simulate strategy performance on historical data"""
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any

from db import get_session
from models import Strategy

# Optional KB service - graceful fallback if chromadb not available
try:
    from services.knowledge_base_service import kb_service
    KB_AVAILABLE = True
except ImportError:
    KB_AVAILABLE = False
    kb_service = None


def generate_price_history(symbol: str, days: int = 30) -> List[Dict[str, Any]]:
    """Simulate historical price data"""
    prices = []
    base_price = random.uniform(50, 500)
    for i in range(days):
        date = datetime.now() - timedelta(days=days - i)
        daily_change = random.uniform(-0.05, 0.05)
        base_price *= (1 + daily_change)
        prices.append({
            'date': date.isoformat(),
            'open': round(base_price * 0.98, 2),
            'close': round(base_price, 2),
            'high': round(base_price * 1.02, 2),
            'low': round(base_price * 0.96, 2),
            'volume': random.randint(1000000, 10000000)
        })
    return prices


def backtest_strategy(strategy_id: int, symbol: str = 'AAPL', days: int = 30, initial_capital: float = 100000) -> Dict[str, Any]:
    """Run backtest simulation for a strategy"""
    session = get_session()
    try:
        strategy = session.query(Strategy).get(strategy_id)
        if not strategy:
            raise ValueError(f"Strategy {strategy_id} not found")
        
        prices = generate_price_history(symbol, days)
        
        # Simulate trading logic: random buy/hold/sell for prototype
        trades = []
        balance = initial_capital
        position = 0
        entry_price = None
        
        for i, bar in enumerate(prices):
            signal = random.choice(['buy', 'hold', 'sell'])
            close_price = bar['close']
            
            if signal == 'buy' and position == 0:
                qty = (balance * 0.8) / close_price
                position = qty
                entry_price = close_price
                trades.append({'action': 'BUY', 'price': close_price, 'qty': qty, 'date': bar['date']})
                balance -= qty * close_price
            elif signal == 'sell' and position > 0:
                balance += position * close_price
                pnl = (close_price - entry_price) * position
                trades.append({'action': 'SELL', 'price': close_price, 'qty': position, 'pnl': pnl, 'date': bar['date']})
                position = 0
            
        # Calculate metrics
        final_value = balance + (position * prices[-1]['close'] if position > 0 else 0)
        total_return = ((final_value - initial_capital) / initial_capital) * 100
        win_count = len([t for t in trades if t.get('pnl', 0) > 0])
        total_trades = len([t for t in trades if t['action'] == 'SELL'])
        win_rate = (win_count / total_trades * 100) if total_trades > 0 else 0
        
        backtest_result = {
            'strategy_id': strategy_id,
            'symbol': symbol,
            'initial_capital': initial_capital,
            'final_value': round(final_value, 2),
            'total_return': round(total_return, 2),
            'win_rate': round(win_rate, 2),
            'total_trades': total_trades,
            'trades': trades,
            'backtest_date': datetime.now().isoformat()
        }
        
        # Log to KB for feedback learning (optional)
        if KB_AVAILABLE and kb_service:
            kb_service.add_document(
                f"Backtest: {strategy.name} on {symbol}",
                f"Return: {total_return}%, Win Rate: {win_rate}%, Trades: {total_trades}",
                {'strategy_id': strategy_id, 'symbol': symbol, 'return': total_return}
            )
        
        return backtest_result
    finally:
        session.close()


def list_backtest_results(limit: int = 10) -> List[Dict[str, Any]]:
    """List recent backtest results from KB"""
    try:
        results = kb_service.search("backtest", limit=limit)
        return results
    except Exception as e:
        return {'error': str(e)}
