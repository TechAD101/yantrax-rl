import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class Config:
    """Centralized configuration for YantraX RL"""

    # System Info
    VERSION = "5.23-STABLE"
    ENVIRONMENT = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
    PORT = int(os.getenv('PORT', 5000))

# API Keys - Environment variables required for production
    ALPACA_API_KEY = os.getenv('ALPACA_API_KEY', '')
    ALPACA_SECRET_KEY = os.getenv('ALPACA_SECRET_KEY', '')
    PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY', '')

    # FYERS API v3 configuration. Live trading remains opt-in and disabled by default.
    FYERS_APP_ID = os.getenv('FYERS_APP_ID', '')
    FYERS_SECRET_ID = os.getenv('FYERS_SECRET_ID', '')
    FYERS_REDIRECT_URI = os.getenv('FYERS_REDIRECT_URI', '')
    FYERS_ACCESS_TOKEN = os.getenv('FYERS_ACCESS_TOKEN', '')
    FYERS_LIVE_TRADING = os.getenv('FYERS_LIVE_TRADING', 'false').lower() == 'true'


    # DB Config
    PERSIST_DIR = "chroma_db"

    # Market Data Config
    CACHE_TTL_SECONDS = 60

    FMP_API_KEY = os.getenv('FMP_API_KEY') or os.getenv('FMP_KEY')

    @classmethod
    def get_market_config(cls) -> Dict[str, Any]:
        return {
            'fmp_api_key': cls.FMP_API_KEY,
            'cache_ttl_seconds': cls.CACHE_TTL_SECONDS,
            'rate_limit_calls': 300,
            'rate_limit_period': 60,
            'batch_size': 50
        }

    @classmethod
    def is_perplexity_enabled(cls) -> bool:
        return bool(cls.PERPLEXITY_API_KEY)

    @classmethod
    def is_fyers_configured(cls) -> bool:
        """Return whether the minimum FYERS credentials for authenticated API use are present."""
        return bool(cls.FYERS_APP_ID and cls.FYERS_ACCESS_TOKEN)
