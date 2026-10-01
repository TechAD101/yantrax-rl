"""Evidence integrity tests (mission §5, §6, §22).

No fabricated production evidence may reach the canonical decision path:
- missing fundamentals → unverified neutral, never fake P/E / ROE / FCF
- missing sentiment provider → unverified neutral, never random-derived scores
- unverified market data → ABSTAIN, never a trade
- synthetic sources are always labeled
"""
import asyncio
import os
import sys
import unittest
from datetime import datetime
from unittest.mock import patch

os.environ['SECRET_KEY'] = 'test-secret-key-for-ci'
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from backend.db import reset_engine, get_engine  # noqa: E402
from backend.models import Base  # noqa: E402
reset_engine()
Base.metadata.create_all(get_engine())

from tests.test_full_pipeline import TestMarketData, TestSentimentService  # noqa: E402
from backend.core.decision_pipeline import DecisionPipeline  # noqa: E402
from backend.core.decision_context import TradingAction  # noqa: E402
from backend.core.evidence_synthesizer import EvidenceSynthesizer, build_market_snapshot  # noqa: E402


class NoFundamentals(TestMarketData):
    def get_fundamentals(self, symbol):
        return {}


class TestEvidenceIntegrity(unittest.TestCase):

    def test_no_sentiment_service_is_unverified_neutral(self):
        from backend.services.institutional_strategy_engine import InstitutionalStrategyEngine
        syn = EvidenceSynthesizer(
            strategy_engine=InstitutionalStrategyEngine(),
            market_data=TestMarketData(),
            sentiment_service=None,
        )
        snapshot = build_market_snapshot('AAPL', TestMarketData(), TestMarketData().get_stock_price('AAPL'), {})
        pkg = syn.synthesize('AAPL', snapshot)
        self.assertFalse(pkg.sentiment.verified)
        self.assertEqual(pkg.sentiment.source, 'unavailable')
        self.assertEqual(pkg.sentiment.composite_signal, 'HOLD')
        # Explicitly neutral — no random-derived extreme signals
        self.assertEqual(pkg.sentiment.composite_sentiment, 0.5)

    def test_missing_fundamentals_not_fabricated(self):
        from backend.services.institutional_strategy_engine import InstitutionalStrategyEngine
        syn = EvidenceSynthesizer(
            strategy_engine=InstitutionalStrategyEngine(),
            market_data=NoFundamentals(),
            sentiment_service=TestSentimentService(),
        )
        result = syn._analyze_fundamental({})
        self.assertFalse(result.verified)
        self.assertIsNone(result.pe_ratio, 'no fake P/E allowed')
        self.assertIsNone(result.return_on_equity, 'no fake ROE allowed')
        self.assertIsNone(result.free_cash_flow, 'no fake FCF allowed')
        self.assertEqual(result.source, 'unavailable')

    def test_unverified_market_data_abstains(self):
        class UnverifiedSource(TestMarketData):
            def get_stock_price(self, symbol):
                quote = super().get_stock_price(symbol)
                quote['source'] = 'simulated_cache'
                quote['verified'] = False
                return quote
        pipeline = DecisionPipeline(market_data=UnverifiedSource(), sentiment_service=TestSentimentService())
        ctx = asyncio.run(pipeline.execute_decision('AAPL'))
        self.assertEqual(ctx.final_action, TradingAction.ABSTAIN)
        self.assertIn('unverified_market_data', ctx.provenance)
        self.assertIsNone(ctx.order_id)

    def test_synthetic_sentiment_source_is_labeled(self):
        class SyntheticSentiment(TestSentimentService):
            def get_comprehensive_sentiment(self, symbol):
                data = super().get_comprehensive_sentiment(symbol)
                data['source'] = 'simulated_social'
                return data
        from backend.services.institutional_strategy_engine import InstitutionalStrategyEngine
        syn = EvidenceSynthesizer(
            strategy_engine=InstitutionalStrategyEngine(),
            market_data=TestMarketData(),
            sentiment_service=SyntheticSentiment(),
        )
        snapshot = build_market_snapshot('AAPL', TestMarketData(), TestMarketData().get_stock_price('AAPL'), {})
        pkg = syn.synthesize('AAPL', snapshot)
        self.assertFalse(pkg.sentiment.verified)
        self.assertEqual(pkg.sentiment.source, 'simulated_social')

    def test_provider_backed_evidence_is_verified(self):
        from backend.services.institutional_strategy_engine import InstitutionalStrategyEngine
        syn = EvidenceSynthesizer(
            strategy_engine=InstitutionalStrategyEngine(),
            market_data=TestMarketData(),
            sentiment_service=TestSentimentService(),
        )
        snapshot = build_market_snapshot('AAPL', TestMarketData(), TestMarketData().get_stock_price('AAPL'),
                                         TestMarketData().get_fundamentals('AAPL'))
        pkg = syn.synthesize('AAPL', snapshot)
        self.assertTrue(pkg.fundamental.verified)
        self.assertEqual(pkg.fundamental.source, 'provider')

    def test_legacy_random_sentiment_service_not_defaulted(self):
        """EvidenceSynthesizer must never silently bind the random-driven legacy service."""
        from backend.services.institutional_strategy_engine import InstitutionalStrategyEngine
        syn = EvidenceSynthesizer(
            strategy_engine=InstitutionalStrategyEngine(),
            market_data=TestMarketData(),
        )
        self.assertIsNone(syn.sentiment_service)


if __name__ == '__main__':
    unittest.main()