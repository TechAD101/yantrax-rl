"""FYERS API v3 broker adapter.

This module is intentionally isolated from the canonical paper-order path.
Live order placement requires both configured FYERS credentials and the explicit
FYERS_LIVE_TRADING=true flag.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any, Dict, Optional
from urllib.parse import urlencode

from backend.config import Config


class FyersConfigurationError(RuntimeError):
    """Raised when FYERS credentials or runtime configuration are incomplete."""


class FyersLiveTradingDisabled(RuntimeError):
    """Raised when a live order is requested while live trading is disabled."""


@dataclass(frozen=True)
class FyersOrderRequest:
    """Canonical request used to construct a FYERS single-order payload."""

    symbol: str
    qty: int
    side: int
    product_type: str = "CNC"
    order_type: int = 2
    limit_price: float = 0
    stop_price: float = 0
    validity: str = "DAY"
    disclosed_qty: int = 0
    offline_order: bool = False
    stop_loss: float = 0
    take_profit: float = 0

    def to_payload(self) -> Dict[str, Any]:
        if not self.symbol:
            raise ValueError("FYERS symbol is required")
        if self.qty <= 0:
            raise ValueError("FYERS quantity must be greater than zero")
        if self.side not in (-1, 1):
            raise ValueError("FYERS side must be -1 (sell) or 1 (buy)")

        return {
            "symbol": self.symbol,
            "qty": self.qty,
            "type": self.order_type,
            "side": self.side,
            "productType": self.product_type,
            "limitPrice": self.limit_price,
            "stopPrice": self.stop_price,
            "validity": self.validity,
            "disclosedQty": self.disclosed_qty,
            "offlineOrder": bool(self.offline_order),
            "stopLoss": self.stop_loss,
            "takeProfit": self.take_profit,
        }


class FyersBroker:
    """Thin adapter around the official FYERS Python SDK.

    The SDK import is lazy so test environments and paper-only deployments can
    import Yantra X without requiring the optional FYERS package or credentials.
    """

    def __init__(
        self,
        *,
        client_id: Optional[str] = None,
        secret_id: Optional[str] = None,
        redirect_uri: Optional[str] = None,
        access_token: Optional[str] = None,
        live_trading: Optional[bool] = None,
        client: Any = None,
    ):
        self.client_id = client_id if client_id is not None else Config.FYERS_APP_ID
        self.secret_id = secret_id if secret_id is not None else Config.FYERS_SECRET_ID
        self.redirect_uri = redirect_uri if redirect_uri is not None else Config.FYERS_REDIRECT_URI
        self.access_token = access_token if access_token is not None else Config.FYERS_ACCESS_TOKEN
        self.live_trading = Config.FYERS_LIVE_TRADING if live_trading is None else live_trading
        self._client = client

    @property
    def is_configured(self) -> bool:
        return bool(self.client_id and self.access_token)

    @property
    def is_live_enabled(self) -> bool:
        return bool(self.live_trading and self.is_configured)

    def require_authenticated(self) -> None:
        if not self.is_configured:
            raise FyersConfigurationError(
                "FYERS_APP_ID and FYERS_ACCESS_TOKEN are required for authenticated API use"
            )

    def require_live_trading(self) -> None:
        self.require_authenticated()
        if not self.live_trading:
            raise FyersLiveTradingDisabled(
                "FYERS live trading is disabled; set FYERS_LIVE_TRADING=true explicitly"
            )

    def build_login_url(self, state: str = "yantrax") -> str:
        if not self.client_id or not self.redirect_uri:
            raise FyersConfigurationError(
                "FYERS_APP_ID and FYERS_REDIRECT_URI are required to build the login URL"
            )
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "state": state,
        }
        return "https://api-t1.fyers.in/api/v3/generate-authcode?" + urlencode(params)

    def build_app_id_hash(self) -> str:
        if not self.client_id or not self.secret_id:
            raise FyersConfigurationError(
                "FYERS_APP_ID and FYERS_SECRET_ID are required for auth-code validation"
            )
        return hashlib.sha256(f"{self.client_id}:{self.secret_id}".encode()).hexdigest()

    def validate_auth_code(self, auth_code: str) -> Dict[str, Any]:
        if not auth_code:
            raise ValueError("auth_code is required")
        if not self.client_id or not self.secret_id:
            raise FyersConfigurationError(
                "FYERS_APP_ID and FYERS_SECRET_ID are required for auth-code validation"
            )

        from fyers_apiv3 import fyersModel

        session = fyersModel.SessionModel(
            client_id=self.client_id,
            secret_key=self.secret_id,
            redirect_uri=self.redirect_uri,
            response_type="code",
            grant_type="authorization_code",
        )
        session.set_token(auth_code)
        return session.generate_token()

    def _client_or_create(self) -> Any:
        self.require_authenticated()
        if self._client is not None:
            return self._client

        from fyers_apiv3 import fyersModel

        self._client = fyersModel.FyersModel(
            client_id=self.client_id,
            token=self.access_token,
            is_async=False,
            log_path="",
        )
        return self._client

    def get_profile(self) -> Dict[str, Any]:
        return self._client_or_create().get_profile()

    def get_funds(self) -> Dict[str, Any]:
        return self._client_or_create().funds()

    def get_holdings(self) -> Dict[str, Any]:
        return self._client_or_create().holdings()

    def get_positions(self) -> Dict[str, Any]:
        return self._client_or_create().positions()

    def get_orderbook(self) -> Dict[str, Any]:
        return self._client_or_create().orderbook()

    def get_quotes(self, symbol: str) -> Dict[str, Any]:
        if not symbol:
            raise ValueError("FYERS symbol is required")
        return self._client_or_create().quotes({"symbols": symbol})

    def get_history(
        self,
        symbol: str,
        resolution: str,
        range_from: str,
        range_to: str,
        date_format: str = "0",
        cont_flag: str = "1",
    ) -> Dict[str, Any]:
        if not symbol:
            raise ValueError("FYERS symbol is required")
        payload = {
            "symbol": symbol,
            "resolution": resolution,
            "date_format": date_format,
            "range_from": range_from,
            "range_to": range_to,
            "cont_flag": cont_flag,
        }
        return self._client_or_create().history(payload)

    def place_order(self, request: FyersOrderRequest) -> Dict[str, Any]:
        """Place a live FYERS order only after explicit live enablement."""
        self.require_live_trading()
        return self._client_or_create().place_order(request.to_payload())
