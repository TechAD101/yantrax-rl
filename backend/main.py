    SENTIMENT_READY = False

# Initialize Institutional Strategy Engine
try:
    from backend.services.institutional_strategy_engine import get_strategy_engine
    STRATEGY_ENGINE = get_strategy_engine()
    STRATEGY_ENGINE_READY = bool(STRATEGY_ENGINE)
    logger.info("✅ Institutional Strategy Engine initialized")
except Exception as e:
    logger.error(f"❌ Failed to initialize Institutional Strategy Engine: {e}")
    STRATEGY_ENGINE = None
    STRATEGY_ENGINE_READY = False

# Initialize Market Data
MARKET_SERVICE_READY = False
market_data = None
market_provider = None
MARKET_PRICE_CACHE: Dict[str, Dict[str, Any]] = {}
try:
    from backend.services.market_data_service import get_market_data
    class AlpacaMarketProvider:
        def get_price(self, symbol):
            data = get_market_data(symbol)
            return {'symbol': symbol.upper(), 'price': data['market_data']['price'], 'source': 'alpaca'} if data else {'symbol': symbol.upper(), 'price': 0, 'error': 'Market data unavailable', 'source': 'alpaca'}
        def get_stock_price(self, symbol):
            return self.get_price(symbol)
        def get_fundamentals(self, symbol): return {}
        def get_verification_stats(self): return {'provider': 'alpaca', 'verified': True}
        def get_price_verified(self, symbol):
            return {'verified': True, **self.get_price(symbol)}
        def get_recent_audit_logs(self, limit): return []
        def get_price_history(self, symbol, days): return []
    market_data = AlpacaMarketProvider()
    market_provider = market_data
    registry.register_service('market_data', market_data)
    MARKET_SERVICE_READY = True
    logger.info("✅ Alpaca market data service initialized successfully")
except Exception as e:
    logger.error(f"❌ MarketDataService initialization failed: {e}")
    market_provider = None

# Initialize AI Firm
AI_FIRM_READY = False
RL_ENV_READY = False
try:
    from backend.ai_firm.ceo import AutonomousCEO, CEOPersonality
    from backend.ai_firm.agent_manager import AgentManager
    from backend.rl_core.env_market_sim import MarketSimEnv
    from backend.services.oracle_service import OracleService
    
    oracle_service = OracleService()
    agent_manager = AgentManager(oracle_service=oracle_service)
    ceo = AutonomousCEO(personality=CEOPersonality.BALANCED)
    if PERPLEXITY_READY:
        ceo.set_perplexity_service(PERPLEXITY_SERVICE)
    
    rl_env = MarketSimEnv()
    
    # Debate Engine
    from backend.ai_firm.debate_engine import DebateEngine
    DEBATE_ENGINE = DebateEngine(agent_manager)
    if PERPLEXITY_READY:
        DEBATE_ENGINE.set_perplexity_service(PERPLEXITY_SERVICE)
        
    AI_FIRM_READY = True
    RL_ENV_READY = True
    logger.info("✅ AI FIRM & RL CORE OPERATIONAL")
except Exception as e:
    logger.error(f"❌ AI Firm core initialization failed: {e}")
    DEBATE_ENGINE = MockDebateEngine()


app = Flask(__name__)
import os
cors_origins_raw = os.environ.get('CORS_ORIGINS')
if cors_origins_raw:
    origins = [o.strip() for o in cors_origins_raw.split(',') if o.strip()]
else:
    origins = ['*']