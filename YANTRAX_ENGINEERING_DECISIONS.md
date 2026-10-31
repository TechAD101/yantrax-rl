# YANTRA X ENGINEERING DECISIONS

## Version Controlled Architecture Decisions

### AD-001: Multi-Gate Decision Pipeline Architecture

**Status**: Accepted (Gates 0-7 implemented)

**Context**: Need for fail-closed, auditable trading decisions with progressive hardening.

**Decision**: Implement 7-Gate architecture:
- Gate 0: Security hardening (CORS allowlist, JWT auth, secret rotation)
- Gate 1: Fail-closed decision pipeline
- Gate 2: Position state persistence
- Gate 3: CEO memory persistence
- Gate 4: Honest agent labeling (configured vs measured)
- Gate 6: Market data verification heartbeat
- Gate 7: Deployment with SHA verification

**Consequences**:
- ✅ Extremely reliable decision flow
- ✅ Full audit trail
- ⚠️ Added complexity in code paths
- ⚠️ More testing overhead

### AD-002: Genuine Paper-Trading Lifecycle

**Status**: Accepted (Phase 5.2 complete)

**Context**: Need to earn the right to use models in production through realized outcomes.

**Decision**: Implement OPEN → CLOSED position lifecycle:
- Positions created as OPEN (no P&L)
- Updated to CLOSED with realized P&L
- Attribution and learning events only after realized outcomes
- Never present unverified performance

**Consequences**:
- ✅ Prevents performance inflation
- ✅ Creates learning signal quality
- ⚠️ Slower iteration on strategies
- ⚠️ More database writes

### AD-003: Provenance Chain Model

**Status**: Accepted

**Context**: Need complete traceability from decision to outcome.

**Decision**: Provenance chain:
```
decision_id → order_id → entry_fill_id → outcome_id → attribution_ids[] → learning_event_ids[]
```

Backward compatible: `attribution_id` and `learning_event_id` store first elements for quick joins.

**Consequences**:
- ✅ Full audit trail for compliance
- ✅ Agent contribution tracking
- ⚠️ Complex joins in analytics queries

### AD-004: ChromaDB for Knowledge Base

**Status**: Accepted

**Context**: Need vector search for agent context enrichment.

**Decision**: Use ChromaDB 0.4.14 with persisted SQLite backend.

**Consequences**:
- ✅ No external vector DB dependencies
- ✅ Local persistence survives restarts
- ⚠️ Schema migration pain when upgrading
- ⚠️ Telemetry errors in logs (acceptable)

### AD-005: Pydantic 2.5.1 Type System

**Status**: Accepted

**Context**: Need type safety with modern Python features.

**Decision**: Use Pydantic 2.x for all data models with:
- Computed fields for derived properties
- Field validation on all inputs
- JSON schema generation for API docs

**Consequences**:
- ✅ Better type safety
- ✅ Cleaner API contracts
- ⚠️ Migration cost from Pydantic v1
- ⚠️ Some legacy `.get()` SQLAlchemy warnings

### AD-006: Fail-Closed Risk Controls

**Status**: Accepted

**Context**: Financial correctness over availability is paramount.

**Decision**: Any critical failure results in ABSTAIN, never fallback to incorrect behavior.

**Consequences**:
- ✅ No silent failures
- ✅ Protected capital at risk
- ⚠️ More manual intervention required

### AD-007: Agent Memory Without LLM Summary

**Status**: Accepted

**Context**: Context compression made previous session history unavailable.

**Decision**: Use OpenViking for durable indexed memory in addition to database persistence.

**Consequences**:
- ✅ Recovery from context loss
- ✅ Semantic search over past decisions
- ⚠️ Additional infrastructure dependency

## Pending Decisions

### PD-001: Model Versioning System

**Context**: Need to track agent/model improvements over time.

**Options**:
1. File-based versioning in Git
2. Database-stored versions
3. Dedicated model registry service

**Recommendation**: Database-stored versions (simple, queryable)

### PD-002: Multi-Provider Market Data

**Context**: Single provider creates single point of failure.

**Options**:
1. Primary + backup pattern
2. Round-robin across providers
3. Vote-based consensus

**Recommendation**: Primary + backup with health checks

### PD-003: User Portfolio Isolation

**Context**: Need to support multiple users without cross-contamination.

**Options**:
1. Database-level tenant isolation
2. Row-level security with user_id
3. Separate databases per user

**Recommendation**: Row-level security (simpler, scalable to ~10k users)

## Guardrail Decisions

| Guardrail | Status | Implementation |
|-----------|--------|----------------|
| Paper trading only | ✅ | No live brokerage integration |
| No fabricated evidence | ✅ | All prices from verified sources |
| Fail-closed on missing evidence | ✅ | ABSTAIN if data unavailable |
| Preserve Mouna governance | ✅ | Emotional-state tracking intact |
| Learning from realized outcomes | ✅ | Only after OPEN→CLOSED |
| Persistent memory | ✅ | Database + ChromaDB |
| Idempotent event processing | ✅ | UUID-based IDs |
| Production durability | ✅ | PostgreSQL + backups |
| Authenticated writes | ✅ | JWT required |
| User isolation | ⚠️ | Partial (user_id field exists) |
| No credential exposure | ✅ | .env protection |
| Rotate exposed Gemini keys | ⚠️ | Pending founder confirmation |
| $5 OpenRouter cap | ✅ | Configured in env |
| No unauthorized /god-cycle | ✅ | Requires auth |
| No security control bypass | ✅ | No bypass mechanisms |

## Debt Items

### High Priority Debt
1. SQLAlchemy `.get()` legacy API warnings
2. PostHog telemetry errors (ChromaDB)
3. Missing ML dependencies (torch, transformers)

### Medium Priority Debt
1. No CI/CD pipeline configured
2. Test fixtures use hardcoded deterministic data
3. No performance testing baseline

### Low Priority Debt
1. Frontend documentation gaps
2. API documentation regeneration needed
3. README needs update for current architecture