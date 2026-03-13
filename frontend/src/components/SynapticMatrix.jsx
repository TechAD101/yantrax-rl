import React, { useState, useEffect } from 'react';

/**
 * SynapticMatrix - God Mode Vision
 * A high-fidelity, surgical visualization of the 24-agent Ghost Council.
 * Replaces the legacy grid with a responsive, data-reactive neural matrix.
 */
const SynapticMatrix = ({ agents = [], consensus = 0 }) => {
  const [pulse, setPulse] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setPulse(p => (p + 1) % 100);
    }, 50);
    return () => clearInterval(interval);
  }, []);

  // Ensure we always have 24 slots for visual consistency
  const totalSlots = 24;
  const displayAgents = [...agents];
  while (displayAgents.length < totalSlots) {
    displayAgents.push({ 
      name: `Ghost_${displayAgents.length + 1}`, 
      confidence: Math.random() * 0.3,
      role: 'Dormant Synapse'
    });
  }

  return (
    <div className="surgical-panel p-8 relative group overflow-hidden">
      {/* Background Neural Noise */}
      <div className="absolute inset-0 opacity-[0.03] pointer-events-none font-mono text-[8px] overflow-hidden leading-none select-none">
        {Array.from({ length: 20 }).map((_, i) => (
          <div key={i} className="whitespace-nowrap mb-1">
            {Array.from({ length: 50 }).map(() => Math.random() > 0.5 ? '1' : '0').join(' ')}
          </div>
        ))}
      </div>

      <div className="relative z-10">
        <div className="flex items-center justify-between mb-8 pb-4 border-b border-[var(--border-void)]">
          <div>
            <h4 className="text-[11px] font-mono font-bold text-[var(--text-secondary)] uppercase tracking-[0.3em] flex items-center">
              <span className="w-1 h-4 bg-[var(--color-aura-blue)] mr-3"></span>
              Council of Ghosts // Synaptic Matrix
            </h4>
            <p className="text-[10px] text-[var(--text-muted)] mt-1 font-mono uppercase">
              24-Protocol Neural Consensus Active
            </p>
          </div>
          <div className="text-right">
            <div className="text-2xl font-mono text-[var(--color-aura-blue)] font-bold text-aura-glow">
              {consensus}%
            </div>
            <div className="text-[9px] text-[var(--text-muted)] uppercase tracking-widest">
              Aggregate Conviction
            </div>
          </div>
        </div>

        {/* The Matrix Grid */}
        <div className="grid grid-cols-4 md:grid-cols-6 lg:grid-cols-8 gap-4">
          {displayAgents.slice(0, 24).map((agent, i) => {
            const isActive = agent.confidence > 0.6;
            const isHighConfidence = agent.confidence > 0.8;
            
            return (
              <div 
                key={`${agent.name}-${i}`} 
                className={`relative aspect-square border transition-all duration-700 cursor-crosshair group/node
                  ${isActive 
                    ? 'border-[var(--color-aura-blue)]/30 bg-[var(--color-aura-blue)]/[0.03]' 
                    : 'border-[var(--border-void)] bg-white/[0.01] grayscale opacity-40 hover:opacity-100 hover:grayscale-0'
                  }
                `}
              >
                {/* Visual Indicators */}
                <div className="absolute inset-0 flex items-center justify-center">
                  {/* Outer Ring */}
                  {isActive && (
                    <div className={`absolute w-3/4 h-3/4 rounded-full border border-[var(--color-aura-blue)]/20 animate-ping opacity-20`}
                         style={{ animationDuration: `${2 + (i % 3)}s` }}></div>
                  )}
                  
                  {/* Core Node */}
                  <div className={`w-1.5 h-1.5 rounded-full transition-all duration-500
                    ${isHighConfidence ? 'bg-[var(--color-aura-blue)] shadow-[0_0_10px_var(--color-aura-blue)]' : 
                      isActive ? 'bg-[var(--color-aura-blue)] opacity-50' : 'bg-[var(--text-muted)] opacity-30'}
                  `}></div>
                </div>

                {/* Index Number */}
                <div className="absolute top-1 left-1 text-[7px] font-mono text-[var(--text-muted)] opacity-50">
                  {String(i + 1).padStart(2, '0')}
                </div>

                {/* Data Trace (Random Micro lines) */}
                {isActive && (
                  <div className="absolute top-0 right-0 w-2 h-[1px] bg-[var(--color-aura-blue)]/50"></div>
                )}

                {/* Tooltip on Hover */}
                <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 hidden group-hover/node:block z-[200] w-40 glass-panel-2 p-3 text-[10px] pointer-events-none">
                  <div className="font-mono font-bold text-white border-b border-white/10 pb-1 mb-1 uppercase tracking-tighter">
                    {agent.name}
                  </div>
                  <div className="text-[var(--text-secondary)] italic mb-1">{agent.role}</div>
                  <div className="flex justify-between items-center mt-2">
                    <span className="text-[var(--text-muted)] uppercase">Conviction</span>
                    <span className="text-[var(--color-aura-blue)] font-bold">{(agent.confidence * 100).toFixed(0)}%</span>
                  </div>
                  {/* Confidence Bar */}
                  <div className="h-1 bg-white/5 w-full mt-1.5 overflow-hidden">
                    <div 
                      className="h-full bg-[var(--color-aura-blue)]" 
                      style={{ width: `${agent.confidence * 100}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Matrix Metadata Footer */}
        <div className="mt-8 pt-4 border-t border-[var(--border-void)] flex justify-between items-end">
          <div className="space-y-1">
            <div className="flex items-center gap-3">
              <span className="status-pulse online"></span>
              <span className="text-[9px] font-mono text-[var(--text-secondary)] uppercase tracking-widest">Neural Link: Established</span>
            </div>
            <div className="text-[8px] font-mono text-[var(--text-muted)] uppercase">
              Latent Space Latency: <span className="text-[var(--color-aura-blue)]">0.42ms</span> // Packets: Stable
            </div>
          </div>
          <div className="font-mono text-[9px] text-[var(--text-muted)] opacity-50 uppercase tracking-tighter">
            yantra_firm_v5_synapse_map
          </div>
        </div>
      </div>

      {/* Aesthetic Surgical scanlines */}
      <div className="absolute inset-0 pointer-events-none opacity-[0.02] bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.25)_50%),linear-gradient(90deg,rgba(255,0,0,0.06),rgba(0,255,0,0.02),rgba(0,0,255,0.06))] bg-[length:100%_2px,3px_100%]"></div>
    </div>
  );
};

export default SynapticMatrix;
