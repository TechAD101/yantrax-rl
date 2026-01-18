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
      <div className="glass-card rounded-2xl p-6 flex items-center justify-center h-48 animate-pulse">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-400"></div>
        <span className="ml-4 text-cyan-300 font-mono tracking-widest text-sm">INITIALIZING AI FIRM NEXUS...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="glass-card from-red-900/40 rounded-xl border border-red-500/30 p-6 backdrop-blur-md">
        <div className="flex items-center">
          <div className="w-3 h-3 rounded-full bg-red-500 mr-3 animate-pulse shadow-[0_0_10px_rgba(239,68,68,0.5)]"></div>
          <span className="text-red-300 font-bold tracking-wide">{error}</span>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-fade-in-scale">
      {/* AI Firm Status Overview */}
      <div className="glass-card rounded-2xl p-8 transition-all hover:shadow-cyan-900/10">
        <div className="flex items-center justify-between mb-8 pb-4 border-b border-white/5">
          <h3 className="text-2xl font-black text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500 flex items-center tracking-tight">
            <span className="w-3 h-3 bg-cyan-400 rounded-full mr-4 animate-pulse-glow shadow-[0_0_15px_rgba(34,211,238,0.6)]"></span>
            AI FIRM COMMAND CENTER
          </h3>
          <div className="flex items-center space-x-3">
            <div className={`px-4 py-1.5 rounded-full text-[10px] font-bold uppercase tracking-[0.2em] transition-all ${firmStatus?.status === 'fully_operational'
              ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 shadow-[0_0_10px_rgba(16,185,129,0.2)]'
              : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
              }`}>
              {firmStatus?.status?.replace('_', ' ') || 'ACTIVE'}
            </div>
            <button
              onClick={fetchAIFirmData}
              className="p-2 bg-white/5 hover:bg-white/10 rounded-lg text-white/70 hover:text-white transition-all active:scale-95"
              disabled={loading}
            >
              <span className={loading ? "inline-block animate-spin" : ""}>↻</span>
            </button>
          </div>
        </div>

        {firmStatus && (
          <div className="space-y-8">
            {/* Institutional Wow: Pain Meter & Mood Dial */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <div className="glass-card rounded-2xl p-6 bg-black/20 hover:bg-black/30 transition-colors">
                <h4 className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-6">Market Sentiment Engine</h4>
                <MarketMoodDial mood={firmStatus.system_performance?.market_mood || 'neutral'} />
              </div>
              <div className="glass-card rounded-2xl p-6 bg-black/20 hover:bg-black/30 transition-colors h-full">
                <h4 className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-6">Strategy Nexus</h4>
                <StrategyMarketplace />
              </div>
            </div>

            {/* KPI Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Total Agents */}
              <div className="glass-card rounded-xl p-5 group hover:-translate-y-1 transition-transform duration-300 border-l-4 border-l-cyan-500">
                <div className="text-3xl font-black text-white mb-1 group-hover:scale-105 transition-transform origin-left">
                  {firmStatus.ai_firm?.total_agents || 24}
                </div>
                <div className="text-xs text-gray-400 font-bold uppercase tracking-wider">Active Neural Agents</div>
                <div className="text-[10px] text-emerald-400 mt-2 font-mono flex items-center">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 mr-2 animate-pulse"></span>
                  COORDINATION: OPTIMAL
                </div>
              </div>

              {/* Portfolio Value */}
              <div className="glass-card rounded-xl p-5 group hover:-translate-y-1 transition-transform duration-300 border-l-4 border-l-emerald-500">
                <div className="text-3xl font-black text-emerald-400 mb-1 group-hover:scale-105 transition-transform origin-left drop-shadow-[0_0_10px_rgba(52,211,153,0.3)]">
                  ${firmStatus.system_performance?.portfolio_balance?.toLocaleString() || '0'}
                </div>
                <div className="text-xs text-gray-400 font-bold uppercase tracking-wider">AUM Value</div>
                <div className="text-[10px] text-emerald-400 mt-2 font-mono">
                  SUCCESS RATE: {firmStatus.system_performance?.success_rate || 0}%
                </div>
              </div>

              {/* Active Departments */}
              <div className="glass-card rounded-xl p-5 group hover:-translate-y-1 transition-transform duration-300 border-l-4 border-l-violet-500">
                <div className="text-3xl font-black text-violet-400 mb-1 group-hover:scale-105 transition-transform origin-left">
                  {Object.keys(firmStatus.ai_firm?.departments || {}).length || 5}
                </div>
                <div className="text-xs text-gray-400 font-bold uppercase tracking-wider">Operational Depts</div>
                <div className="text-[10px] text-amber-400 mt-2 font-mono">
                  FULL MANAGEMENT MODE
                </div>
              </div>
            </div>

            {/* Top Strategies (internal) */}
            <div className="p-4 rounded-xl bg-white/5 border border-white/5 hover:border-white/10 transition-colors">
              <div className="flex items-center justify-between mb-3">
                <h4 className="text-xs font-bold text-violet-300 uppercase tracking-widest">Top Internal Strategies</h4>
                <button className="text-[10px] text-white/50 hover:text-white transition-colors">VIEW ALL</button>
              </div>
              <div className="space-y-2">
                {topStrategies.length === 0 ? (
                  <div className="text-xs text-gray-500 italic">Calculating performance metrics...</div>
                ) : (
                  topStrategies.map((s, i) => (
                    <div key={s.id} className="flex items-center justify-between p-2 rounded-lg bg-black/20 hover:bg-white/5 transition-colors group">
                      <div className="flex items-center space-x-3">
                        <span className="text-xs font-mono text-gray-600 group-hover:text-violet-400 w-4">#{i + 1}</span>
                        <div className="text-sm text-gray-300 font-medium group-hover:text-white">{s.name}</div>
                      </div>
                      <div className="text-xs font-mono font-bold text-emerald-400">SR: {s.metrics?.sharpe ?? '—'}</div>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Council of Ghosts: 24-Agent Matrix */}
            <div className="glass-card rounded-xl p-6 relative overflow-hidden group">
              <div className="absolute top-0 right-0 p-4 opacity-50 text-[100px] leading-none select-none pointer-events-none grayscale opacity-5">🧠</div>
              <h4 className="text-xs font-bold text-gray-500 mb-6 uppercase tracking-[0.2em] flex items-center justify-between relative z-10">
                <span className="flex items-center">
                  <span className="w-1.5 h-1.5 bg-violet-500 rounded-full mr-2 shadow-[0_0_10px_rgba(139,92,246,0.5)]"></span>
                  Council of Ghosts (Agent Grid)
                </span>
                <span className="text-[10px] text-violet-400 font-mono bg-violet-500/10 px-2 py-1 rounded border border-violet-500/20">
                  CONSENSUS: {firmStatus.system_performance?.success_rate}%
                </span>
              </h4>

              <div className="grid grid-cols-6 md:grid-cols-12 gap-3 mb-4 relative z-10">
                {firmStatus.ai_firm?.all_agents?.map((agent, i) => (
                  <div key={agent.name} className="group/agent relative flex flex-col items-center justify-center p-2 rounded-lg hover:bg-white/5 transition-colors cursor-help">
                    <div
                      className={`w-2.5 h-2.5 rounded-full transition-all duration-500 ${agent.confidence > 0.8 ? 'bg-cyan-400 shadow-[0_0_10px_rgba(34,211,238,0.8)]' :
                        agent.confidence > 0.6 ? 'bg-blue-400 shadow-[0_0_8px_rgba(96,165,250,0.6)]' :
                          'bg-gray-600 shadow-none'
                        } ${i % 3 === 0 ? 'animate-pulse' : ''}`}
                    ></div>
                    {/* Tooltip on hover */}
                    <div className="absolute bottom-full mb-2 hidden group-hover/agent:block z-50 w-40 bg-gray-900 border border-gray-700 rounded-lg p-3 text-xs shadow-xl pointer-events-none backdrop-blur-xl animate-fade-in-scale">
                      <div className="font-bold text-white border-b border-gray-700 pb-1.5 mb-1.5">{agent.name}</div>
                      <div className="text-gray-400 mb-1">{agent.role}</div>
                      <div className="text-cyan-400 font-mono font-bold">Conf: {(agent.confidence * 100).toFixed(0)}%</div>
                    </div>
                  </div>
                ))}
              </div>
              <div className="flex justify-between text-[10px] text-gray-500 mt-4 border-t border-white/5 pt-3 font-mono uppercase tracking-wider relative z-10">
                <span>Stealth Mode: ENABLED</span>
                <span>Active Synapses: {firmStatus.ai_firm?.total_agents * 1024}</span>
              </div>
            </div>

            {/* CEO Reasoning & Ghost Whispers */}
            {wisdom && (
              <div className="relative rounded-xl p-0.5 bg-gradient-to-r from-blue-500/30 to-purple-500/30">
                <div className="bg-gray-900 rounded-[10px] p-6 relative overflow-hidden">
                  <div className="absolute top-0 right-0 w-32 h-32 bg-blue-500/10 rounded-full blur-3xl -mr-10 -mt-10"></div>
                  <h4 className="text-sm font-bold text-blue-300 mb-3 flex items-center relative z-10">
                    <span className="mr-2 text-lg">📜</span> INSTITUTIONAL WISDOM
                  </h4>
                  <div className="text-sm text-gray-200 leading-relaxed italic font-serif relative z-10 pl-4 border-l-2 border-blue-500/30">
                    "{wisdom.text || "Boond boond se ghada bharta hai."}"
                    <span className="block mt-2 text-[10px] text-gray-500 not-italic font-sans uppercase tracking-widest">— {wisdom.metadata?.source || "YantraX Core DNA"}</span>
                  </div>
                </div>
              </div>
            )}

            {/* Institutional Phase Ω: Action Bar */}
            <div className="flex items-center justify-center pt-8 pb-4">
              <button
                onClick={() => setReportOpen(true)}
                className="group relative px-10 py-4 bg-gradient-to-r from-cyan-600 to-blue-700 hover:from-cyan-500 hover:to-blue-600 rounded-2xl font-bold text-white shadow-2xl transition-all duration-300 transform hover:scale-[1.02] active:scale-[0.98] ring-1 ring-white/10 hover:ring-white/20"
              >
                <div className="absolute inset-0 bg-white/20 opacity-0 group-hover:opacity-100 rounded-2xl transition-opacity animate-pulse"></div>
                <span className="flex items-center tracking-widest uppercase text-xs font-bold relative z-10">
                  <span className="mr-3 text-lg">📄</span>
                  Generate Institutional Intelligence Report
                </span>
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
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {personas.map((persona) => (
          <div key={persona.name} className={`glass-card rounded-2xl p-6 transition-all duration-300 hover:shadow-lg group relative overflow-hidden
                        ${persona.role === 'director' ? 'hover:shadow-cyan-500/10 hover:border-cyan-500/20' : 'hover:shadow-purple-500/10 hover:border-purple-500/20'}`}>

            <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-white/5 to-transparent rounded-full blur-3xl -mr-20 -mt-20 pointer-events-none"></div>

            <div className="flex items-center mb-6 relative z-10">
              <div className={`w-16 h-16 rounded-2xl bg-gradient-to-br from-gray-800 to-gray-900 flex items-center justify-center mr-5 border border-white/10 text-3xl shadow-lg ring-1 ring-white/5 group-hover:scale-110 transition-transform duration-300`}>
                {persona.name === 'warren' ? '👴' :
                  persona.name === 'cathie' ? '🚀' :
                    persona.name === 'macro_monk' ? '🧘' :
                      persona.name === 'the_ghost' ? '👻' :
                        persona.name === 'degen_auditor' ? '🔍' : '🤖'}
              </div>
              <div>
                <h4 className="text-xl font-bold text-white capitalize tracking-tight group-hover:text-transparent group-hover:bg-clip-text group-hover:bg-gradient-to-r group-hover:from-white group-hover:to-gray-400 transition-all">{persona.name}</h4>
                <p className="text-xs text-gray-400 uppercase tracking-widest mt-1">{persona.role} • {persona.specialty}</p>
              </div>
            </div>

            <div className="space-y-4 relative z-10">
              <div className="flex items-center justify-between p-3 rounded-lg bg-white/5 hover:bg-white/10 transition-colors">
                <span className="text-sm text-gray-400 font-medium">Conviction</span>
                <span className={`text-sm font-bold font-mono ${persona.confidence > 0.8 ? 'text-emerald-400' : 'text-amber-400'}`}>
                  {(persona.confidence * 100).toFixed(0)}%
                </span>
              </div>

              <div className="bg-black/20 rounded-xl p-4 border border-white/5">
                <p className="text-[10px] text-gray-500 uppercase tracking-widest mb-2 font-bold flex items-center">
                  <span className="w-1 h-1 bg-gray-500 rounded-full mr-2"></span>
                  Current Focus
                </p>
                <p className="text-sm text-gray-300 leading-relaxed font-light">
                  Agents in the <span className="text-white font-medium">{persona.department?.replace('_', ' ') || 'core'}</span> department are currently monitoring {persona.specialty?.toLowerCase() || 'market'} patterns efficiently.
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
