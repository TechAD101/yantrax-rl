import logging
from datetime import datetime
from flask import Blueprint, request, jsonify
import numpy as np

from models import RawMarketData, AuditLog
from db import get_session

logger = logging.getLogger(__name__)

data_ingest_bp = Blueprint('data_ingest', __name__)

def verify_triple_source(instrument: str, metric: str, sources_data: dict, db):
    """
    sources_data: {'fmp': 150.5, 'alpaca': 150.6, 'yfinance': 150.4}
    Returns validation status, fallback level, and trust contribution
    """
    fallback_level = 0
    verification_status = 'ok'
    trust_contrib = 1.0

    values = [float(v) for v in sources_data.values() if v is not None]
    
    if len(values) == 0:
        return 'missing', 5, 0.0

    if len(values) < 3:
        fallback_level += (3 - len(values))
    
    median_val = np.median(values)
    
    max_variance = 0
    if median_val > 0:
        max_variance = max([abs(v - median_val) / median_val for v in values])
    
    if max_variance > 0.005:  # 0.5%
        verification_status = 'variance_flag'
        fallback_level += 1
        trust_contrib -= (max_variance * 10)  # reduce trust
        
    return verification_status, min(int(fallback_level), 5), float(max(0.1, trust_contrib))

@data_ingest_bp.route('/data/ingest', methods=['POST'])
def ingest_data():
    """
    Accepts: {
        "instrument": "AAPL",
        "metric": "price",
        "sources": {
            "fmp": 150.5,
            "alpaca": 150.6,
            "yfinance": 150.4
        },
        "timestamp": "2023-10-27T10:00:00Z"
    }
    """
    data = request.json
    instrument = data.get('instrument')
    metric = data.get('metric')
    sources_data = data.get('sources', {})
    
    if not instrument or not metric or not sources_data:
        return jsonify({'error': 'bad_request', 'message': 'Missing fields'}), 400
        
    db = get_session()
    try:
        # 1. Triple-source verification
        status, level, trust = verify_triple_source(instrument, metric, sources_data, db)
        
        # 2. Pick the primary source or median
        values = [float(v) for v in sources_data.values() if v is not None]
        final_value = np.median(values) if values else None
        
        # 3. Store raw datapoint
        timestamp_str = data.get('timestamp')
        ts = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00")) if timestamp_str else datetime.utcnow()

        raw_data = RawMarketData(
            source=','.join(sources_data.keys()),
            instrument=instrument,
            metric=metric,
            value=float(final_value) if final_value is not None else None,
            timestamp=ts,
            meta=sources_data
        )
        db.add(raw_data)
        db.flush()  # to get raw_data.id
        
        # 4. Store audit log
        audit = AuditLog(
            section='market_data_ingest',
            datapoint_ref=raw_data.id,
            data_age_seconds=0,
            sources=sources_data,
            verification_status=status,
            fallback_level=level,
            trust_contrib=trust
        )
        db.add(audit)
        db.commit()
        
        return jsonify({
            'status': 'success',
            'raw_data_id': raw_data.id,
            'audit_id': audit.id,
            'fallback_level': level,
            'verification_status': status
        }), 201

    except Exception as e:
        db.rollback()
        logger.error(f"Ingest error: {e}")
        return jsonify({'error': 'internal_error', 'message': str(e)}), 500
    finally:
        db.close()

@data_ingest_bp.route('/audit/fallback-status', methods=['GET'])
def get_fallback_status():
    db = get_session()
    try:
        recent_audits = db.query(AuditLog).order_by(AuditLog.id.desc()).limit(50).all()
        if not recent_audits:
            return jsonify({'fallback_level': 0.0, 'status': 'no_data'})
            
        avg_fallback = float(np.mean([a.fallback_level for a in recent_audits]))
        status = 'optimal' if avg_fallback < 1 else 'degraded' if avg_fallback < 3 else 'critical'
        
        return jsonify({
            'fallback_level': round(avg_fallback, 2),
            'status': status,
            'recent_issues': [a.to_dict() for a in recent_audits if a.fallback_level > 0][:5]
        }), 200
    finally:
        db.close()
