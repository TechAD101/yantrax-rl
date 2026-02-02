import React from 'react';
import { api } from '../api/api';
import { useState, useEffect } from 'react';

const Header = () => {
  const [systemStatus, setSystemStatus] = useState({
    version: '4.1.0',
    status: 'loading...',
    aiFirm: {
      total_agents: 0,
      departments: 0,
    },
    lastUpdated: new Date()
  });

  useEffect(() => {
    // Subscribe to status updates
    const unsubscribe = api.subscribeToUpdates('getStatus', (data) => {
      setSystemStatus({ ...data, lastUpdated: new Date() });
    });

    return () => unsubscribe();
  }, []);

  return (
    <header className="border-b border-[var(--border-muted)] bg-[var(--bg-deep)] sticky top-0 z-50">
      <div className="px-6 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <h1 className="text-2xl font-bold text-[var(--text-primary)] tracking-widest uppercase">
              YantraX<span className="text-[var(--color-success)]">RL</span> <span className="text-xs text-[var(--border-active)]">v{systemStatus.version}</span>
            </h1>
            <span className="px-2 py-0.5 text-[10px] font-mono border border-[var(--color-info)] text-[var(--color-info)] uppercase tracking-wider">
              System Online
            </span>
          </div>

          <div className="flex items-center space-x-8 font-mono">
            {/* Institutional Trust Score */}
            <div className="flex flex-col items-end">
              <span className="text-[10px] text-[var(--text-muted)] uppercase tracking-widest">Trust Index</span>
              <div className="flex items-center space-x-2">
                <span className={`text-sm font-bold ${systemStatus.institutional_trust?.score > 80 ? 'text-[var(--color-success)]' : 'text-[var(--color-warning)]'}`}>
                  {systemStatus.institutional_trust?.score || '88.5'}%
                </span>
                <div className={`w-1.5 h-1.5 rounded-none ${systemStatus.institutional_trust?.score > 80 ? 'bg-[var(--color-success)]' : 'bg-[var(--color-warning)]'} animate-pulse`} />
              </div>
            </div>

            {/* Ghost Layer Status */}
            <div className="flex flex-col items-end border-l border-[var(--border-muted)] pl-6">
              <span className="text-[10px] text-[var(--text-muted)] uppercase tracking-widest">Ghost Layer</span>
              <span className="text-xs text-[var(--color-info)]">
                {systemStatus.ghost_layer?.dimension || '9TH_CHAMBER'}
              </span>
            </div>

            {/* System Status */}
            <div className="flex items-center space-x-3 border-l border-[var(--border-muted)] pl-6">
              <div className="text-right">
                <div className="text-[10px] text-[var(--text-muted)] uppercase">LAST PULSE</div>
                <div className="text-xs text-[var(--text-primary)]">
                  {systemStatus.lastUpdated?.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                </div>
              </div>
              <div className="w-2 h-2 bg-[var(--color-success)] animate-pulse shadow-[0_0_8px_var(--color-success)]" />
            </div>
          </div>
        </div>
      </div>
      {/* Decorative scanline at bottom of header */}
      <div className="h-[1px] w-full bg-gradient-to-r from-transparent via-[var(--color-success)] to-transparent opacity-50"></div>
    </header>
  );
};

export default Header;