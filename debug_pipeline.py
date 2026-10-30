import asyncio, os
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
from backend.db import reset_engine, get_session
from backend.models import Base, PaperPosition
reset_engine()
from backend.db import get_engine
engine = get_engine()
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)
from tests.test_full_pipeline import TestMarketData, TestSentimentService
from backend.core.decision_pipeline import DecisionPipeline
from backend.core.decision_context import TradingAction

# Monkey-patch lifecycle for debug
orig_lifecycle = DecisionPipeline._stage_position_lifecycle
async def debug_lifecycle(self, ctx):
    print('[LIFECYCLE] Called')
    action = ctx.final_action or (ctx.candidate_strategy.action if ctx.candidate_strategy else None)
    print('[LIFECYCLE] action=%s' % action)
    
    if action not in (TradingAction.BUY, TradingAction.SELL):
        print('[LIFECYCLE] Returning early - not BUY/SELL')
        return await orig_lifecycle(self, ctx)
    
    session = get_session()
    try:
        existing_pos = session.query(PaperPosition).filter_by(symbol=ctx.symbol, status='OPEN').first()
        print('[LIFECYCLE] Existing pos: %s' % (existing_pos.id if existing_pos else None))
        if existing_pos:
            new_side = (ctx.final_action or (ctx.candidate_strategy.action if ctx.candidate_strategy else None) or TradingAction.BUY).value
            print('[LIFECYCLE] Existing side=%s, new_side=%s' % (existing_pos.side, new_side))
            if existing_pos.side == new_side:
                print('[LIFECYCLE] SAME SIDE - would reject')
            else:
                print('[LIFECYCLE] OPPOSITE SIDE - would close')
    finally:
        session.close()
    
    result = await orig_lifecycle(self, ctx)
    print('[LIFECYCLE] Result: action=%s, pos=%s' % (result.final_action, result.position_id))
    return result

DecisionPipeline._stage_position_lifecycle = debug_lifecycle

pipeline = DecisionPipeline(market_data=TestMarketData(), sentiment_service=TestSentimentService())

print('\\n=== EXEC1 ===')
ctx1 = asyncio.run(pipeline.execute_decision('AAPL'))
print('Result: action=%s, pos=%s' % (ctx1.final_action, ctx1.position_id))

print('\\n=== EXEC2 ===')
ctx2 = asyncio.run(pipeline.execute_decision('AAPL'))
print('Result: action=%s, pos=%s' % (ctx2.final_action, ctx2.position_id))
