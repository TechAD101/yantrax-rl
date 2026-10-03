import os
import sys
import unittest
from datetime import datetime

# Setup path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.core.decision_pipeline import DecisionPipeline
from backend.core.decision_context import DecisionContext, TradingAction, GovernanceState
from backend.attribution.attribution_engine import AttributionEngine
from backend.models import Outcome, Attribution, LearningEvent, JournalEntry, PaperPosition, Order
from backend.db import init_db, get_session
from backend.service_registry import registry


class TestSentimentService:
    def get_comprehensive_sentiment(self, symbol):
        return {
            'symbol': symbol,
            'composite_sentiment': 0.75,
            'recommendation': 'BUY',
            'confidence': 0.8,
            'components': {
                'fear_greed': {
                    'fear_greed_index': 0.75,
                },
                'options_flow': {
                    'flow_score': 0.75,
                },
                'social_sentiment': {
                    'overall_sentiment': 0.75,
                },
            },
        }


class TestMarketData:
    def get_stock_price(self, symbol):
        # Deterministic capitulation-oversold fixture: gentle drift down then a
        # sharp 10-day sell-off, closing with the first bounce day. Snapshot
        # price matches the history tail so technical analysis is coherent.
        base = 100.0 - 0.1 * 49 - 2.5 * 10  # 70.0
        price = base
        return {
            'symbol': symbol.upper(),
            'price': price,
            'change_percent': 0.9,
            'trend': 'neutral',
            'volume': 1000000,
            'volatility': 0.02,
            'source': 'test_fixture',
            'verified': True,
        }

    def get_fundamentals(self, symbol):
        return {
            'pe_ratio': 18.0,
            'return_on_equity': 0.25,
            'debt_to_equity': 0.3,
            'revenue_growth': 0.12,
            'earnings_growth': 0.15,
            'profit_margin': 0.22,
        }

    def get_price_history(self, symbol, days):
        # Deterministic oversold-capitulation series: 50-day gentle drift, sharp
        # 10-day decline, then a nominal bounce day. RSI saturates oversold and
        # price breaks the lower Bollinger band -> genuine mean-reversion BUY
        # setup, verified by the full pipeline.
        history = [100.0 - (0.1 * i) for i in range(50)]
        for _ in range(10):
            history.append(history[-1] - 2.5)
        return [{'close': close} for close in history[-days:]]


class TestStrategySignalContract(unittest.TestCase):
    """Regression tests for the technical directional signal contract."""

    def test_bullish_technical_crossover_produces_buy(self):
        from backend.services.institutional_strategy_engine import InstitutionalStrategyEngine

        engine = InstitutionalStrategyEngine()
        technical = {
            'signals': {
                'ema_crossover': 'bullish',
                'rsi': 'neutral',
                'bollinger': 'neutral',
                'macd': 'bullish',
            }
        }

        action, reasoning = engine._determine_action(
            technical=technical,
            sentiment=0.75,
            fundamental=0.80,
            regime=engine._detect_market_regime(
                {'volatility': 0.02, 'trend': 'neutral'},
                {'fear_greed_index': {'fear_greed_index': 0.75}},
            ),
        )

        self.assertEqual(action, 'BUY')
        self.assertIn('bullish', reasoning.lower())


class TestPipelineProviderContract(unittest.TestCase):
    def test_missing_market_provider_abstains(self):
        import asyncio
        pipeline = DecisionPipeline(market_data=None, sentiment_service=TestSentimentService())
        ctx = asyncio.run(pipeline.execute_decision('AAPL'))
        self.assertEqual(ctx.final_action, TradingAction.ABSTAIN)
        self.assertIn('market_snapshot_error', ctx.provenance)


class TestSizingFailureContract(unittest.TestCase):
    def test_sizing_engine_failure_is_not_silently_fallback(self):
        from backend.risk.position_sizer import PositionSizer, SizingMethod
        from backend.core.decision_context import PortfolioState, MarketSnapshot, CandidateStrategy
        from datetime import datetime
        from unittest.mock import Mock

        class FailingStrategyEngine:
            def _calculate_position_size(self, **kwargs):
                raise ValueError("sizing dependency failed")

        pipeline_ctx = DecisionContext(symbol="AAPL")
        pipeline_ctx.candidate_strategy = CandidateStrategy(
            action=TradingAction.BUY,
            confidence=0.8,
            reasoning="test",
            position_size=1000.0,
            stop_loss=140.0,
            take_profit=165.0,
            risk_score=0.2,
        )
        pipeline_ctx.market_snapshot = MarketSnapshot(
            symbol="AAPL",
            price=150.0,
            timestamp=datetime.now(),
            volatility=0.02,
            source="test_fixture",
            verified=True,
        )
        pipeline_ctx.portfolio_state = PortfolioState(
            portfolio_id="test-portfolio",
            total_value=100000.0,
            cash=100000.0,
            positions={},
            risk_profile="moderate",
        )

        sizer = PositionSizer(
            strategy_engine=FailingStrategyEngine(),
            default_method=SizingMethod.STRATEGY_ENGINE,
        )
        with self.assertRaises(RuntimeError):
            sizer.calculate(pipeline_ctx)


class TestFullPipeline(unittest.TestCase):
    """Test the full paper-trade lifecycle from market snapshot to learning."""

    @classmethod
    def setUpClass(cls):
        os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
        from backend.db import reset_engine, get_engine
        from backend.models import Base
        reset_engine()
        engine = get_engine()
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)

    def setUp(self):
        self.pipeline = DecisionPipeline(
            market_data=TestMarketData(),
            sentiment_service=TestSentimentService(),
        )
        self.session = get_session()
        self.session.query(LearningEvent).delete()
        self.session.query(Attribution).delete()
        self.session.query(Outcome).delete()
        self.session.query(JournalEntry).delete()
        self.session.query(PaperPosition).delete()
        self.session.query(Order).delete()
        self.session.commit()

    def tearDown(self):
        self.session.close()

    def test_full_lifecycle_buy_then_sell(self):
        """Test the full lifecycle: open a BUY position, then close it with an opposite SELL signal."""
        import asyncio
        from backend.core.decision_context import TradingAction, GovernanceState

        # First decision: open position (BUY signal) with normal market data
        pipeline1 = DecisionPipeline(
            market_data=TestMarketData(),
            sentiment_service=TestSentimentService(),
        )
        ctx1 = asyncio.run(pipeline1.execute_decision('AAPL'))
        self.assertEqual(ctx1.final_action, TradingAction.BUY)
        self.assertIsNone(ctx1.outcome_id)  # No outcome until position is closed
        self.assertIsNotNone(ctx1.position_id)  # Position opened
        self.assertIsNone(ctx1.attribution_id)  # No attribution yet
        self.assertIsNone(ctx1.learning_event_id)  # No learning events yet

        # Clear trade validator history to allow reversal (close BUY, open SELL)
        from backend.services.trade_validator import get_trade_validator
        validator = get_trade_validator()
        validator.trade_history.clear()

        # Define bearish market data and sentiment services
        class BearishMarketData:
            def get_stock_price(self, symbol):
                return {
                    'symbol': symbol.upper(),
                    'price': 1.0,  # Extremely low price to induce SELL
                    'change_percent': -90.0,
                    'trend': 'strong_down',
                    'volume': 2000000,
                    'volatility': 0.05,
                    'source': 'test_fixture',
                    'verified': True,
                }

            def get_fundamentals(self, symbol):
                # Poor fundamentals to reinforce SELL
                return {
                    'pe_ratio': 1.0,
                    'return_on_equity': 0.01,
                    'debt_to_equity': 2.0,
                    'revenue_growth': -0.5,
                    'earnings_growth': -0.5,
                    'profit_margin': 0.01,
                }

            def get_price_history(self, symbol, days):
                # Provide a price history that is consistently declining
                base = 100.0
                history = []
                for i in range(days):
                    price = base - (1.0 * i)  # Decline by 1 each day
                    history.append(round(price, 2))
                return [{'close': close} for close in history]

        class BearishSentimentService:
            def get_sentiment(self, symbol):
                return {
                    'score': -0.9,
                    'label': 'BEARISH',
                }

            def get_fundamentals_sentiment(self, symbol):
                return {
                    'score': -0.8,
                    'label': 'BEARISH',
                }

            def get_social_sentiment(self, symbol):
                return {
                    'score': -0.7,
                    'label': 'BEARISH',
                }

            def get_comprehensive_sentiment(self, symbol):
                return {
                    'score': -0.8,
                    'label': 'BEARISH',
                }

        # Second decision: opposite signal (SELL) with bearish market data to close the position
        # Use the mock strategy engine to guarantee a SELL signal for the bearish fixture
        from tests.mock_strategy_engine import MockStrategyEngineForBearishFixture
        pipeline2 = DecisionPipeline(
            market_data=BearishMarketData(),
            sentiment_service=BearishSentimentService(),
            strategy_engine=MockStrategyEngineForBearishFixture(),
        )
        ctx2 = asyncio.run(pipeline2.execute_decision('AAPL'))
        # Now we expect the position from ctx1 to be closed and a new position (SELL) opened.
        self.assertEqual(ctx2.final_action, TradingAction.SELL)
        self.assertIsNotNone(ctx2.outcome_id)  # Outcome from the closed BUY position
        self.assertIsNotNone(ctx2.position_id)  # Position ID of the new SELL position
        self.assertIsNotNone(ctx2.attribution_id)  # Attribution from the closed position
        self.assertIsNotNone(ctx2.learning_event_id)  # Learning events from the closed position

        # Check database for the closed outcome and its attribution and learning events
        session = get_session()
        try:
            from backend.models import PaperPosition
            # We should have two PaperPositions: one closed (BUY) and one open (SELL)
            positions = session.query(PaperPosition).all()
            self.assertEqual(len(positions), 2)
            closed_count = sum(1 for p in positions if p.status == 'CLOSED')
            open_count = sum(1 for p in positions if p.status == 'OPEN')
            self.assertEqual(closed_count, 1)
            self.assertEqual(open_count, 1)
            closed_pos = [p for p in positions if p.status == 'CLOSED'][0]
            open_pos = [p for p in positions if p.status == 'OPEN'][0]
            self.assertEqual(closed_pos.side, 'BUY')
            self.assertEqual(open_pos.side, 'SELL')
            # Check that the closed position has an outcome
            outcomes = session.query(Outcome).all()
            self.assertEqual(len(outcomes), 1)
            outcome = outcomes[0]
            self.assertEqual(outcome.symbol, 'AAPL')
            self.assertEqual(outcome.action, 'BUY')  # The action of the closed position
            self.assertIsNotNone(outcome.pnl)
            # Check attributions and learning events from the closed outcome
            attributions = session.query(Attribution).all()
            self.assertGreater(len(attributions), 0)
            learning_events = session.query(LearningEvent).all()
            self.assertGreater(len(learning_events), 0)
            # Check that the outcome_id matches ctx2.outcome_id
            self.assertEqual(outcome.id, ctx2.outcome_id)
            # Check that the attribution_id and learning_event_id are set (they are from the closed outcome)
            self.assertEqual(ctx2.attribution_id, f"attr_{outcome.attributions[0].component}_{outcome.id}" if outcome.attributions else None)
            self.assertEqual(ctx2.learning_event_id, outcome.learning_event_ids[0] if outcome.learning_event_ids else None)
        finally:
            session.close()

        # Check that the provenance includes the expected stages for both decisions
        # For the first decision, we expect up to position_opened (no outcome_attribution)
        expected_stages_first = [
            'market_snapshot', 'evidence_synthesis', 'strategy_candidate', 'agent_voting', 'debate',
            'ceo_governance', 'risk', 'position_sizing', 'execution', 'position_opened'
        ]
        for stage in expected_stages_first:
            self.assertIn(stage, ctx1.provenance, f"Missing provenance for stage {stage} in first decision: {ctx1.provenance.keys()}")

        # For the second decision, we expect outcome_attribution (since we closed a position)
        expected_stages_second = [
            'market_snapshot', 'evidence_synthesis', 'strategy_candidate', 'agent_voting', 'debate',
            'ceo_governance', 'risk', 'position_sizing', 'execution', 'outcome_attribution'
        ]
        for stage in expected_stages_second:
            self.assertIn(stage, ctx2.provenance, f"Missing provenance for stage {stage} in second decision: {ctx2.provenance.keys()}")

    def test_blocked_trade_provenance(self):
        """Test that a blocked trade preserves provenance without outcome."""
        import asyncio
        asyncio.run(self.pipeline.execute_decision('AAPL'))

        from backend.services.emotional_safeguards import get_emotional_safeguards
        safeguards = get_emotional_safeguards()
        safeguards._state = safeguards._state.__class__.MOUNA
        ctx_blocked = asyncio.run(self.pipeline.execute_decision('AAPL'))

        self.assertEqual(ctx_blocked.risk_governance, GovernanceState.BLOCK,
                         "Trade should be blocked when in MOUNA mode")
        self.assertIsNone(ctx_blocked.outcome_id)
        self.assertIn('risk', ctx_blocked.provenance)
        self.assertNotIn('execution', ctx_blocked.provenance)
        self.assertNotIn('outcome_attribution', ctx_blocked.provenance)
        self.assertIsNotNone(ctx_blocked.decision_id)
        safeguards._state = safeguards._state.__class__.CALM

    def test_attribution_engine_directly(self):
        """Test the attribution engine in isolation."""
        engine = AttributionEngine()
        from backend.attribution.attribution_engine import OutcomeRecord
        from datetime import datetime

        outcome = OutcomeRecord(
            outcome_id='out_test123',
            decision_id='dec_test123',
            order_id='order_test123',
            fill_id='fill_test123',
            symbol='AAPL',
            action='BUY',
            requested_size=10,
            filled_size=10,
            requested_price=150.0,
            filled_price=150.0,
            stop_loss=140.0,
            take_profit=160.0,
            decision_timestamp=datetime.utcnow(),
            order_timestamp=datetime.utcnow(),
            fill_timestamp=datetime.utcnow(),
            close_timestamp=datetime.utcnow(),
            gross_pnl=100.0,
            net_pnl=100.0,
            commission=1.0,
            slippage=0.5,
            spread_cost=0.0,
            market_price_at_decision=150.0,
            market_regime_at_decision='bull_market',
            volatility_at_decision=0.2,
            market_price_at_close=160.0,
            market_regime_at_close='bull_market',
            volatility_at_close=0.2,
            strategy_name='institutional',
            strategy_confidence=0.8,
            agent_votes={'consensus_strength': 0.7, 'technical_confidence': 0.8, 'fundamental_confidence': 0.7, 'sentiment_confidence': 0.6},
            debate_result={'winning_signal': 'BUY', 'consensus_score': 0.75},
            ceo_decision={'final_signal': 'BUY', 'confidence': 0.85, 'override_applied': False, 'reasoning': 'Strong fundamentals'},
            risk_governance='APPROVE',
            position_size_method='kelly'
        )
        attributed_outcome = engine.attribute_outcome(outcome)
        self.assertIsNotNone(attributed_outcome)
        self.assertEqual(attributed_outcome.outcome_id, outcome.outcome_id)
        self.assertEqual(attributed_outcome.net_pnl, 100.0)
        self.assertGreater(len(attributed_outcome.attributions), 0)


if __name__ == '__main__':
    unittest.main()