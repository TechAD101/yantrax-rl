import logging

logger = logging.getLogger(__name__)


class ServiceRegistry:
    """
    Singleton Service Registry for YantraX RL.
    Manages the lifecycle of core services and provides a centralized access point.
    Initialization of heavy services is LAZY - occurs on first explicit request.
    """

    _instance = None

    def __init__(self):
        if ServiceRegistry._instance:
            raise Exception("This class is a singleton!")
        self.services = {}
        self._initialized = False
        ServiceRegistry._instance = self

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = ServiceRegistry()
        return cls._instance

    def _initialize_core_services(self):
        """Pre-initialize or setup placeholder for core services. Call explicitly when needed."""
        if self._initialized:
            return
        logger.info("Initializing Service Registry (lazy)...")

        # Initialize Perplexity (if configured)
        try:
            from backend.services.perplexity_intelligence import get_perplexity_service
            self.services['perplexity'] = get_perplexity_service()
            logger.info("✓ Perplexity Service registered")
        except Exception as e:
            logger.error(f"Failed to register Perplexity Service: {e}")
            self.services['perplexity'] = None

        # Initialize Knowledge Base (lazy - no embedding init here)
        try:
            from backend.services.knowledge_base_service import get_knowledge_base
            self.services['kb'] = get_knowledge_base(persist_directory="./chroma_db", lazy_init=True)
            logger.info("✓ Knowledge Base registered (lazy)")
        except Exception as e:
            logger.error(f"Failed to register Knowledge Base: {e}")
            self.services['kb'] = None

        # Initialize Trade Validator
        try:
            from backend.services.trade_validator import get_trade_validator
            self.services['trade_validator'] = get_trade_validator()
            logger.info("✓ Trade Validator registered")
        except Exception as e:
            logger.error(f"Failed to register Trade Validator: {e}")
            self.services['trade_validator'] = None

        self._initialized = True

    def ensure_initialized(self):
        """Ensure core services are initialized. Safe to call multiple times."""
        if not self._initialized:
            self._initialize_core_services()

    def get_service(self, name: str):
        # Auto-initialize on first service access
        self.ensure_initialized()
        return self.services.get(name)

    def register_service(self, name: str, service_instance):
        self.services[name] = service_instance
        logger.info(f"Registered external service: {name}")


# Global access point - lazily instantiated
registry = ServiceRegistry.get_instance()