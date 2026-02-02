import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { BASE_URL } from '../api/api';
import PainMeter from './PainMeter';
import MarketMoodDial from './MarketMoodDial';
import InstitutionalReport from './InstitutionalReport';
import StrategyMarketplace from './StrategyMarketplace';

const AIFirmDashboard = () => {
  const [firmStatus, setFirmStatus] = useState(null);
  const [personas, setPersonas] = useState([]);
  const [wisdom, setWisdom] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [reportOpen, setReportOpen] = useState(false);
  const [topStrategies, setTopStrategies] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    fetchAIFirmData();
    const interval = setInterval(fetchAIFirmData, 60000); // Update every 1 minute (Global Sync)
    return () => clearInterval(interval);
  }, []);

  const fetchAIFirmData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch AI firm status, Personas, Wisdom, and top strategies in parallel
      const [statusRes, personaRes, wisdomRes, topRes] = await Promise.allSettled([
        fetch(`${BASE_URL}/api/ai-firm/status`).then(r => r.json()),
        fetch(`${BASE_URL}/api/personas`).then(r => r.json()),
        fetch(`${BASE_URL}/api/knowledge/query`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ topic: 'philosophy', max_results: 1 })
        }).then(r => r.json()),
        fetch(`${BASE_URL}/api/strategy/top?limit=3&metric=sharpe`).then(r => r.json())
      ]);

      if (statusRes.status === 'fulfilled') setFirmStatus(statusRes.value);
      if (personaRes.status === 'fulfilled') {
        const personaList = personaRes.value.personas || [];
        setPersonas(personaList);
      }
      if (wisdomRes.status === 'fulfilled') {
        setWisdom(wisdomRes.value.wisdom?.[0]);
      }
      if (topRes.status === 'fulfilled') {
        setTopStrategies(topRes.value.strategies || []);
      }

    } catch (err) {
      console.error('AI Firm data fetch error:', err);
      setError('Failed to load AI firm data');
    } finally {
      setLoading(false);
    }
  };

  if (loading && !firmStatus) {
    return (
      <div className="industrial-panel p-8 flex flex-col items-center justify-center h-48 animate-pulse text-[var(--color-info)]">
        <div className="font-mono text-xl tracking-widest">SYSTEM INITIALIZING...</div>
        <div className="mt-2 text-xs font-mono text-[var(--text-muted)]">ESTABLISHING NEURAL LINK</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="industrial-panel border-[var(--color-danger)] p-6">
        <div className="flex items-center text-[var(--color-danger)]">
          <span className="text-3xl mr-4">⚠️</span>
          <div>
            <h3 className="font-bold tracking-wider">SYSTEM CRITICAL ERROR</h3>
            <p className="font-mono text-sm mt-1">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8 pb-12">
      {/* AI Firm Status Overview */}
      <div className="industrial-panel p-8">
        <div className="flex items-center justify-between mb-8 pb-4 border-b border-[var(--border-muted)]">
          <h3 className="text-2xl font-bold flex items-center tracking-tight text-white">
            <span className="w-2 h-2 bg-[var(--color-success)] mr-4 animate-pulse"></span>
            AI FIRM COMMAND CENTER
          </h3>
          <div className="flex items-center space-x-4">
            <div className={`px-4 py-1 text-xs font-mono font-bold uppercase tracking-wider border ${firmStatus?.status === 'fully_operational'
              ? 'text-[var(--color-success)] border-[var(--color-success)] bg-[var(--color-success)]/10'
              : 'text-[var(--color-warning)] border-[var(--color-warning)] bg-[var(--color-warning)]/10'
              }`}>
              {firmStatus?.status?.replace('_', ' ') || 'ACTIVE'}
            </div>
            <button
              onClick={fetchAIFirmData}
              className="p-2 border border-[var(--border-muted)] hover:border-[var(--text-primary)] hover:text-white text-[var(--text-muted)] transition-colors"
              disabled={loading}
            >
              <span className={loading ? "inline-block animate-spin" : ""}>↻</span>
            </button>
          </div>
        </div>

        {firmStatus && (
          <div className="space-y-8">
            {/* KPI Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Total Agents */}
              <div className="bg-[var(--bg-surface)] border border-[var(--border-muted)] p-5 relative overflow-hidden group">
                <div className="absolute top-0 right-0 p-2 text-[var(--text-muted)] opacity-20 text-4xl font-mono">01</div>
                <div className="text-3xl font-bold text-white mb-1 font-mono">
                  {firmStatus.ai_firm?.total_agents || 24}
                </div>
                <div className="text-xs text-[var(--text-muted)] uppercase tracking-wider">Active Neural Agents</div>
                <div className="text-[10px] text-[var(--color-success)] mt-4 font-mono flex items-center">
                  <span className="w-1 h-1 bg-[var(--color-success)] mr-2"></span>
                  SYNC: OPTIMAL
                </div>
              </div>

              {/* Portfolio Value */}
              <div className="bg-[var(--bg-surface)] border border-[var(--border-muted)] p-5 relative overflow-hidden group border-b-2 border-b-[var(--color-success)]">
                <div className="absolute top-0 right-0 p-2 text-[var(--text-muted)] opacity-20 text-4xl font-mono">02</div>
                <div className="text-3xl font-bold text-[var(--color-success)] mb-1 font-mono">
                  ${firmStatus.system_performance?.portfolio_balance?.toLocaleString() || '0'}
                </div>
                <div className="text-xs text-[var(--text-muted)] uppercase tracking-wider">AUM Value</div>
                <div className="text-[10px] text-[var(--color-success)] mt-4 font-mono">
                  SUCCESS RATE: {firmStatus.system_performance?.success_rate || 0}%
                </div>
              </div>

              {/* Active Departments */}
              <div className="bg-[var(--bg-surface)] border border-[var(--border-muted)] p-5 relative overflow-hidden group">
                <div className="absolute top-0 right-0 p-2 text-[var(--text-muted)] opacity-20 text-4xl font-mono">03</div>
                <div className="text-3xl font-bold text-[var(--color-info)] mb-1 font-mono">
                  {Object.keys(firmStatus.ai_firm?.departments || {}).length || 5}
                </div>
                <div className="text-xs text-[var(--text-muted)] uppercase tracking-wider">Operational Depts</div>
                <div className="text-[10px] text-[var(--color-warning)] mt-4 font-mono">
                  FULL MANAGEMENT MODE
                </div>
              </div>
            </div>

            {/* Institutional Wow: Pain Meter & Mood Dial */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <div className="industrial-panel p-6 bg-[var(--bg-surface)]">
                <div className="border-b border-[var(--border-muted)] mb-4 pb-2 flex justify-between items-center">
                  <h4 className="text-xs font-bold text-[var(--text-muted)] uppercase tracking-widest">Market Sentiment Engine</h4>
                  <div className="text-[10px] font-mono text-[var(--color-info)]">MODULE: SENTIMENT</div>
                </div>
                <MarketMoodDial mood={firmStatus.system_performance?.market_mood || 'neutral'} />
              </div>
              <div className="industrial-panel p-6 bg-[var(--bg-surface)] h-full">
                <div className="border-b border-[var(--border-muted)] mb-4 pb-2 flex justify-between items-center">
                  <h4 className="text-xs font-bold text-[var(--text-muted)] uppercase tracking-widest">Strategy Nexus</h4>
                  <div className="text-[10px] font-mono text-[var(--color-info)]">MODULE: STRATEGY</div>
                </div>
                <StrategyMarketplace />
              </div>
            </div>

            {/* Top Strategies (internal) */}
            <div className="p-4 border border-[var(--border-muted)] bg-[var(--bg-deep)]">
              <div className="flex items-center justify-between mb-4">
                <h4 className="text-xs font-bold text-[var(--text-primary)] uppercase tracking-widest pl-2 border-l-2 border-[var(--color-info)]">Top Internal Strategies</h4>
                <button className="text-[10px] font-mono text-[var(--color-info)] hover:underline">VIEW ALL ></button>
              </div>
              <div className="space-y-1">
                {topStrategies.length === 0 ? (
                  <div className="text-xs text-[var(--text-muted)] font-mono italic p-2">CALCULATING PERFORMANCE METRICS...</div>
                ) : (
                  topStrategies.map((s, i) => (
                    <div key={s.id} className="flex items-center justify-between p-3 border-b border-[var(--border-muted)] hover:bg-[var(--bg-surface)] transition-colors group">
                      <div className="flex items-center space-x-4">
                        <span className="text-xs font-mono text-[var(--text-muted)] w-6">0{i + 1}</span>
                        <div className="text-sm text-[var(--text-primary)] font-mono uppercase">{s.name}</div>
                      </div>
                      <div className="text-xs font-mono font-bold text-[var(--color-success)]">SR: {s.metrics?.sharpe ?? '—'}</div>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Loki Swarm Intelligence Grid */}
            <div className="industrial-panel p-6 relative">
              <div className="flex items-center justify-between mb-6 pb-2 border-b border-[var(--border-muted)]">
                <h4 className="text-xs font-bold text-[var(--text-primary)] uppercase tracking-[0.2em]">
                  Loki Swarm Intelligence
                </h4>
                <span className="text-[10px] text-[var(--color-success)] font-mono border border-[var(--color-success)] px-2 py-1">
                  MODE: AUTONOMOUS
                </span>
              </div>

              {/* Render Swarms */}
              <div className="space-y-6">
                {firmStatus.ai_firm?.departments && Object.entries(firmStatus.ai_firm.departments).map(([key, swarm]) => (
                  <div key={key} className="bg-[var(--bg-deep)] p-4 border border-[var(--border-muted)]">
                    <h5 className="text-sm font-bold text-[var(--color-info)] uppercase mb-3 font-mono">{swarm.swarm || key}</h5>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                      {swarm.agents && Object.entries(swarm.agents).map(([agentName, state]) => (
                        <div key={agentName} className="flex items-center justify-between p-2 bg-[var(--bg-surface)] border border-[var(--border-muted)]">
                          <span className="text-xs font-mono text-white">{agentName}</span>
                          <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${state === 'IDLE' ? 'text-[var(--text-muted)] bg-[var(--text-muted)]/10' :
                              state === 'VERIFYING' ? 'text-[var(--color-success)] bg-[var(--color-success)]/10 animate-pulse' :
                                state === 'ERROR' ? 'text-[var(--color-danger)] bg-[var(--color-danger)]/10' :
                                  'text-[var(--color-info)] bg-[var(--color-info)]/10'
                            }`}>
                            {state}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>

              <div className="flex justify-between text-[10px] text-[var(--text-muted)] mt-4 font-mono uppercase tracking-wider">
                <span>Architecture: SWARM V2</span>
                <span>Cycle: RARV (Reason-Act-Reflect-Verify)</span>
              </div>
            </div>

            {/* CEO Reasoning & Ghost Whispers */}
            {wisdom && (
              <div className="border border-[var(--border-muted)] bg-[var(--bg-surface)] p-6 relative overflow-hidden">
                <div className="absolute top-0 left-0 w-1 h-full bg-[var(--color-info)]"></div>
                <h4 className="text-xs font-bold text-[var(--color-info)] mb-3 flex items-center uppercase tracking-widest">
                  Institutional Wisdom
                </h4>
                <div className="text-lg text-[var(--text-primary)] leading-relaxed font-serif italic pl-4">
                  "{wisdom.text || "Boond boond se ghada bharta hai."}"
                </div>
                <div className="mt-4 text-[10px] text-[var(--text-muted)] font-mono uppercase tracking-widest pl-4">
                  — {wisdom.metadata?.source || "YantraX Core DNA"}
                </div>
              </div>
            )}

            {/* Institutional Phase Ω: Action Bar */}
            <div className="flex items-center justify-center pt-8 pb-4">
              <button
                onClick={() => setReportOpen(true)}
                className="btn-cyber-primary text-sm px-8 py-4 tracking-widest"
              >
                GENERATE INSTITUTIONAL INTELLIGENCE REPORT
              </button>
            </div>
          </div>
        )}

        <InstitutionalReport
          symbol="AAPL"
          isOpen={reportOpen}
          onClose={() => setReportOpen(false)}
        />
      </div>

      {/* Named Personas Analysis */}
      <h3 className="text-lg font-bold text-[var(--text-primary)] uppercase tracking-wider pl-4 border-l-4 border-[var(--color-info)]">
        Key Persona Analysis
      </h3>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {personas.map((persona) => (
          <div key={persona.name} className="industrial-panel p-0 group">
            <div className="p-6 border-b border-[var(--border-muted)] bg-[var(--bg-surface)] flex justify-between items-start">
              <div>
                <h4 className="text-xl font-bold text-white capitalize font-mono">{persona.name}</h4>
                <p className="text-xs text-[var(--text-muted)] uppercase tracking-widest mt-1">{persona.role}</p>
              </div>
              <div className="text-2xl opacity-50 grayscale group-hover:grayscale-0 transition-all">
                {persona.name === 'warren' ? '👴' :
                  persona.name === 'cathie' ? '🚀' :
                    persona.name === 'macro_monk' ? '🧘' :
                      persona.name === 'the_ghost' ? '👻' :
                        persona.name === 'degen_auditor' ? '🔍' : '🤖'}
              </div>
            </div>

            <div className="p-6 space-y-4">
              <div className="flex items-center justify-between p-3 border border-[var(--border-muted)] bg-[var(--bg-deep)]">
                <span className="text-xs text-[var(--text-muted)] font-mono uppercase">Conviction</span>
                <span className={`text-sm font-bold font-mono ${persona.confidence > 0.8 ? 'text-[var(--color-success)]' : 'text-[var(--color-warning)]'}`}>
                  {(persona.confidence * 100).toFixed(0)}%
                </span>
              </div>

              <div className="p-4 border-l-2 border-[var(--border-muted)]">
                <p className="text-[10px] text-[var(--text-muted)] uppercase tracking-widest mb-2 font-bold flex items-center">
                  Target Focus
                </p>
                <p className="text-sm text-[var(--text-secondary)] leading-relaxed font-mono">
                  Agents in the <span className="text-white">{persona.department?.replace('_', ' ') || 'core'}</span> department are currently monitoring {persona.specialty?.toLowerCase() || 'market'} patterns.
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default AIFirmDashboard;
