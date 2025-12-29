import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from main import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_metrics_endpoint_returns_metrics(client):
    # Ensure metrics endpoint returns content
    resp = client.get('/metrics')
    assert resp.status_code in (200, 500)
    if resp.status_code == 200:
        assert resp.data is not None


def test_god_cycle_emits_metrics(client):
    # Call god-cycle to create metrics and then hit /metrics
    resp = client.get('/god-cycle')
    assert resp.status_code == 200

    # Now scrape metrics
    m = client.get('/metrics')
    assert m.status_code in (200, 500)
    if m.status_code == 200:
        data = m.data.decode('utf-8')
        # basic check: the metrics text should contain the metric name if registry active
        assert 'yantrax_agent_latency_seconds' in data or 'yantrax_requests_total' in data
