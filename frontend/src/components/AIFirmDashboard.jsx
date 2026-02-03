import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/api';
import PainMeter from './PainMeter';
import MarketMoodDial from './MarketMoodDial';
import InstitutionalReport from './InstitutionalReport';
import StrategyMarketplace from './StrategyMarketplace';
import IntelligencePanel from './IntelligencePanel';
import WisdomPulse from './WisdomPulse';
import NeuralSpine from './NeuralSpine';

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

      // Using standardized API client for architecture consistency
      const [statusData, personaData, wisdomData, topData] = await Promise.allSettled([
        api.getAIFirmStatus(),
        api.getPersonas(),
        api.queryKnowledge('philosophy', null),
        api.getTopStrategies({ limit: 3, metric: 'sharpe' })
      ]);

      if (statusData.status === 'fulfilled') setFirmStatus(statusData.value);
      if (personaData.status === 'fulfilled') {
        const personaList = personaData.value.personas || [];
        setPersonas(personaList);
      }
      if (wisdomData.status === 'fulfilled') {
        setWisdom(wisdomData.value.wisdom?.[0]);
      }
      if (topData.status === 'fulfilled') {
        setTopStrategies(topData.value.strategies || []);
      }

    } catch (err) {
      console.error('AI Firm data fetch error:', err);
      setError('Failed to load AI firm data');
    } finally {
      setLoading(false);
    }
  };

  if (loading && !firmStatus) return (
    <div className="min-h-screen bg-black flex items-center justify-center p-8">
      <div className="flex flex-col items-center">
        <div className="w-16 h-16 border-t-2 border-b-2 border-[var(--color-info)] animate-spin rounded-full mb-6"></div>
        <div className="text-[var(--color-info)] font-mono text-sm tracking-[0.3em] uppercase animate-pulse">
          Initializing Synaptic Matrix...
        </div>
      </div>
    </div>
  );

  if (error) return (
    <div className="min-h-screen bg-black flex items-center justify-center p-8 text-red-500 font-mono text-center">
      SYSTEM FAILURE: {error}
    </div>
  );

  const isPanic = firmStatus?.system_performance?.is_in_panic || false;
  const painLevel = firmStatus?.system_performance?.pain_level || 0;

  return (
    <div className={`min-h-screen bg-black text-[#e2e8f0] transition-colors duration-1000 cursor-pointer-all ${isPanic ? 'bg-red-950/20' : ''}`}>
      <div className="flex h-screen overflow-hidden">
        {/* Left Side: Neural Spine (Visual Anchor) */}
        <NeuralSpine painLevel={painLevel} isPanic={isPanic} />

        {/* Main Fluid Content */}
        <div className="flex-1 overflow-y-auto scrollbar-hide">
          <div className="max-w-[1600px] mx-auto p-4 md:p-8 space-y-8 relative">

            {/* Panic Mode / Mouna Overlay */}
            {isPanic && (
              <div className="absolute inset-0 z-[100] bg-red-950/40 backdrop-blur-sm flex items-center justify-center p-12 animate-fade-in border-4 border-red-500/20 m-4 pointer-events-none">
                <div className="industrial-panel bg-black border-red-600 p-10 max-w-2xl text-center pointer-events-auto shadow-[0_0_50px_rgba(239,68,68,0.3)]">
                  <h2 className="text-4xl font-bold text-red-500 mb-4 tracking-tighter uppercase font-mono">Mouna Mode Active</h2>
                  <p className="text-xl text-red-200/80 mb-6 font-serif italic">
                    "When the mirror is shattered by chaos, the sage stays silent."
                  </p>
                  <div className="text-sm text-red-400 font-mono uppercase tracking-[0.2em] mb-8">
                    Drawdown Threshold Exceeded // Systemic Restraint Engaged
                  </div>
                  <div className="h-1 bg-red-900 w-full overflow-hidden">
                    <div className="h-full bg-red-500 animate-pulse"></div>
                  </div>
                </div>
              </div>
            )}

            {/* Dashboard Header */}
            <div className="flex flex-col md:flex-row md:items-end justify-between border-b border-[var(--border-muted)] pb-6 gap-4">
              <h3 className="text-2xl font-bold flex items-center tracking-tight text-white uppercase">
                <span className={`w-2 h-2 mr-4 animate-pulse ${isPanic ? 'bg-red-500' : 'bg-[var(--color-success)]'}`}></span>
                AI Firm Command Center
              </h3>
              <div className="flex items-center space-x-4">
                <div className={`px-4 py-1 text-xs font-mono font-bold uppercase tracking-wider border transition-colors duration-500 ${isPanic
                  ? 'text-red-500 border-red-500 bg-red-500/10'
                  : 'text-[var(--color-success)] border-[var(--color-success)] bg-[var(--color-success)]/10'
                  }`}>
                  {isPanic ? 'MOUNA_MODE' : (firmStatus?.status?.replace('_', ' ') || 'ACTIVE')}
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

            {/* AI Firm Status Overview */}
            <div className="industrial-panel p-8">
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
                      <div className="text-[10px] text-[var(--color-warning)] mt-4 font-mono uppercase">
                        Full Synaptic Management
                      </div>
                    </div>
                  </div>

                  {/* Institutional Wow: Pain Meter & Mood Dial */}
                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    <div className="neon-card p-6 bg-[var(--bg-surface)]">
                      <div className="border-b border-[var(--border-muted)] mb-4 pb-2 flex justify-between items-center">
                        <h4 className="text-xs font-bold text-[var(--text-muted)] uppercase tracking-widest">Market Sentiment Engine</h4>
                        <div className="text-[10px] font-mono text-[var(--color-info)]">MODULE: SENTIMENT</div>
                      </div>
                      <MarketMoodDial mood={firmStatus.system_performance?.market_mood || 'neutral'} />
                    </div>
                    <div className="neon-card p-6 bg-[var(--bg-surface)]">
                      <div className="border-b border-[var(--border-muted)] mb-4 pb-2 flex justify-between items-center">
                        <h4 className="text-xs font-bold text-[var(--text-muted)] uppercase tracking-widest">AI Intelligence</h4>
                        <div className="text-[10px] font-mono text-[var(--color-success)]">PERPLEXITY.AI</div>
                      </div>
                      <IntelligencePanel ticker="AAPL" showNews={true} />
                    </div>
                    <div className="neon-card p-6 bg-[var(--bg-surface)] h-full">
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
                      <button className="text-[10px] font-mono text-[var(--color-info)] hover:underline">VIEW ALL →</button>
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

                  {/* Council of Ghosts: 24-Agent Matrix */}
                  <div className="industrial-panel p-6 relative">
                    <div className="flex items-center justify-between mb-6 pb-2 border-b border-[var(--border-muted)]">
                      <h4 className="text-xs font-bold text-[var(--text-primary)] uppercase tracking-[0.2em]">
                        Council of Ghosts (Agent Grid)
                      </h4>
                      <span className="text-[10px] text-[var(--color-success)] font-mono border border-[var(--color-success)] px-2 py-1">
                        CONSENSUS: {firmStatus.system_performance?.success_rate}%
                      </span>
                    </div>

                    <div className="grid grid-cols-6 md:grid-cols-12 gap-2 mb-4">
                      {firmStatus.ai_firm?.all_agents?.map((agent, i) => (
                        <div key={agent.name} className="group/agent relative flex flex-col items-center justify-center p-2 border border-[var(--border-muted)] bg-[var(--bg-surface)] hover:border-[var(--color-info)] transition-colors cursor-help h-12">
                          <div
                            className={`w-2 h-2 transition-all duration-0 ${agent.confidence > 0.8 ? 'bg-[var(--color-success)]' :
                              agent.confidence > 0.6 ? 'bg-[var(--color-info)]' :
                                'bg-[var(--text-muted)]'
                              } ${i % 3 === 0 ? 'animate-pulse' : ''}`}
                          ></div>
                          <div className="absolute bottom-full mb-2 hidden group-hover/agent:block z-50 w-48 bg-[var(--bg-deep)] border border-[var(--color-info)] p-3 text-xs shadow-xl pointer-events-none">
                            <div className="font-bold text-white border-b border-[var(--border-muted)] pb-1 mb-1 font-mono uppercase">{agent.name}</div>
                            <div className="text-[var(--text-muted)] mb-1">{agent.role}</div>
                            <div className="text-[var(--color-info)] font-mono">CONF: {(agent.confidence * 100).toFixed(0)}%</div>
                          </div>
                        </div>
                      ))}
                    </div>
                    <div className="flex justify-between text-[10px] text-[var(--text-muted)] mt-2 font-mono uppercase tracking-wider">
                      <span>Stealth Mode: ENABLED</span>
                      <span>Active Synapses: {firmStatus.ai_firm?.total_agents * 1024}</span>
                    </div>
                  </div>

                  {/* CEO Reasoning & Ghost Whispers */}
                  {wisdom && (
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                      <div className="lg:col-span-2 border border-[var(--border-muted)] bg-[var(--bg-surface)] p-6 relative overflow-hidden">
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
                      <WisdomPulse />
                    </div>
                  )}

                  {/* Action Bar */}
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
            <h3 className="text-lg font-bold text-[var(--text-primary)] uppercase tracking-wider pl-4 border-l-4 border-[var(--color-info)] mt-12 mb-6">
              Key Persona Analysis
            </h3>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 pb-20">
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
        </div>
      </div>
    </div>
  );
};

export default AIFirmDashboard;
