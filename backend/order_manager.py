from datetime import datetime
from typing import Dict, Any, List

from backend.db import get_session
from backend.models import Order, Portfolio
from backend.memecoin_service import simulate_trade


def create_order(symbol: str, usd: float, price: float = None) -> Dict[str, Any]:
    """Create a paper order.

    price: explicit market price (canonical pipeline passes the verified
    snapshot price). When omitted, falls back to the legacy memecoin
    paper-simulation fill — SYNTHETIC, only acceptable for the memecoin
    prototype API surface, never for canonical equity decisions.
    """
    session = get_session()
    try:
        if price and price > 0:
            quantity = usd / price
        else:
            # Legacy synthetic paper fill (memecoin prototype surface only)
            exec_res = simulate_trade(symbol, usd)
            price = exec_res.get('price')
            quantity = exec_res.get('quantity')

        # Ensure a portfolio exists
        from backend.models import Portfolio
        portfolio = session.query(Portfolio).filter_by(name="Default Paper Portfolio").first()
        if not portfolio:
            portfolio = Portfolio(
                name="Default Paper Portfolio",
                owner_id=1,
                risk_profile="moderate",
                current_value=100000.0,
            )
            session.add(portfolio)
            session.commit()
            session.refresh(portfolio)

        o = Order(
            portfolio_id=portfolio.id,
            symbol=symbol.upper(),
            usd=usd,
            quantity=quantity,
            price=price,
            status='filled',
            executed_at=datetime.utcnow(),
            meta={'simulated': True},
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
