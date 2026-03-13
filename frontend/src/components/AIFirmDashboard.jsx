import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/api';
import PainMeter from './PainMeter';
import MarketMoodDial from './MarketMoodDial';
import InstitutionalReport from './InstitutionalReport';
import StrategyMarketplace from './StrategyMarketplace';
import IntelligencePanel from './IntelligencePanel';
import SynapticMatrix from './SynapticMatrix';
import WisdomOracle from './WisdomOracle';

const AIFirmDashboard = () => {
  const [firmStatus, setFirmStatus] = useState(null);
  const [personas, setPersonas] = useState([]);
  const [oracleWisdom, setOracleWisdom] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [reportOpen, setReportOpen] = useState(false);
  const [topStrategies, setTopStrategies] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    fetchAIFirmData();
    const interval = setInterval(fetchAIFirmData, 300000); // Update every 5 minutes
    return () => clearInterval(interval);
  }, []);

  const fetchAIFirmData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [statusData, personaData, oracleData, topData] = await Promise.allSettled([
        api.getAIFirmStatus(),
        api.getPersonas(),
        api.getOracleWisdom(),
        api.getTopStrategies({ limit: 3, metric: 'sharpe' })
      ]);

      if (statusData.status === 'fulfilled') setFirmStatus(statusData.value);
      if (personaData.status === 'fulfilled') {
        setPersonas(personaData.value.personas || []);
      }
      if (oracleData.status === 'fulfilled') {
        setOracleWisdom(oracleData.value.oracle_wisdom);
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
    <div className="min-h-screen bg-[#020202] flex items-center justify-center p-8">
      <div className="flex flex-col items-center">
        <div className="w-12 h-12 border-t-2 border-[var(--color-aura-blue)] animate-spin rounded-full mb-8 shadow-[0_0_20px_var(--color-aura-blue)]"></div>
        <div className="text-[var(--color-aura-blue)] font-mono text-[10px] tracking-[0.5em] uppercase animate-pulse">
          Syncing with Synaptic Matrix...
        </div>
      </div>
    </div>
  );

  return (
    <div className="yantra-dashboard">
      <div className="max-w-[1600px] mx-auto space-y-12 pb-24">
        
        {/* Surgical Header */}
        <header className="dashboard-header">
          <div className="flex flex-col md:flex-row md:items-end justify-between gap-8">
            <div className="space-y-4">
              <div className="flex items-center gap-4">
                <span className="status-pulse online"></span>
                <span className="text-[10px] font-mono text-[var(--text-muted)] uppercase tracking-[0.3em]">
                  System Status: Sovereign & Optimized
                </span>
              </div>
              <h1>The Ghost Council</h1>
              <p>
                Multi-agent reinforcement learning firm. Operational precision through distributed 
                neural consensus and divine strategic synthesis.
              </p>
            </div>
            
            <div className="flex items-center gap-4">
              <div className="text-right mr-4 hidden md:block">
                <div className="text-[10px] text-[var(--text-muted)] uppercase tracking-widest font-mono">Institutional AUM</div>
                <div className="text-xl font-mono text-white font-bold">
                  ${firmStatus?.system_performance?.portfolio_balance?.toLocaleString() || '2,491,082'}
                </div>
              </div>
              <button 
                onClick={fetchAIFirmData}
                className="btn-surgical btn-surgical-ghost"
              >
                Refresh Matrix
              </button>
            </div>
          </div>
        </header>

        {/* Global Intelligence Layer */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Main Neural Core */}
          <div className="lg:col-span-8 space-y-8">
            <SynapticMatrix 
              agents={firmStatus?.ai_firm?.all_agents} 
              consensus={firmStatus?.system_performance?.success_rate || 78} 
            />
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div className="surgical-panel p-6">
                <h4 className="section-title">Market Sentiment Dial</h4>
                <MarketMoodDial />
              </div>
              <div className="surgical-panel p-6">
                <h4 className="section-title">Institutional Report</h4>
                <div className="space-y-6 pt-4">
                  <p className="text-sm text-[var(--text-secondary)] leading-relaxed italic">
                    Generate a high-fidelity audit of current synaptic performance and market alignment.
                  </p>
                  <button 
                    onClick={() => setReportOpen(true)}
                    className="btn-surgical btn-surgical-primary w-full"
                  >
                    Generate Signal Audit
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Side Strategy Layer */}
          <div className="lg:col-span-4 space-y-8">
            <WisdomOracle wisdom={oracleWisdom} loading={loading && !!firmStatus} />
            
            <div className="surgical-panel p-6">
              <h4 className="section-title">Strategy Nexus</h4>
              <StrategyMarketplace />
            </div>
          </div>
        </div>

        {/* Institutional Audit Checkpoints */}
        <div className="surgical-panel p-8">
          <div className="flex items-center justify-between mb-8 pb-4 border-b border-[var(--border-void)]">
            <h4 className="text-[11px] font-mono font-bold text-[var(--text-secondary)] uppercase tracking-[0.3em]">
              Trade Validation Protocol // 8-Point Check
            </h4>
            <span className="text-[10px] text-[var(--color-precision-green)] font-mono uppercase bg-[var(--color-precision-green)]/5 px-3 py-1 border border-[var(--color-precision-green)]/20">
              Protocol: Active
            </span>
          </div>
          
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
            {Object.entries(firmStatus?.institutional_audit?.trading_checklist || {
              "Macro Alignment ≥50": true,
              "Liquidity ≥40": true,
              "Confidence ≥60": true,
              "Risk/Reward ≥1.5": true,
              "No Disqualifying Reversals": true,
              "No Black Swan Event": true,
              "Position Size ≤10%": true,
              "Execution Risk <2%": true
            }).map(([checkName, passed]) => (
              <div key={checkName} className="flex items-center gap-4 p-4 border border-[var(--border-void)] bg-white/[0.01]">
                <div className={`w-3 h-3 rounded-full ${passed ? 'bg-[var(--color-precision-green)] shadow-[0_0_10px_var(--color-precision-green)]' : 'border border-[var(--color-surgical-red)]'}`}></div>
                <span className={`text-[11px] font-mono ${passed ? 'text-white' : 'text-[var(--text-muted)]'}`}>
                  {checkName}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Persona Sovereign Grid */}
        <div className="pt-12">
          <h4 className="section-title mb-8">Executive Persona Analysis</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {personas.map((persona) => (
              <div key={persona.name} className="surgical-panel p-0 group overflow-hidden">
                <div className="p-8 border-b border-[var(--border-void)] bg-white/[0.02] flex justify-between items-start">
                  <div>
                    <h5 className="text-2xl font-bold font-mono text-white tracking-tighter capitalize">
                      {persona.name}
                    </h5>
                    <p className="text-[10px] text-[var(--text-muted)] uppercase tracking-widest mt-2">
                       {persona.role}
                    </p>
                  </div>
                  <div className="text-3xl opacity-20 group-hover:opacity-100 transition-all duration-700 hover:scale-110">
                    {persona.name === 'warren' ? '👴' :
                      persona.name === 'cathie' ? '🚀' :
                        persona.name === 'macro_monk' ? '🧘' :
                          persona.name === 'the_ghost' ? '👻' :
                            persona.name === 'degen_auditor' ? '🔍' : '🤖'}
                  </div>
                </div>

                <div className="p-8 space-y-6">
                  <div className="flex justify-between items-end">
                    <div className="space-y-1">
                      <div className="text-[9px] text-[var(--text-muted)] uppercase tracking-widest">Neural Conviction</div>
                      <div className={`text-xl font-mono font-bold ${persona.confidence > 0.8 ? 'text-[var(--color-aura-blue)]' : 'text-[var(--text-primary)]'}`}>
                        {(persona.confidence * 100).toFixed(0)}%
                      </div>
                    </div>
                    <div className="w-16 h-1 bg-[var(--border-void)] relative overflow-hidden">
                      <div 
                        className="absolute inset-0 bg-[var(--color-aura-blue)]" 
                        style={{ width: `${persona.confidence * 100}%` }}
                      ></div>
                    </div>
                  </div>

                  <div className="pt-4 border-t border-[var(--border-void)]">
                    <p className="text-[10px] text-[var(--text-muted)] uppercase tracking-widest mb-3 font-bold">
                       Cognitive Specialization
                    </p>
                    <p className="text-xs text-[var(--text-secondary)] leading-relaxed font-mono">
                      Currently monitoring <span className="text-white"> {persona.specialty?.toLowerCase() || 'latent market'}</span> patterns 
                      within the <span className="text-[var(--color-aura-blue)]">{persona.department?.replace('_', ' ') || 'core'}</span> department.
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <InstitutionalReport
          symbol="AAPL"
          isOpen={reportOpen}
          onClose={() => setReportOpen(false)}
        />
      </div>
    </div>
  );
};

export default AIFirmDashboard;
