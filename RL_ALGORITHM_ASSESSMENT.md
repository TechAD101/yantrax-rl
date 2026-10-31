# Yantra X — RL Trainer: Algorithm, Limitations, and Safe Gating

**Last Updated:** 2026-10-30
**Status:** Prototype — not integrated into the canonical decision path.

---

## 1. What Actually Exists

### `backend/rl_core/env_market_sim.py` — `MarketSimEnv`
- Starts at a **random price** (`random.uniform(20000, 30000)`) and evolves via **random Gaussian price changes** (`random.gauss(0, volatility)`).
- Mood-driven volatility amplification (euphoric, panic, bored, crisis) is a **synthetic behavioral model**, not derived from real market data.
- No OHLCV history, no provider-backed replay, no corporate-action handling, no transaction costs beyond a fixed 0.1 fee.
- **Classification:** Explicitly labeled synthetic research fixture. Not real market data.

### `backend/rl_core/rl_trainer.py` — `PPOAgent`
- Named `PPOAgent` but implements a **simplified linear policy-gradient**:
  - Policy/value "networks" are plain `np.random.randn` weight matrices (no hidden layers, no nonlinearity beyond softmax).
  - `train()` computes TD advantages and applies a **hand-rolled gradient update** (`_calculate_policy_gradient`) — no automatic differentiation, no backprop.
  - The PPO clipped objective (`min(ratio * A, clipped_ratio * A)`) is computed, but the update step uses a simplified manual gradient rather than the true PPO gradient.
- **Classification:** Prototype with PPO-shaped loss, not mathematically valid PPO. **Do not label as production PPO.**

### `backend/rl_core/reward_function.py`
- Reward shaping helper used by `MarketSimEnv.step()`. Purely synthetic.

---

## 2. Relationship to the Canonical Decision Path

**The RL trainer is NOT connected to the production pipeline.**

Verified by grep across `backend/core/`, `backend/main.py`, and `backend/ai_firm/`: no file imports `PPOAgent`, `AdvancedRLTrainer`, `MarketSimEnv`, or `env_market_sim`. The canonical path (`DecisionPipeline`) uses:

```
Market-data provider → MarketSnapshot → EvidenceSynthesizer →
InstitutionalStrategyEngine → AgentManager voting → DebateEngine →
AutonomousCEO governance → RiskGovernor → PositionSizer →
final decision → paper execution → position lifecycle →
realized outcome → attribution → learning
```

The RL components are standalone research fixtures. They have **no influence** on production decisions, risk gates, or execution authority.

---

## 3. Honest Labeling

| Claim | Verdict |
|-------|---------|
| "The system has a self-improving RL policy" | **False.** The trainer runs in isolation on synthetic data. |
| "PPOAgent implements PPO" | **Misleading.** It computes a PPO-shaped clipped objective but uses simplified manual gradients, not valid PPO. |
| "MarketSimEnv models real markets" | **False.** Pure synthetic random walk with mood-driven amplification. |
| "RL policy can override canonical decisions" | **False.** No integration exists; no override path exists. |

---

## 4. Required Gating (per ARCHITECTURE_CONTRACT)

Until out-of-sample evaluation is accepted:

1. **No RL policy may enter the canonical decision path.** Integration requires an explicit `research`/`shadow`/`paper` feature gate.
2. **RL must not change risk gates or gain execution authority** merely because training completed.
3. **A defined out-of-sample acceptance threshold and human-reviewed promotion** is required before any RL output can influence production.
4. **Policy versioning, training data windows, feature definitions, model hashes, metrics and checkpoints** must be preserved with rollback capability.

---

## 5. Path Forward (not yet implemented)

To move from prototype to defensible evolutionary learning:

- **Deterministic historical replay** with provider-backed OHLCV (requires market-data credentials, currently unavailable).
- **Realistic cost modeling**: commissions, spread, slippage, position sizing, risk constraints.
- **No look-ahead leakage**: chronological train/validation/test splits with walk-forward evaluation.
- **Baseline comparison**: no-trade and simple benchmark strategy; evaluate returns, drawdown, risk-adjusted performance, turnover, fees, stability across regimes — not reward alone.
- **Valid PPO**: either replace with a maintained, tested implementation compatible with the deployment environment, or clearly retain as prototype.

**Current blocker:** No FYERS/Alpaca credentials available. Provider-backed historical replay is blocked. This does not affect the canonical decision path's fail-closed behavior, which is verified working.