import hashlib

import pytest

from backend.services.fyers_broker import (
    FyersBroker,
    FyersConfigurationError,
    FyersLiveTradingDisabled,
    FyersOrderRequest,
)


class FakeFyersClient:
    def __init__(self):
        self.calls = []

    def quotes(self, payload):
        self.calls.append(("quotes", payload))
        return {"s": "ok", "d": [{"symbol": payload["symbols"]}]}

    def history(self, payload):
        self.calls.append(("history", payload))
        return {"s": "ok", "candles": []}

    def place_order(self, payload):
        self.calls.append(("place_order", payload))
        return {"s": "ok", "id": "TEST-ORDER"}


def test_fyers_configuration_status():
    broker = FyersBroker(client_id="APP-200", access_token="token")
    assert broker.is_configured
    assert not broker.is_live_enabled


def test_fyers_login_url_and_app_hash():
    broker = FyersBroker(
        client_id="APP-200",
        secret_id="secret",
        redirect_uri="https://example.com/callback",
    )
    assert broker.build_login_url("state-1").startswith(
        "https://api-t1.fyers.in/api/v3/generate-authcode?"
    )
    assert broker.build_login_url("state-1").count("client_id=APP-200") == 1
    expected = hashlib.sha256(b"APP-200:secret").hexdigest()
    assert broker.build_app_id_hash() == expected


def test_fyers_quote_and_history_use_expected_payloads():
    client = FakeFyersClient()
    broker = FyersBroker(client_id="APP-200", access_token="token", client=client)

    quote = broker.get_quotes("NSE:TCS-EQ")
    history = broker.get_history(
        "NSE:TCS-EQ", "D", "1700000000", "1701000000"
    )

    assert quote["s"] == "ok"
    assert history["s"] == "ok"
    assert client.calls == [
        ("quotes", {"symbols": "NSE:TCS-EQ"}),
        (
            "history",
            {
                "symbol": "NSE:TCS-EQ",
                "resolution": "D",
                "date_format": "0",
                "range_from": "1700000000",
                "range_to": "1701000000",
                "cont_flag": "1",
            },
        ),
    ]


def test_fyers_order_payload_and_live_guard():
    request = FyersOrderRequest(symbol="NSE:TCS-EQ", qty=10, side=1)
    assert request.to_payload() == {
        "symbol": "NSE:TCS-EQ",
        "qty": 10,
        "type": 2,
        "side": 1,
        "productType": "CNC",
        "limitPrice": 0,
        "stopPrice": 0,
        "validity": "DAY",
        "disclosedQty": 0,
        "offlineOrder": False,
        "stopLoss": 0,
        "takeProfit": 0,
    }

    broker = FyersBroker(
        client_id="APP-200",
        access_token="token",
        client=FakeFyersClient(),
        live_trading=False,
    )
    with pytest.raises(FyersLiveTradingDisabled):
        broker.place_order(request)


def test_fyers_order_rejects_invalid_quantity_and_side():
    with pytest.raises(ValueError):
        FyersOrderRequest(symbol="NSE:TCS-EQ", qty=0, side=1).to_payload()
    with pytest.raises(ValueError):
        FyersOrderRequest(symbol="NSE:TCS-EQ", qty=1, side=0).to_payload()


def test_fyers_requires_credentials_for_authenticated_calls():
    broker = FyersBroker()
    with pytest.raises(FyersConfigurationError):
        broker.get_profile()
