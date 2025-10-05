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
    }
  });

  useEffect(() => {
    // Subscribe to status updates
    const unsubscribe = api.subscribeToUpdates('getStatus', (data) => {
      setSystemStatus(data);
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
            {/* AI Firm Status */}
            <div className="flex items-center space-x-2">
              <div className="text-sm text-gray-400">
                <span className="block text-right">AI Firm</span>
                <span className="block text-xs text-gray-500">
                  {systemStatus.aiForm?.total_agents || 24} Agents • {systemStatus.aiForm?.departments || 5} Departments
                </span>
              </div>
            </div>

            {/* System Status */}
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-400">Status:</span>
              <div className="flex items-center space-x-2">
                <span className="text-green-400">{systemStatus.status}</span>
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              </div>
            </div>
            {/* Debug: show effective API URL for deployment verification */}
            <div className="text-xs text-gray-400">
              API: <span className="text-blue-300">{EFFECTIVE_API}</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;