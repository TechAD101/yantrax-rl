# YantraX RL: Comprehensive Bug Report & Missing Pieces

This document outlines the identified errors, architectural mismatches, and missing components that are preventing the YantraX RL application from being fully operational.

## 1. Critical Environment & Configuration Issues
- **Missing API Keys**: The backend requires `FMP_API_KEY` (Financial Modeling Prep) and `GEMINI_API_KEY` (Google Gemini) to function. Without these, market data and AI insights (Oracle, Debate) fail.
- **Hardcoded URLs**: The frontend `api.js` was hardcoded to a production Render URL, causing local development to fail until manually updated.
- **Dependency Mismatches**: Some backend dependencies in `requirements.txt` were missing or had version conflicts during initial setup.

## 2. Frontend-Backend Contract Mismatches (AI Firm Dashboard)
| Component | Frontend Expects | Backend Returns | Status |
| :--- | :--- | :--- | :--- |
| **WisdomOracle** | `wisdom.text`, `wisdom.metadata.source` | `whisper`, `perspective`, `confidence` | **BROKEN** |
| **InstitutionalReport** | `report.markdown` | `report` (string) | **BROKEN** |
| **AIFirmDashboard** | `personaData.value.personas` | `personas` (top-level) | **PARTIAL** |
| **SynapticMatrix** | `agents` array with specific fields | `all_agents` (nested in `ai_firm`) | **PARTIAL** |

## 3. Missing or Inconsistent API Routes
- **Risk Metrics**: Frontend calls `api.getRiskMetrics()`, but no `/api/risk-metrics` route exists in `main.py`.
- **Performance**: Frontend calls `api.getPerformance()`, but no `/api/performance` route exists in `main.py`.
- **Strategy Marketplace**: The frontend expects `api.getTopStrategies()`, but the backend route `/api/strategy/top` has strict database requirements that may fail if the DB is not initialized.
- **Voting History**: Frontend calls `/api/ai-firm/voting-history`, but the backend implementation in `agent_manager.py` might return empty lists if no cycles have run.

## 4. Logic & Architectural Bugs
- **Agent Manager Duplication**: `agent_manager.py` defines `macro_monk` and `degen_auditor` twice in the `_initialize_20_plus_agents` method, leading to overwrites.
- **Async/Sync Conflicts**: The `get_oracle_wisdom` route in `main.py` attempts to run an async loop inside a sync Flask route using `asyncio.run_until_complete`, which can cause issues in certain WSGI environments.
- **Fallback Data**: Many components rely on hardcoded fallback data (e.g., AUM of $2,491,082) because the backend doesn't yet provide real-time portfolio calculations.

## 5. Vision Alignment Gaps
- **20+ Agent Integration**: While the `AgentManager` defines 20+ agents, the `PersonaRegistry` only registers 6. The "Institutional" feel is missing because many agents are currently placeholders.
- **The Ghost Layer**: The "Divine Doubt" protocol is implemented in the backend but its visual representation in the frontend (Synaptic Matrix) is static and doesn't reflect real-time "Ghost" interventions.
- **Philosophy Integration**: The `PhilosophyManager` is defined but not deeply integrated into the main trading loop or visible in the frontend "Market Mood" as intended.
