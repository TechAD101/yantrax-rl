"""YantraX heartbeat module — production health contract.

States:  HEALTHY | DEGRADED | UNHEALTHY | DEPENDENCY_FAILURE

The module never exposes secrets.  Each sub-check returns
(status, detail_dict).  The aggregate heartbeat is the minimum
of all sub-check statuses.
"""

from __future__ import annotations

import os
import time
import logging
from datetime import datetime, timezone
from typing import Any, Dict

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# State ordering (lower is worse)
# ---------------------------------------------------------------------------
_STATUS_ORDER = {
    'DEPENDENCY_FAILURE': 0,
    'UNHEALTHY': 1,
    'DEGRADED': 2,
    'HEALTHY': 3,
}


def _worst(*statuses: str) -> str:
    return min(statuses, key=lambda s: _STATUS_ORDER.get(s, -1))


# ---------------------------------------------------------------------------
# Global runtime state — mutated by god-cycle / pipeline
# ---------------------------------------------------------------------------
_heartbeat_state: Dict[str, Any] = {
    'start_time': time.time(),
    'last_pipeline_run': None,
    'last_pipeline_status': None,
    'last_pipeline_error': None,
    'last_error': None,
    'last_error_timestamp': None,
    'last_db_check': None,
    'last_db_status': None,
    'last_market_check': None,
    'last_market_status': None,
}


def record_pipeline_run(status: str, error: str | None = None) -> None:
    """Call after each god-cycle / decision-pipeline run."""
    ts = datetime.now(timezone.utc).isoformat()
    _heartbeat_state['last_pipeline_run'] = ts
    _heartbeat_state['last_pipeline_status'] = status
    if error:
        _heartbeat_state['last_pipeline_error'] = error
        _heartbeat_state['last_error'] = error
        _heartbeat_state['last_error_timestamp'] = ts


def record_error(error: str) -> None:
    """Record an unexpected error visible to /heartbeat."""
    ts = datetime.now(timezone.utc).isoformat()
    _heartbeat_state['last_error'] = error
    _heartbeat_state['last_error_timestamp'] = ts


# ---------------------------------------------------------------------------
# Individual health checks
# ---------------------------------------------------------------------------

def check_process() -> tuple[str, dict]:
    """Always HEALTHY — if we can call this, the process is alive."""
    uptime = time.time() - _heartbeat_state['start_time']
    return 'HEALTHY', {
        'uptime_seconds': round(uptime, 1),
        'start_time': datetime.fromtimestamp(
            _heartbeat_state['start_time'], tz=timezone.utc
        ).isoformat(),
    }


def check_database() -> tuple[str, dict]:
    """Verify the configured DB is reachable and basic queries work."""
    ts = datetime.now(timezone.utc).isoformat()
    _heartbeat_state['last_db_check'] = ts
    try:
        from backend.db import get_session
        from backend.models import JournalEntry
        from sqlalchemy import func as sa_func

        session = get_session()
        # Lightweight read: count journal entries
        cnt = session.query(sa_func.count(JournalEntry.id)).scalar()
        result = {'tables_accessible': True, 'journal_entries': cnt}
        _heartbeat_state['last_db_status'] = 'ok'
        return 'HEALTHY', result
    except Exception as exc:
        logger.error('Heartbeat DB check failed: %s', exc)
        _heartbeat_state['last_db_status'] = str(exc)
        return 'DEGRADED', {'error': str(exc)}


def check_market_data() -> tuple[str, dict]:
    """Check whether any market-data provider is configured."""
    ts = datetime.now(timezone.utc).isoformat()
    _heartbeat_state['last_market_check'] = ts
    try:
        from backend.config import Config
        has_api = bool(Config.MARKET_DATA_API_KEY)
        return 'HEALTHY' if has_api else 'DEGRADED', {
            'configured': has_api,
            'note': 'Market data provider not configured — decisions will ABSTAIN'
            if not has_api else 'Market data provider configured',
        }
    except Exception as exc:
        _heartbeat_state['last_market_status'] = str(exc)
        return 'DEPENDENCY_FAILURE', {'error': str(exc)}


def check_pipeline() -> tuple[str, dict]:
    """Report last pipeline run info — no live call."""
    last_run = _heartbeat_state.get('last_pipeline_run')
    if last_run is None:
        return 'HEALTHY', {
            'last_run': None,
            'note': 'No pipeline runs yet — system is idle',
        }
    return 'HEALTHY', {
        'last_run': last_run,
        'last_status': _heartbeat_state.get('last_pipeline_status'),
        'last_error': _heartbeat_state.get('last_pipeline_error'),
    }


# ---------------------------------------------------------------------------
# Aggregate heartbeat
# ---------------------------------------------------------------------------

def build_heartbeat() -> tuple[str, dict]:
    """Build a full machine-readable heartbeat payload."""
    from backend.config import Config

    checks = {
        'process': check_process(),
        'database': check_database(),
        'market_data': check_market_data(),
        'pipeline': check_pipeline(),
    }

    statuses = [c[0] for c in checks.values()]
    overall = _worst(*statuses)

    # Last error info
    last_error = _heartbeat_state.get('last_error')
    if last_error:
        overall = _worst(overall, 'DEGRADED')

    payload: Dict[str, Any] = {
        'status': overall,
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'service': 'yantrax-rl-backend',
        'version': Config.VERSION,
        'commit': _git_short(),
        'checks': {name: info for name, (_, info) in checks.items()},
    }

    if last_error:
        payload['last_error'] = last_error
        payload['last_error_timestamp'] = _heartbeat_state.get(
            'last_error_timestamp'
        )

    return overall, payload


def _git_short() -> str:
    try:
        import subprocess
        return subprocess.check_output(
            ['git', 'rev-parse', '--short', 'HEAD'],
            text=True, stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return 'unknown'


# ---------------------------------------------------------------------------
# Flask blue-print (register at import)
# ---------------------------------------------------------------------------

from flask import Blueprint, jsonify

heartbeat_bp = Blueprint('heartbeat', __name__)


@heartbeat_bp.route('/heartbeat', methods=['GET'])
def heartbeat_endpoint():
    """Production health contract — never returns fabricated health."""
    status, payload = build_heartbeat()
    code = 200 if status in ('HEALTHY', 'DEGRADED') else 503
    return jsonify(payload), code
