"""Memecoin Engine prototype

- Scans for memecoin candidates (simulated social + onchain signals)
- Ranks by composite 'degen_score'
- Provides simulation helpers (paper buy/sell) and basic persistence via DB model
"""
import time
import random
from typing import List, Dict, Any

from db import get_session
from models import Memecoin


def generate_candidate(symbol: str) -> Dict[str, Any]:
    # Simulate signals
    social = random.uniform(0, 1000)
    mentions = int(random.expovariate(1/50))
    price = round(random.uniform(0.0001, 5.0), 6)
    momentum = random.uniform(-1.0, 1.0)

    # Composite degen score: weights are arbitrary for prototype
    score = round((mentions * 0.5 + social * 0.3 + max(0, momentum) * 100) / (1 + price), 4)

    return {
        'symbol': symbol.upper(),
        'social': round(social, 2),
        'mentions': mentions,
        'price': price,
        'momentum': round(momentum, 4),
        'degen_score': score,
        'scanned_at': int(time.time())
    }


def scan_market(sample_symbols: List[str]) -> List[Dict[str, Any]]:
    results = []
    for s in sample_symbols:
        results.append(generate_candidate(s))
    # Sort desc by degen_score
    results.sort(key=lambda x: x['degen_score'], reverse=True)

    # Persist top 3 to DB for quick access
    session = get_session()
    try:
        for r in results[:3]:
            # Upsert by symbol
            m = session.query(Memecoin).filter_by(symbol=r['symbol']).first()
            if not m:
                m = Memecoin(symbol=r['symbol'], score=r['degen_score'], meta={'social': r['social'], 'mentions': r['mentions'], 'price': r['price'], 'momentum': r['momentum']})
                session.add(m)
            else:
                m.score = r['degen_score']
                m.meta = {'social': r['social'], 'mentions': r['mentions'], 'price': r['price'], 'momentum': r['momentum']}
        session.commit()
    except Exception:
        session.rollback()
    finally:
        session.close()

    return results


def get_top_memecoins(limit: int = 10) -> List[Dict[str, Any]]:
    session = get_session()
    try:
        items = session.query(Memecoin).order_by(Memecoin.score.desc()).limit(limit).all()
        return [i.to_dict() for i in items]
    finally:
        session.close()


def simulate_trade(symbol: str, usd: float) -> Dict[str, Any]:
    # Simple paper simulation: buy at stored price if present else random
    session = get_session()
    try:
        m = session.query(Memecoin).filter_by(symbol=symbol.upper()).first()
        if m and m.meta and m.meta.get('price'):
            price = m.meta['price']
        else:
            price = round(random.uniform(0.0001, 5.0), 6)
        qty = round(usd / price, 6) if price > 0 else 0
        return {'symbol': symbol.upper(), 'price': price, 'usd': usd, 'quantity': qty}
    finally:
        session.close()
