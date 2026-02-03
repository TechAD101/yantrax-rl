import logging
from typing import Dict, Any, Optional
from config import Config

logger = logging.getLogger(__name__)

class ServiceRegistry:
    """
    Singleton Service Registry for YantraX RL.
    Manages the lifecycle of core services and provides a centralized access point.
    """
    _instance = None
    
    def __init__(self):
        if ServiceRegistry._instance:
            raise Exception("This class is a singleton!")
        self.services = {}
        self._initialize_core_services()
        ServiceRegistry._instance = self

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = ServiceRegistry()
        return cls._instance

    def _initialize_core_services(self):
        """Pre-initialize or setup placeholder for core services"""
        logger.info("Initializing Service Registry...")
        
        # Initialize Perplexity (if configured)
        try:
            from services.perplexity_intelligence import get_perplexity_service
            self.services['perplexity'] = get_perplexity_service()
            logger.info("✓ Perplexity Service registered")
        except Exception as e:
            logger.error(f"Failed to register Perplexity Service: {e}")
            self.services['perplexity'] = None

        # Initialize Knowledge Base
        try:
            from services.knowledge_base_service import get_knowledge_base
            self.services['kb'] = get_knowledge_base()
            logger.info("✓ Knowledge Base registered")
        except Exception as e:
            logger.error(f"Failed to register Knowledge Base: {e}")
            self.services['kb'] = None

        # Initialize Trade Validator
        try:
            from services.trade_validator import get_trade_validator
            self.services['trade_validator'] = get_trade_validator()
            logger.info("✓ Trade Validator registered")
        except Exception as e:
            logger.error(f"Failed to register Trade Validator: {e}")
            self.services['trade_validator'] = None

    def get_service(self, name: str):
        return self.services.get(name)

    def register_service(self, name: str, service_instance):
        self.services[name] = service_instance
        logger.info(f"Registered external service: {name}")

# Global access point
registry = ServiceRegistry.get_instance()
