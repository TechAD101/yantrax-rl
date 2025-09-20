// AIFirmDashboard.jsx - Enhanced AI Firm Integration Component
import React, { useState, useEffect } from 'react';

const AIFirmDashboard = () => {
  const [firmStatus, setFirmStatus] = useState(null);
  const [warrenAnalysis, setWarrenAnalysis] = useState(null);
  const [cathieAnalysis, setCathieAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const API_BASE = 'https://yantrax-backend.onrender.com';

  useEffect(() => {
    fetchAIFirmData();
    const interval = setInterval(fetchAIFirmData, 30000); // Update every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchAIFirmData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch AI firm status
      const firmResponse = await fetch(`${API_BASE}/api/ai-firm/status`);
      if (firmResponse.ok) {
        const firmData = await firmResponse.json();
        setFirmStatus(firmData);
      }

      // Fetch Warren analysis
      const warrenResponse = await fetch(`${API_BASE}/api/ai-firm/personas/warren`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ symbol: 'AAPL' })
      });
      if (warrenResponse.ok) {
        const warrenData = await warrenResponse.json();
        setWarrenAnalysis(warrenData);
      }

      // Fetch Cathie analysis
      const cathieResponse = await fetch(`${API_BASE}/api/ai-firm/personas/cathie`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ symbol: 'NVDA' })
      });
      if (cathieResponse.ok) {
        const cathieData = await cathieResponse.json();
        setCathieAnalysis(cathieData);
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
            <div className={`px-3 py-1 rounded-full text-xs font-semibold ${
              firmStatus?.status === 'fully_operational' 
                ? 'bg-green-900/50 text-green-400' 
                : 'bg-yellow-900/50 text-yellow-400'
            }`}>
              {firmStatus?.status || 'Loading...'}
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
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Total Agents */}
            <div className="bg-gray-900/60 rounded-lg p-4 border border-gray-700/30">
              <div className="text-2xl font-bold text-white mb-1">
                {firmStatus.ai_firm?.total_agents || 0}
              </div>
              <div className="text-sm text-gray-400">Total AI Agents</div>
              <div className="text-xs text-green-400 mt-1">
                ✓ Multi-Agent Coordination Active
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
                {Object.keys(firmStatus.ai_firm?.departments || {}).length || 0}
              </div>
              <div className="text-sm text-gray-400">Active Departments</div>
              <div className="text-xs text-orange-400 mt-1">
                🏢 Full Firm Coordination
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Named Personas Analysis */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Warren Buffett Persona */}
        <div className="bg-gradient-to-br from-green-800/20 to-green-900/20 rounded-xl border border-green-700/50 p-6 backdrop-blur-sm">
          <div className="flex items-center mb-4">
            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center mr-4">
              <span className="text-white font-bold text-lg">W</span>
            </div>
            <div>
              <h4 className="text-lg font-bold text-green-400">Warren Persona</h4>
              <p className="text-sm text-green-300/70">Value Investing • Fundamental Analysis</p>
            </div>
          </div>

          {warrenAnalysis ? (
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-300">Recommendation:</span>
                <span className={`text-sm font-bold px-2 py-1 rounded ${
                  warrenAnalysis.warren_analysis?.recommendation?.includes('BUY') 
                    ? 'bg-green-900/50 text-green-400'
                    : 'bg-gray-700/50 text-gray-300'
                }`}>
                  {warrenAnalysis.warren_analysis?.recommendation || 'ANALYZING'}
                </span>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-300">Confidence:</span>
                <span className="text-sm font-bold text-green-400">
                  {((warrenAnalysis.warren_analysis?.confidence || 0) * 100).toFixed(0)}%
                </span>
              </div>

              <div className="bg-green-900/20 rounded-lg p-3 border border-green-700/30">
                <p className="text-xs text-green-200 italic">
                  "{warrenAnalysis.philosophy || 'Value investing philosophy'}"
                </p>
                <p className="text-xs text-green-300 mt-2">
                  {warrenAnalysis.warren_analysis?.reasoning || 'Analyzing fundamental metrics...'}
                </p>
              </div>
            </div>
          ) : (
            <div className="text-center text-green-400 py-4">
              <div className="animate-pulse">Loading Warren's Analysis...</div>
            </div>
          )}
        </div>

        {/* Cathie Wood Persona */}
        <div className="bg-gradient-to-br from-purple-800/20 to-pink-900/20 rounded-xl border border-purple-700/50 p-6 backdrop-blur-sm">
          <div className="flex items-center mb-4">
            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-purple-500 to-pink-600 flex items-center justify-center mr-4">
              <span className="text-white font-bold text-lg">C</span>
            </div>
            <div>
              <h4 className="text-lg font-bold text-purple-400">Cathie Persona</h4>
              <p className="text-sm text-purple-300/70">Innovation Focus • Growth Analysis</p>
            </div>
          </div>

          {cathieAnalysis ? (
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-300">Recommendation:</span>
                <span className={`text-sm font-bold px-2 py-1 rounded ${
                  cathieAnalysis.cathie_analysis?.recommendation?.includes('BUY')
                    ? 'bg-purple-900/50 text-purple-400'
                    : 'bg-gray-700/50 text-gray-300'
                }`}>
                  {cathieAnalysis.cathie_analysis?.recommendation || 'ANALYZING'}
                </span>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-300">Confidence:</span>
                <span className="text-sm font-bold text-purple-400">
                  {((cathieAnalysis.cathie_analysis?.confidence || 0) * 100).toFixed(0)}%
                </span>
              </div>

              <div className="bg-purple-900/20 rounded-lg p-3 border border-purple-700/30">
                <p className="text-xs text-purple-200 italic">
                  "{cathieAnalysis.philosophy || 'Innovation investment philosophy'}"
                </p>
                <p className="text-xs text-purple-300 mt-2">
                  {cathieAnalysis.cathie_analysis?.reasoning || 'Analyzing innovation potential...'}
                </p>
              </div>
            </div>
          ) : (
            <div className="text-center text-purple-400 py-4">
              <div className="animate-pulse">Loading Cathie's Analysis...</div>
            </div>
          )}
        </div>
      </div>

      {/* AI Firm Coordination Status */}
      {firmStatus?.ai_firm && (
        <div className="bg-gradient-to-br from-blue-800/20 to-indigo-900/20 rounded-xl border border-blue-700/50 p-6 backdrop-blur-sm">
          <h4 className="text-lg font-bold text-blue-400 mb-4">Firm Coordination Metrics</h4>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-xl font-bold text-blue-400">
                {firmStatus.ai_firm.ceo_metrics?.total_decisions || 0}
              </div>
              <div className="text-xs text-gray-400">CEO Decisions</div>
            </div>
            
            <div className="text-center">
              <div className="text-xl font-bold text-green-400">
                {firmStatus.ai_firm.personas_active ? '2' : '0'}
              </div>
              <div className="text-xs text-gray-400">Active Personas</div>
            </div>
            
            <div className="text-center">
              <div className="text-xl font-bold text-purple-400">
                {firmStatus.ai_firm.recent_coordination_sessions || 0}
              </div>
              <div className="text-xs text-gray-400">Coordination Sessions</div>
            </div>
            
            <div className="text-center">
              <div className="text-xl font-bold text-orange-400">
                {Object.keys(firmStatus.ai_firm.departments || {}).length}
              </div>
              <div className="text-xs text-gray-400">Departments Online</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AIFirmDashboard;
