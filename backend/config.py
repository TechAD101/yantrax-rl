import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class Config:
    """Centralized configuration for YantraX RL"""
    
    # System Info
    VERSION = "5.23-STABLE"
    ENVIRONMENT = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('DEBUG', 'true').lower() == 'true'
    PORT = int(os.getenv('PORT', 5000))
    
# API Keys - Environment variables required for production
    FMP_API_KEY = os.getenv('FMP_API_KEY') or os.getenv('FMP_KEY')
    if not FMP_API_KEY:
        logger.warning("FMP_API_KEY not found in environment. Market data may be limited.")
    ALPACA_API_KEY = os.getenv('ALPACA_API_KEY', '')
    ALPACA_SECRET_KEY = os.getenv('ALPACA_SECRET_KEY', '')
    PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY', '')

    # CORS Configuration
    CORS_ALLOWED_ORIGINS = [
        origin.strip()
        for origin in os.getenv(
            'CORS_ALLOWED_ORIGINS',
            'http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173'
        ).split(',')
    ]
    
    # DB Config
    PERSIST_DIR = "chroma_db"
    
    # Market Data Config
    CACHE_TTL_SECONDS = 60
    
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
