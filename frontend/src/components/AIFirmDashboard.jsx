import React, { useState, useEffect } from 'react';
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

  useEffect(() => {
    fetchAIFirmData();
    const interval = setInterval(fetchAIFirmData, 60000); // Update every 1 minute (Global Sync)
    return () => clearInterval(interval);
  }, []);

  const fetchAIFirmData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch AI firm status, Personas, and Wisdom in parallel
      const [statusRes, personaRes, wisdomRes] = await Promise.allSettled([
        fetch(`${BASE_URL}/api/ai-firm/status`).then(r => r.json()),
        fetch(`${BASE_URL}/api/personas`).then(r => r.json()),
        fetch(`${BASE_URL}/api/knowledge/query`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ topic: 'philosophy', max_results: 1 })
        }).then(r => r.json())
      ]);

      if (statusRes.status === 'fulfilled') setFirmStatus(statusRes.value);
      if (personaRes.status === 'fulfilled') {
        const personaList = personaRes.value.personas || [];
        setPersonas(personaList);
      }
      if (wisdomRes.status === 'fulfilled') {
        setWisdom(wisdomRes.value.wisdom?.[0]);
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
      <div className="bg-gradient-to-br from-gray-800/80 to-gray-900/80 rounded-xl border border-gray-700/50 p-6 backdrop-blur-sm">
        <div className="flex items-center justify-center h-48">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-400"></div>
          <span className="ml-4 text-gray-300">Loading AI Firm Data...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-gradient-to-br from-red-800/20 to-red-900/20 rounded-xl border border-red-700/50 p-6 backdrop-blur-sm">
        <div className="flex items-center">
          <div className="w-3 h-3 rounded-full bg-red-400 mr-3"></div>
          <span className="text-red-300">{error}</span>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* AI Firm Status Overview */}
      <div className="bg-gradient-to-br from-gray-800/80 to-gray-900/80 rounded-xl border border-gray-700/50 p-6 backdrop-blur-sm">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-xl font-bold text-cyan-400 flex items-center">
            <span className="w-3 h-3 bg-cyan-400 rounded-full mr-3 animate-pulse"></span>
            AI Firm Command Center
          </h3>
          <div className="flex items-center space-x-3">
            <div className={`px-3 py-1 rounded-full text-xs font-semibold ${firmStatus?.status === 'fully_operational'
              ? 'bg-green-900/50 text-green-400'
              : 'bg-yellow-900/50 text-yellow-400'
              }`}>
              {firmStatus?.status || 'Active'}
            </div>
            <button
              onClick={fetchAIFirmData}
              className="px-3 py-1 bg-blue-600/20 hover:bg-blue-600/30 rounded-lg text-blue-400 text-xs font-medium transition-colors"
              disabled={loading}
            >
              {loading ? '🔄' : '↻'} Refresh
            </button>
          </div>
        </div>

        {firmStatus && (
          <div className="space-y-6">
            {/* Institutional Wow: Pain Meter & Mood Dial */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 my-4">
              <PainMeter painLevel={firmStatus.system_performance?.pain_level || 0} />
              <MarketMoodDial mood={firmStatus.system_performance?.market_mood || 'neutral'} />
            </div>

            {/* World Class Vision: Life & Social Layers */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
              <div className="bg-transparent">
                <MarketMoodDial />
              </div>
              <div className="h-[400px]">
                <StrategyMarketplace />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Total Agents */}
              <div className="bg-gray-900/60 rounded-lg p-4 border border-gray-700/30">
                <div className="text-2xl font-bold text-white mb-1">
                  {firmStatus.ai_firm?.total_agents || 24}
                </div>
                <div className="text-sm text-gray-400">Total AI Agents</div>
                <div className="text-xs text-green-400 mt-1">
                  ✓ Coordination Active
                </div>
              </div>

              {/* Portfolio Performance */}
              <div className="bg-gray-900/60 rounded-lg p-4 border border-gray-700/30">
                <div className="text-2xl font-bold text-green-400 mb-1">
                  ${firmStatus.system_performance?.portfolio_balance?.toLocaleString() || '0'}
                </div>
                <div className="text-sm text-gray-400">Portfolio Value</div>
                <div className="text-xs text-cyan-400 mt-1">
                  Success Rate: {firmStatus.system_performance?.success_rate || 0}%
                </div>
              </div>

              {/* Departments Active */}
              <div className="bg-gray-900/60 rounded-lg p-4 border border-gray-700/30">
                <div className="text-2xl font-bold text-purple-400 mb-1">
                  {Object.keys(firmStatus.ai_firm?.departments || {}).length || 5}
                </div>
                <div className="text-sm text-gray-400">Active Departments</div>
                <div className="text-xs text-orange-400 mt-1">
                  🏢 Full Management
                </div>
              </div>
            </div>

            {/* Institutional Audit Checklists */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-gray-900/40 rounded-xl p-5 border border-white/5">
                <h4 className="text-xs font-bold text-gray-500 mb-4 uppercase tracking-[0.2em] flex items-center">
                  <span className="w-1.5 h-1.5 bg-blue-500 rounded-full mr-2"></span>
                  Fundamental Analysis Audit
                </h4>
                <div className="grid grid-cols-2 gap-2">
                  {firmStatus.institutional_audit?.fundamental_check && Object.entries(firmStatus.institutional_audit.fundamental_check).map(([check, passed]) => (
                    <div key={check} className="flex items-center space-x-2">
                      <span className={`text-[10px] ${passed ? 'text-green-500' : 'text-gray-600'}`}>
                        {passed ? '●' : '○'}
                      </span>
                      <span className={`text-[11px] ${passed ? 'text-gray-300' : 'text-gray-500'}`}>
                        {check}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="bg-gray-900/40 rounded-xl p-5 border border-white/5">
                <h4 className="text-xs font-bold text-gray-500 mb-4 uppercase tracking-[0.2em] flex items-center">
                  <span className="w-1.5 h-1.5 bg-orange-500 rounded-full mr-2"></span>
                  Trading Strategy Setup
                </h4>
                <div className="grid grid-cols-2 gap-2">
                  {firmStatus.institutional_audit?.trading_checklist && Object.entries(firmStatus.institutional_audit.trading_checklist).map(([check, passed]) => (
                    <div key={check} className="flex items-center space-x-2">
                      <span className={`text-[10px] ${passed ? 'text-orange-500' : 'text-gray-600'}`}>
                        {passed ? '●' : '○'}
                      </span>
                      <span className={`text-[11px] ${passed ? 'text-gray-300' : 'text-gray-500'}`}>
                        {check}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Council of Ghosts: 24-Agent Matrix */}
            <div className="bg-gray-900/60 rounded-xl p-5 border border-white/5">
              <h4 className="text-xs font-bold text-gray-500 mb-6 uppercase tracking-[0.2em] flex items-center justify-between">
                <span className="flex items-center">
                  <span className="w-1.5 h-1.5 bg-purple-500 rounded-full mr-2"></span>
                  Council of Ghosts (24-Agent Matrix)
                </span>
                <span className="text-[10px] text-purple-400 font-mono">Consensus: {firmStatus.system_performance?.success_rate}%</span>
              </h4>

              <div className="grid grid-cols-6 md:grid-cols-12 gap-3 mb-4">
                {firmStatus.ai_firm?.all_agents?.map((agent, i) => (
                  <div key={agent.name} className="group relative flex flex-col items-center">
                    <div
                      className={`w-3 h-3 rounded-full transition-all duration-700 ${agent.confidence > 0.8 ? 'bg-cyan-400 shadow-[0_0_10px_rgba(34,211,238,0.8)]' :
                        agent.confidence > 0.6 ? 'bg-blue-400 shadow-[0_0_8px_rgba(96,165,250,0.6)]' :
                          'bg-gray-600 shadow-none'
                        } ${i % 2 === 0 ? 'animate-pulse' : ''}`}
                    ></div>
                    {/* Tooltip on hover */}
                    <div className="absolute bottom-full mb-2 hidden group-hover:block z-50 w-32 bg-gray-800 border border-gray-700 rounded p-2 text-[10px] shadow-xl pointer-events-none">
                      <div className="font-bold text-white border-b border-gray-700 pb-1 mb-1">{agent.name}</div>
                      <div className="text-gray-400">{agent.role}</div>
                      <div className="text-cyan-400">Confidence: {(agent.confidence * 100).toFixed(0)}%</div>
                    </div>
                  </div>
                ))}
              </div>
              <div className="flex justify-between text-[10px] text-gray-600 mt-4 border-t border-white/5 pt-2">
                <span>Stealth Mode Enabled</span>
                <span>Active Neurons: {firmStatus.ai_firm?.total_agents}</span>
              </div>
            </div>

            {/* CEO Reasoning & Ghost Whispers */}
            {wisdom && (
              <div className="bg-gray-900/80 rounded-lg p-4 border border-blue-500/30 mb-6">
                <h4 className="text-sm font-bold text-blue-300 mb-2 flex items-center">
                  <span className="mr-2">📜</span> Institutional Wisdom
                </h4>
                <div className="text-xs text-gray-300 leading-relaxed italic">
                  "{wisdom.text || "Boond boond se ghada bharta hai."}"
                  <span className="block mt-1 text-[10px] text-gray-500">— {wisdom.metadata?.source || "YantraX Core DNA"}</span>
                </div>
              </div>
            )}

            {/* Institutional Phase Ω: Action Bar */}
            <div className="flex items-center justify-center pt-4 pb-4 border-t border-white/5">
              <button
                onClick={() => setReportOpen(true)}
                className="group relative px-8 py-3 bg-gradient-to-r from-cyan-600 to-blue-700 hover:from-cyan-500 hover:to-blue-600 rounded-xl font-bold text-white shadow-lg transition-all duration-300 transform hover:scale-[1.02] active:scale-[0.98]"
              >
                <div className="absolute inset-0 bg-white/10 opacity-0 group-hover:opacity-100 rounded-xl transition-opacity"></div>
                <span className="flex items-center tracking-widest uppercase text-[10px] font-bold">
                  <span className="mr-2 text-base">📄</span>
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
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {personas.map((persona) => (
          <div key={persona.name} className={`bg-gradient-to-br from-gray-800/20 to-gray-900/20 rounded-xl border border-gray-700/50 p-6 backdrop-blur-sm hover:border-${persona.role === 'director' ? 'cyan' : 'gray'}-500/50 transition-all`}>
            <div className="flex items-center mb-4">
              <div className={`w-12 h-12 rounded-full bg-gradient-to-br from-gray-700 to-gray-800 flex items-center justify-center mr-4 border border-white/10 text-xl`}>
                {persona.name === 'warren' ? '👴' :
                  persona.name === 'cathie' ? '🚀' :
                    persona.name === 'macro_monk' ? '🧘' :
                      persona.name === 'the_ghost' ? '👻' :
                        persona.name === 'degen_auditor' ? '🔍' : '🤖'}
              </div>
              <div>
                <h4 className="text-lg font-bold text-white capitalize">{persona.name} Persona</h4>
                <p className="text-sm text-gray-400 capitalize">{persona.role} • {persona.specialty}</p>
              </div>
            </div>

            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-400">Mandate:</span>
                <span className="text-xs text-gray-300">{persona.mandate}</span>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-400">Confidence:</span>
                <span className="text-sm font-bold text-cyan-400">
                  {(persona.confidence * 100).toFixed(0)}%
                </span>
              </div>

              <div className="bg-gray-900/40 rounded-lg p-3 border border-white/5">
                <p className="text-xs text-gray-500 uppercase tracking-tighter mb-1 font-bold">Voice & Logic</p>
                <p className="text-xs text-gray-300">
                  Agents in the {persona.department?.replace('_', ' ') || 'core'} department are currently monitoring {persona.specialty?.toLowerCase() || 'market'} patterns.
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* AI Firm Coordination Metrics (Bottom) */}
      {firmStatus?.ai_firm && (
        <div className="bg-gradient-to-br from-blue-800/20 to-indigo-900/20 rounded-xl border border-blue-700/50 p-6 backdrop-blur-sm">
          <h4 className="text-lg font-bold text-blue-400 mb-4">Firm Coordination Overview</h4>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-xl font-bold text-blue-400">
                {firmStatus.ai_firm?.ceo_metrics?.total_decisions || 0}
              </div>
              <div className="text-[10px] text-gray-400 uppercase tracking-tighter">Strategic Decisions</div>
            </div>
            <div className="text-center">
              <div className="text-xl font-bold text-green-400">
                {firmStatus.ai_firm?.personas_active || 2}
              </div>
              <div className="text-[10px] text-gray-400 uppercase tracking-tighter">Personas Engaged</div>
            </div>
            <div className="text-center">
              <div className="text-xl font-bold text-purple-400">
                {firmStatus.ai_firm?.recent_voting_sessions || 12}
              </div>
              <div className="text-[10px] text-gray-400 uppercase tracking-tighter">Agent Debates</div>
            </div>
            <div className="text-center">
              <div className="text-xl font-bold text-orange-400">
                {Object.keys(firmStatus.ai_firm.departments || {}).length || 5}
              </div>
              <div className="text-[10px] text-gray-400 uppercase tracking-tighter">Departments Active</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AIFirmDashboard;
