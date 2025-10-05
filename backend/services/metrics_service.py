"""
services/metrics_service.py

Simple Prometheus metrics helper.
"""
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from prometheus_client import CollectorRegistry
from typing import Dict

registry = CollectorRegistry()

request_counter = Counter('yantrax_requests_total', 'Total HTTP requests', ['endpoint', 'method', 'status'], registry=registry)
agent_latency = Histogram('yantrax_agent_latency_seconds', 'Agent processing latency seconds', ['agent'], registry=registry)
cb_state_changes = Counter('yantrax_cb_state_changes_total', 'Circuit breaker state changes', ['key', 'state'], registry=registry)

def metrics_app(environ, start_response):
    data = generate_latest(registry)
    start_response('200 OK', [('Content-Type', CONTENT_TYPE_LATEST)])
    return [data]

def get_metrics_text() -> bytes:
    return generate_latest(registry)
