from datetime import datetime
from typing import Dict, Any, List, Optional

from db import get_session
from models import Order, Portfolio
from memecoin_service import simulate_trade


def create_order(symbol: str, usd: float, portfolio_id: Optional[int] = None) -> Dict[str, Any]:
    session = get_session()
    try:
        if portfolio_id is None:
            # Fallback to default portfolio
            p = session.query(Portfolio).filter_by(name='Default Paper Portfolio').first()
            if not p:
                p = Portfolio(name='Default Paper Portfolio', initial_capital=100000.0, current_value=100000.0)
                session.add(p)
                session.flush()
            portfolio_id = p.id

        # simulate execution (paper)
        exec_res = simulate_trade(symbol, usd)
        price = exec_res.get('price', 0.0)
        quantity = exec_res.get('quantity', 0.0)

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
    except Exception:
        return []
    finally:
        session.close()


def get_order(order_id: int) -> Dict[str, Any] | None:
    session = get_session()
    try:
        o = session.get(Order, order_id)
        return o.to_dict() if o else None
    except Exception:
        return None
    finally:
        session.close()
