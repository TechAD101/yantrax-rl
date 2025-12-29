import React from 'react';
import { api } from '../api/api';
import { useState, useEffect } from 'react';

const EFFECTIVE_API = import.meta.env.VITE_API_URL || 'https://yantrax-api.onrender.com';

const Header = () => {
  const [systemStatus, setSystemStatus] = useState({
    version: '4.1.0',
    status: 'loading...',
    aiFirm: {
      total_agents: 0,
      departments: 0,
      mode: ''
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
    <header className="border-b border-gray-700/50 bg-gray-900/80 backdrop-blur-xl sticky top-0 z-50">
      <div className="px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
              YantraX RL v{systemStatus.version}
            </h1>
            <span className="px-2 py-1 text-xs font-medium bg-purple-500/20 text-purple-300 rounded-md">
              SUPERNATURAL
            </span>
          </div>

          <div className="flex items-center space-x-6">
            {/* Institutional Trust Score */}
            <div className="flex flex-col items-end">
              <span className="text-[10px] text-gray-500 uppercase tracking-widest">Trust Score</span>
              <div className="flex items-center space-x-2">
                <span className={`text-sm font-bold ${systemStatus.institutional_trust?.score > 80 ? 'text-cyan-400' : 'text-yellow-400'}`}>
                  {systemStatus.institutional_trust?.score || '88.5'}%
                </span>
                <div className={`w-1.5 h-1.5 rounded-full ${systemStatus.institutional_trust?.score > 80 ? 'bg-cyan-400 shadow-[0_0_5px_rgba(34,211,238,0.8)]' : 'bg-yellow-400'}`} />
              </div>
            </div>

            {/* Ghost Layer Status */}
            <div className="flex flex-col items-end border-l border-gray-700/50 pl-6">
              <span className="text-[10px] text-purple-400 uppercase tracking-widest font-bold">Ghost Layer</span>
              <span className="text-xs text-purple-300 font-mono">
                {systemStatus.ghost_layer?.dimension || '9th_chamber'}
              </span>
            </div>

            {/* System Status */}
            <div className="flex items-center space-x-3 border-l border-gray-700/50 pl-6">
              <div className="text-right">
                <div className="text-xs text-gray-400">v{systemStatus.version}</div>
                <div className="text-[9px] text-gray-500 font-mono">Updated: {systemStatus.lastUpdated?.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</div>
                <div className="text-[10px] text-green-500 font-mono uppercase tracking-tighter">Sync: {systemStatus.cache_sync || '60s'}</div>
              </div>
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse shadow-[0_0_8px_rgba(34,197,94,0.6)]" />
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;