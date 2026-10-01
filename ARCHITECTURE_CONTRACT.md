# Yantra X Architecture Contract

## Purpose

Yantra X contains several generations of AI-firm code. This document defines the current canonical decision path and the boundaries between live market evidence, intelligence, governance, simulation, and legacy compatibility code.

## Canonical decision path

The authoritative trading-decision flow is:

Market-data provider
-> MarketSnapshot
-> EvidenceSynthesizer
-> InstitutionalStrategyEngine
-> AgentManager voting
-> DebateEngine
-> AutonomousCEO governance
-> RiskGovernor
-> PositionSizer
-> final decision
-> execution boundary

The canonical pipeline is `backend/core/decision_pipeline.py`.

A decision pipeline instance must receive an explicit market-data provider. It must not silently import or substitute a global provider, dummy provider, cached fabricated value, or synthetic market-data source.

## Market-data providers

The allowed market-data entry points are:

- Alpaca: primary production/future-use market-data provider.
- FYERS: current testing/staging broker/data integration; isolated in `backend/services/fyers_broker.py`.

FYERS live order placement is explicitly opt-in and is not the default execution path.

The canonical market-data layer must fail closed when required market evidence is unavailable.

## Evidence

`EvidenceSynthesizer` is the canonical adapter into `EvidencePackage`.

Evidence must be sourced from provider-backed data or explicitly supplied deterministic test fixtures.

Missing evidence must not be replaced by plausible-looking financial or market values.

Examples of prohibited decision evidence include invented P/E, ROE, debt/equity, growth, free-cash-flow, random price, random volume, or random sentiment.

## InstitutionalStrategyEngine

`backend/services/institutional_strategy_engine.py` is the canonical strategy calculation layer.

Its responsibilities are:

- regime detection
- technical analysis
- sentiment integration when real sentiment evidence exists
- fundamental scoring when real fundamentals exist
- signal confidence
- candidate action
- candidate sizing/exits

The strategy engine is not the market-data provider.

Strategy-engine exceptions must be observable and must not silently turn a valid decision into a different methodology merely to keep execution moving.

## AgentManager

`backend/ai_firm/agent_manager.py` is the current 20+ agent coordination layer.

Agent votes are advisory evidence for governance. They are not a replacement for the strategy candidate.

Agent metadata such as historical confidence/performance is model configuration, not evidence that a live trade is profitable.

## DebateEngine

`backend/ai_firm/debate_engine.py` provides structured debate/dissent and produces a canonical debate result.

The canonical pipeline runs debate once and passes that result into CEO governance. CEO must not silently rerun an independent debate for the same pipeline decision.

## The Ghost / Divine Doubt

`backend/ai_firm/ghost_layer.py` is a meta-governance layer.

Its intended role is to challenge excessive certainty, identify extreme disagreement, and provide warnings/veto-oriented signals.

Divine Doubt is not a market-data source and must not manufacture market evidence.

A Ghost nudge may alter governance/confidence only through explicit, auditable rules. It must not silently rewrite a strategy direction merely because consensus is high.

The Ghost contains a probabilistic non-linear insight path; that path must not become an untracked source of trade direction or fabricated market facts.

## AutonomousCEO

`backend/ai_firm/ceo.py` is the governance/oversight layer.

CEO `decision_type` is a workflow classification, not BUY/SELL/HOLD direction.

The explicit strategy action is carried separately as `strategy_action`.

CEO may govern, veto, or enter defensive lockdown under explicit rules, while preserving the separation between governance state and trade direction.

## MarketSentimentService

`backend/services/market_sentiment_service.py` is legacy/synthetic infrastructure in its current form.

It currently contains simulated/random implementations for several sentiment components. Therefore it is not authoritative live evidence.

It may remain temporarily for compatibility/tests, but its output must not be treated as real market evidence in a live/canonical decision path until each component is replaced by an identified real data source with provenance.

## DataWhisperer

`backend/ai_agents/data_whisperer.py` belongs to the older `backend/ai_agents` generation.

It contains synthetic/random fallbacks for price, volume, technical values, volatility, and sentiment.

It is not the canonical market-data provider and must not feed live trade decisions through fallback simulation.

It can be retained for legacy compatibility only until its callers are retired or it is rewritten around provider-backed evidence.

## Legacy versus current AI-firm generations

Two major generations coexist:

1. `backend/ai_agents/` — older persona/agent implementation family.
2. `backend/ai_firm/` — current orchestration/governance family used by the canonical decision pipeline.

Do not assume similarly named classes across these directories are interchangeable.

`backend/app/` is a newer application skeleton and is not currently the canonical trading pipeline.

## Simulation

RL/backtesting/paper-trading simulation is valid when explicitly named and isolated.

Simulation must never masquerade as real market evidence.

Paper execution through the existing order manager is simulation and must remain distinct from future broker execution.

## Position sizing

`DecisionContext.final_position_size` and `SizingResult.position_size` represent dollar/notional value.

`SizingResult.quantity` represents units/shares/contracts.

These units must not be multiplied by price twice or mixed with quantity-based risk calculations.

Sizing-method failures must fail closed or surface an explicit error. They must not silently switch to another methodology.

## Provider provenance

The system should preserve, where available:

- provider
- verification status
- timestamp/data age
- evidence source
- error reason when evidence is unavailable

A plausible value without provenance is not equivalent to verified market evidence.

## Test philosophy

A test fixture may be deterministic and synthetic, but it must clearly be a fixture.

Tests should prove architecture contracts such as:

- missing provider -> ABSTAIN
- missing required evidence -> no fabricated substitute
- sizing dependency failure -> explicit failure
- CEO preserves explicit strategy direction
- Ghost modifies governance only through documented rules

Tests must not weaken production thresholds simply to make CI pass.

## Historical context

Repository history contains earlier attempts to deploy/force-redeploy the AI Firm, legacy fallback systems, and prior Ghost/persona failures.

Historical commits are useful for understanding intent and failure modes, but current source plus tests are authoritative for current behavior.

## Security

Credentials and API keys do not belong in Git.

Removing a secret from the current tree does not remove it from Git history; historical credentials must be revoked/rotated separately.

## Future broker architecture

The intended future execution boundary is:

DecisionPipeline
-> canonical OrderIntent
-> broker adapter
-> Paper / Alpaca / FYERS execution mode

No broker integration should silently switch the system from paper to live execution.
