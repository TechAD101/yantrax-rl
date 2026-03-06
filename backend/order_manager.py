from datetime import datetime
from typing import Dict, Any, List

from db import get_session
from models import Order
from memecoin_service import simulate_trade


def create_order(symbol: str, usd: float) -> Dict[str, Any]:
    session = get_session()
    try:
        # simulate execution (paper)
        exec_res = simulate_trade(symbol, usd)
        price = exec_res.get('price')
        quantity = exec_res.get('quantity')

        o = Order(symbol=symbol.upper(), usd=usd, quantity=quantity, price=price, status='filled', executed_at=datetime.utcnow(), meta={'simulated': True}, portfolio_id=1)
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
