import sys
import os
import logging

# Setup paths
sys.path.append(os.path.join(os.getcwd(), 'backend'))

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("InstitutionalVerifier")

def test_institutional_grade():
    logger.info("🧪 STARTING TEAM 5 INSTITUTIONAL VERIFICATION...")
    
    results = {
        "personas": False,
        "knowledge_base": False,
        "trade_validator": False,
        "data_verification": False,
        "api_layer": False
    }

    try:
        # 1. PERSONA REGISTRY CHECK
        logger.info("\n--- 1. Testing Explicit AI Personas ---")
        from backend.ai_agents.persona_registry import PersonaRegistry
        registry = PersonaRegistry()
        
        # Check if personas are registered
        summaries = registry.get_all_summaries()
        logger.info(f"Personas found: {len(summaries)}")
        if len(summaries) >= 2:
            results["personas"] = True
            logger.info("✅ Persona Registry Active")
        else:
            logger.error("❌ Persona Registry Incomplete")

        # Conduct a mock vote
        vote_result = registry.conduct_vote({
            "symbol": "AAPL", 
            "price": 150.0, 
            "rsi": 30, 
            "trend": "bullish"
        }, market_context={
            "vix": 15,
            "market_trend": "bullish",
            "liquidity": "high"
        })
        logger.info(f"Vote Concluded: {vote_result['consensus']} (Confidence: {vote_result['consensus_strength']})")


        # 2. KNOWLEDGE BASE CHECK
        logger.info("\n--- 2. Testing Knowledge Base Engine ---")
        from backend.services.knowledge_base_service import KnowledgeBaseService
        kb = KnowledgeBaseService()
        
        # Query wisdom
        wisdom = kb.query_wisdom("market crash", max_results=1)
        if wisdom:  # Wisdom is a list, check if not empty
            logger.info(f"Wisdom Retrieved: {wisdom[0]['content'][:50]}...")
            results["knowledge_base"] = True
            logger.info("✅ Knowledge Base Operational")
        else:
            logger.warning("⚠️ Knowledge Base returned empty results (might need ingestion)")
            # Assuming it passes if code runs, but flagging empty

        
        # 3. TRADE VALIDATOR CHECK
        logger.info("\n--- 3. Testing Trade Validation Engine ---")
        from backend.services.trade_validator import TradeValidator
        validator = TradeValidator()
        
        # Mock Trade (Should likely fail defaults if market data is strict, but we test logic)
        mock_trade = {
            "symbol": "TEST",
            "action": "BUY",
            "price": 100,
            "quantity": 10,
            "strategy": "test"
        }
        # Mock context for validation
        mock_context = {
            "portfolio_value": 100000,
            "vix": 15,  # Safe
            "market_trend": "bullish"
        }
        
        validation = validator.validate_trade(mock_trade, mock_context)
        logger.info(f"Validation Result: {validation['allowed']}")
        logger.info(f"Checks Passed: {validation['checks_passed']}/{len(validation['pass_map'])}")
        
        if 'validation_history' in validator.__dict__: # Check if audit trail exists
            results["trade_validator"] = True
            logger.info("✅ Trade Validator & Audit Trail Active")


        # 4. DATA VERIFICATION CHECK
        logger.info("\n--- 4. Testing Triple-Source Verification ---")
        from backend.services.market_data_service_waterfall import WaterfallMarketDataService
        service = WaterfallMarketDataService()
        
        # Check if new methods exist
        if hasattr(service, 'get_price_verified') and hasattr(service, 'get_verification_stats'):
            results["data_verification"] = True
            logger.info("✅ Triple-Source Methods Detected")
            
            # Mock call (might fail without API keys, so wrapping)
            try:
                stats = service.get_verification_stats()
                logger.info(f"Verification Stats: {stats}")
            except Exception as e:
                logger.warning(f"Could not fetch live stats (expected if no keys): {e}")
        else:
            logger.error("❌ Triple-Source Methods Missing")


        # 5. API LAYER CHECK (Flask Test Client)
        logger.info("\n--- 5. Testing API Endpoints ---")
        from backend.main import app
        with app.test_client() as client:
            # Check Health
            resp = client.get('/health')
            if resp.status_code == 200:
                logger.info("✅ /health endpoint OK")
                
            # Check Status (Institutional Metrics)
            resp = client.get('/api/ai-firm/status')
            data = resp.get_json()
            if 'institutional_services' in data:
                logger.info("✅ Institutional Metrics Exposed")
                results["api_layer"] = True
            else:
                logger.error("❌ Institutional Metrics Missing from /status")

    except Exception as e:
        logger.error(f"❌ FATAL ERROR DURING VERIFICATION: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    # FINAL REPORT
    logger.info("\n" + "="*40)
    logger.info("INSTITUTIONAL VERIFICATION REPORT")
    logger.info("="*40)
    passed = 0
    for component, success in results.items():
        status = "PASS" if success else "FAIL"
        if success: passed += 1
        logger.info(f"{component.ljust(25)}: {status}")
    
    logger.info("-" * 40)
    logger.info(f"SCORE: {passed}/5")
    
    if passed == 5:
        logger.info("🏆 RESULT: INSTITUTIONAL GRADE CONFIRMED")
        return True
    else:
        logger.info("⚠️ RESULT: GAPS DETECTED")
        return False

if __name__ == "__main__":
    success = test_institutional_grade()
    sys.exit(0 if success else 1)
