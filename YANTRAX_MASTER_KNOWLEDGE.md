# YANTRA X MASTER KNOWLEDGE

## 1. Verified Current Facts

### Repository State
- **Location**: `/home/ubuntu/yantrax-rl`
- **Python Version**: 3.10.13 (venv at `.venv/`)
- **Test Status**: 16 core tests passing (test_full_pipeline.py, test_position_lifecycle.py, test_learning_loop.py)
- **3 pre-existing test failures** remain unrelated to architecture changes (require additional ML dependencies: torch, transformers, etc.)

### Architecture (Gates Implementation)
- **Gate 0**: Security hardening (CORS allowlist, JWT auth, secret removal)
- **Gate 1**: Fail-closed decision pipeline
- **Gate 2-3**: Persistence layer - CEO memory and learning state across restarts
- **Gate 4**: Honest agent labeling (configured defaults vs measured performance)
- **Gate 6**: Heartbeat market-data check verifies actual data reachability
- **Gate 7**: Deployment workflow hardening with real SHA and health verification

### Core Components
- `backend/core/decision_pipeline.py` - Main decision flow with Gate architecture
- `backend/core/decision_context.py` - TradingAction, GovernanceState, MarketSnapshot, PortfolioState
- `backend/ai_firm/agent_manager.py` - Multi-agent orchestration
- `backend/attribution/attribution_engine.py` - Provenance chain and learning
- `backend/risk/risk_governor.py` - Risk control and position sizing
- `backend/db.py` - SQLAlchemy with JournalEntry, PaperPosition, Order models
- `backend/models.py` - Outcome, Attribution, LearningEvent models

### Database Schema (11 Models)
- User, Portfolio, PortfolioPosition, Strategy, StrategyProfile, Memecoin
- JournalEntry, Order, Outcome, Attribution, LearningEvent

## 2. Historical Facts

### Original Vision (2024-2025)
- Multi-agent AI trading firm with distinct personas
- CEO with governance and persistent memory
- Emotional intelligence via Mouna system
- Genuine learning from realized outcomes
- Paper trading only (no live execution)

### Development Phases Implemented
- Phase 0: Core infrastructure and security
- Phase 1: Portfolio management and strategy marketplace
- Phase 2: Order management and memecoin engine
- Phase 3: Backtesting and authentication
- Phase 5.1: Provenance & Integrity Correction
- Phase 5.2: Genuine Paper-Trading Lifecycle

## 3. Previously Intended but Unimplemented Designs

### Missing Components
- **RedisCircuitBreaker** - Risk module incomplete (test_circuit_breaker.py imports it but service doesn't exist)
- **Celery beat schedules** - God cycle/cron infrastructure partially configured
- **Real market data providers** - Current mocks in test fixtures; production needs actual data feeds
- **User authentication flow** - JWT auth present, but full user management incomplete
- **Frontend integration** - Backend complete, frontend separate repo

## 4. Completed Features

- ✅ 7-Gate deployment-hardened decision pipeline
- ✅ Position lifecycle (OPEN → CLOSED with P&L)
- ✅ Provenance chain with attribution and learning events
- ✅ CEO governance with persistent memory
- ✅ Mouna emotional-state awareness
- ✅ Risk governor with fail-closed behavior
- ✅ Market provider abstraction layer
- ✅ Institutional strategy engine
- ✅ Database with Alembic migrations
- ✅ 16 core tests passing

## 5. Partially Completed Features

- **Trading UI** - backend complete, frontend exists but integration incomplete
- **Strategy Marketplace** - API exists but frontend less polished
- **Memecoin Engine** - prototype exists but needs refinement
- **Knowledge Base** - ChromaDB integration works but needs production tuning

## 6. Abandoned or Superseded Decisions

- **Gemini credential** - Exposed, must rotate (guardrail)
- **Synthetic fallback responses** - Removed per P0-5 fix
- **Old chromadb schema** - Dropped in favor of 0.4.14

## 7. Assumptions Needing Verification

- ✅ God-mode learning cycle `/god-cycle` endpoint works correctly in production
  - Returns real market data from Yahoo Finance (AAPL @ $344.63, TSLA @ $399.81, MSFT verified)
  - Full provenance chain intact with decision_id, vote, debate, CEO decision
- Redis connectivity for circuit breaker ⚠️ Optional - fallback to in-memory
- PostgreSQL production database migrations ✅ Applied via Alembic
- Render deployment health checks ⚠️ SERVICE NEEDS MANUAL RESTART

## 8. Contradictions Between Documentation and Code

None currently - codebase aligns with the archaeological reports. The FINAL_DELIVERY_REPORT.txt from the TradeSmartAI phase represents older work; current codebase is Yantra X with 7-Gate architecture.

---

## Key Technical Decisions

| Decision | Rationale | Status |
|----------|-----------|--------|
| ChromaDB 0.4.14 | Simpler schema, no external dependencies | Implemented |
| Pydantic 2.5.1 | Type safety,ydantic-core 2.14.3 | Implemented |
| Fail-closed pipeline | Financial correctness over availability | Implemented (Gates 1, 0) |
| SQLAlchemy 2.0 | Modern ORM, async support | Implemented |
| SQLite dev / PostgreSQL prod | Dev simplicity, prod scalability | Configured |