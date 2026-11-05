# PR #139: Phase 1 Remediation - JWT & Ghost Governance Fixes

**Branch:** `phase1-remediation-jwt-prod`  
**Current SHA:** `234dd9a64eace14cf488ec123d4f8bf36338a8c7`

## Summary

This PR addresses all 6 acceptance failures for Phase 1 remediation:

1. **Real API lifecycle test** - Replaced synthetic mocks with actual three-request API test
2. **Learning timing assertions** - Added database-level verification of learning event generation
3. **Ghost governance tests** - Added deterministic tests for Ghost intervention scenarios
4. **Migration fixes** - Corrected migration chain, removed duplicate journal_entries
5. **Repository hygiene** - Removed chroma_db artifacts, verified security validation
6. **PR documentation** - Updated with accurate current SHA

---

## Changes

### Backend (`backend/`)

#### `ai_firm/ceo.py`
- Added `action`, `ghost_nudge`, `pain_level`, `market_mood` fields to `CEODecision` dataclass
- Fixed Ghost advisory logic: preserves `candidate_strategy.action` for DIVINE_DOUBT/DISSSENT/CAUTION_NUDGE cases instead of defaulting to HOLD

#### `alembic/versions/20260108_add_strategies_portfolios.py`
- Fixed `down_revision = None` → `down_revision = '0001_create_journal_entries'`
- Removed duplicate `journal_entries` table creation
- Now correctly creates only `strategy_profiles` and `strategies` tables

#### `main.py`
- Added `scenario` parameter to `/god-cycle` endpoint
- Added `scenario` parameter to `/run-cycle` endpoint
- JWT_SECRET_KEY validation: rejects 32+ known placeholder values
- API_ACCESS_KEY validation: enforces 16+ char minimum, rejects placeholders

#### `services/synthetic_market_provider.py`
- Rewrote bearish_decline scenario with complete technical indicators (EMA, MACD, RSI, Bollinger)
- bullish_mean_reversion produces: composite_sentiment=0.68, confidence=0.75
- bearish_decline produces: composite_sentiment=0.28 (BEARISH)

#### `services/knowledge_base.py`
- Added graceful fallback for chromadb import errors

### Tests (`tests/`)

#### `test_synthetic_full_lifecycle.py` (NEW: 339 lines)
Three-request API test using Flask test client:
1. Request 1: Opens BUYI position (bullish scenario, `/god-cycle?scenario=bullish_mean_reversion`)
2. Request 2: Verifies same position persists
3. Request 3: Closes via bearish scenario (`/god-cycle?scenario=bearish_decline`)

Assertions:
- No learning events before closure
- After closure: verified P&L, Outcome, Attribution, provenance, LearningEvent
- Learning only from realized outcome
- No MockStrategyEngine usage

#### `test_migrations.py` (NEW: 166 lines)
Migration integrity tests:
- `test_clean_migration_vs_isolated_db` - Fresh DB migration verification
- `test_no_duplicate_journal_entries` - Duplicate prevention
- `test_migration_chain_correct` - Chain validation
- `test_no_automatic_stamp_head` - CI failure visibility

#### `test_god_cycle.py` (existing, 9 passing tests)
Includes deterministic Ghost governance tests:
- BUY without Ghost challenge → succeeds
- DIVINE_DOUBT → advisory nudge, position survives
- DISSSENT → advisory signal, not hard veto
- Ghost VETO → confidence reduction, not action change
- Risk Governor veto → blocks when truly risky

#### `mock_strategy_engine.py` (DELETED)
- Removed mock; synthetic provider handles all scenarios natively

---

## Test Results

```
tests/test_migrations.py::TestMigrations::test_clean_migration_vs_isolated_db PASSED
tests/test_migrations.py::TestMigrations::test_no_duplicate_journal_entries PASSED
tests/test_migrations.py::TestMigrations::test_migration_chain_correct PASSED
tests/test_migrations.py::TestMigrations::test_no_automatic_stamp_head PASSED

tests/test_synthetic_full_lifecycle.py::test_lifecycle_opens_buy_position PASSED
tests/test_synthetic_full_lifecycle.py::test_same_position_persists PASSED
tests/test_synthetic_full_lifecycle.py::test_position_closes_on_bearish_signal PASSED
tests/test_synthetic_full_lifecycle.py::test_learning_timing_correct PASSED
tests/test_synthetic_full_lifecycle.py::test_realized_pnl_verified PASSED
tests/test_synthetic_full_lifecycle.py::test_outcome_attribution_preserved PASSED
tests/test_synthetic_full_lifecycle.py::test_learning_from_realized_outcome PASSED

tests/test_god_cycle.py::9 tests PASSED

Total: 20 passed
```

---

## Security Validation

### JWT_SECRET_KEY
- Minimum 32 characters required in production
- Must contain at least one digit and one letter
- Rejects 32 known placeholder values (changeme, your-secret-key-here, dev, test, placeholder, example, demo, password, secret, default-secret, etc.)
- Timing-safe comparison prevents timing attacks

### API_ACCESS_KEY
- Minimum 16 characters required
- Must contain at least one digit and one letter
- Rejects known placeholder values

---

## Limitations

1. **Paper trading only** - No live market data or credentials in tests
2. **Phase 1 synthetic fixtures only** - Tests use deterministic synthetic market scenarios
3. **No Phase 2 integration** - External data providers not included
4. **chromadb** - Removed from repository (handled by knowledge_base.py graceful fallback)
5. **Ghost intervention** - Advisory influence only; does not unconditionally veto positions

---

## Verification Steps

1. All tests pass: `pytest tests/test_migrations.py tests/test_synthetic_full_lifecycle.py tests/test_god_cycle.py -v`
2. Migration chain verified: `alembic history` shows 0001 → 20260108 → 20260108_add_memecoins → 20261030
3. No chroma_db artifacts in repository
4. JWT/API key validation code properly rejects predictable values

---

## Checklist

- [x] Real API lifecycle test (3-request)
- [x] Learning timing assertions
- [x] Ghost governance deterministic tests
- [x] Migration fixes (chain, duplicate journal_entries)
- [x] Repository hygiene (removed chroma_db)
- [x] JWT secret validation verified
- [x] API_ACCESS_KEY deployment documented
- [x] PR description updated with SHA `234dd9a`
- [x] All 20 tests passing

---

**Ready for founder review.**