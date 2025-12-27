import services.market_data_service_v2 as msvc
from services.market_data_service_v2 import MarketDataConfig, MarketDataService


class DummyResp:
    def __init__(self, status_code=200, json_data=None, text=''):
        self.status_code = status_code
        self._json = json_data
        self.text = text

    @property
    def ok(self):
        return 200 <= self.status_code < 300

    def json(self):
        return self._json

    def raise_for_status(self):
        if not self.ok:
            raise Exception(f"HTTP {self.status_code}: {self.text}")


def test_fmp_v4_fallback(monkeypatch):
    # First call: v3 returns 403 legacy
    # Second call: v4 returns valid list
    responses = [
        DummyResp(status_code=403, json_data={"Error Message": "Legacy Endpoint ..."}, text='Legacy Endpoint'),
        DummyResp(status_code=200, json_data=[{"symbol": "AAPL", "price": 150.12}])
    ]

    def fake_get(url, params=None, timeout=10):
        return responses.pop(0)

    monkeypatch.setattr(msvc.requests, 'get', fake_get)

    cfg = MarketDataConfig(fmp_api_key='testkey')
    s = MarketDataService(cfg)
    res = s.get_stock_price('AAPL')

    assert res['symbol'] == 'AAPL'
    assert res['price'] == round(150.12, 2)
