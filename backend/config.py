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

    # DB Config
    PERSIST_DIR = "chroma_db"

    # Market Data Config
    CACHE_TTL_SECONDS = 60

    @classmethod
    def is_perplexity_enabled(cls) -> bool:
        return bool(cls.PERPLEXITY_API_KEY)
