from datetime import datetime
from typing import Dict, Any, List

from db import get_session
from models import Order, Portfolio, PortfolioPosition
from memecoin_service import simulate_trade


def get_default_portfolio_id(session) -> int:
    """Get or create the default paper portfolio."""
    default_portfolio = session.query(Portfolio).filter_by(name='Default Paper Portfolio').first()
    if not default_portfolio:
        default_portfolio = Portfolio(
            name='Default Paper Portfolio',
            risk_profile='moderate',
            initial_capital=100000.0,
            current_value=100000.0
        )
        session.add(default_portfolio)
        session.commit()
    return default_portfolio.id


def create_order(symbol: str, usd: float) -> Dict[str, Any]:
    session = get_session()
    try:
        # simulate execution (paper)
        exec_res = simulate_trade(symbol, usd)
        price = exec_res.get('price')
        quantity = exec_res.get('quantity')

        # Fix: Ensure a portfolio exists and assign it
        # In a real app, this would come from the user's session or request
        portfolio_id = get_default_portfolio_id(session)

        o = Order(
            portfolio_id=portfolio_id,
            symbol=symbol.upper(),
            usd=usd,
            quantity=quantity,
            price=price,
            status='filled',
            executed_at=datetime.utcnow(),
            meta={'simulated': True}
        )
        session.add(o)
        session.commit()
        return o.to_dict()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def list_orders(limit: int = 100) -> List[Dict[str, Any]]:
    session = get_session()
    try:
        items = session.query(Order).order_by(Order.created_at.desc()).limit(limit).all()
        return [i.to_dict() for i in items]
    finally:
        session.close()


def get_order(order_id: int) -> Dict[str, Any] | None:
    session = get_session()
    try:
        o = session.query(Order).get(order_id)
        return o.to_dict() if o else None
    finally:
        session.close()
