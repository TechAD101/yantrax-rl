import React, { useState, useEffect } from 'react';
import { api } from '../api/api';

const RiskDashboard = () => {
  const [riskData, setRiskData] = useState({
    data: null,
    loading: true
  });

  useEffect(() => {
    const unsubscribe = api.subscribeToUpdates('getRiskMetrics', (data) => {
      setRiskData({
        data,
        loading: false
      });
    });

    return () => unsubscribe();
  }, []);

  const getRiskLevelColor = (level) => {
    const levels = {
      LOW: 'bg-green-500/20 text-green-300',
      MEDIUM: 'bg-yellow-500/20 text-yellow-300',
      HIGH: 'bg-red-500/20 text-red-300',
      CRITICAL: 'bg-red-600/20 text-red-400'
    };
    return levels[level] || 'bg-gray-500/20 text-gray-300';
  };

  if (riskData.loading) {
    return (
      <div className="flex items-center justify-center h-48">
        <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-400"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Risk Overview */}
      {riskData.data && (
        <div className="bg-gray-800/50 backdrop-blur-lg rounded-xl border border-gray-700/30 p-6">
          <h2 className="text-xl font-semibold text-gray-100 mb-4">Risk Metrics</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="p-4 bg-gray-900/30 rounded">
              <div className="text-sm text-gray-400">VaR (95%)</div>
              <div className="text-xl text-red-400">
                ${riskData.data.value_at_risk.toLocaleString()}
              </div>
            </div>
            <div className="p-4 bg-gray-900/30 rounded">
              <div className="text-sm text-gray-400">Portfolio Beta</div>
              <div className="text-xl text-blue-400">
                {riskData.data.portfolio_beta.toFixed(2)}
              </div>
            </div>
            <div className="p-4 bg-gray-900/30 rounded">
              <div className="text-sm text-gray-400">Sharpe Ratio</div>
              <div className="text-xl text-green-400">
                {riskData.data.sharpe_ratio.toFixed(2)}
              </div>
            </div>
            <div className="p-4 bg-gray-900/30 rounded">
              <div className="text-sm text-gray-400">Market Correlation</div>
              <div className="text-xl text-purple-400">
                {(riskData.data.market_correlation * 100).toFixed(1)}%
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Risk Alerts */}
      {riskData.data?.risk_alerts && (
        <div className="bg-gray-800/50 backdrop-blur-lg rounded-xl border border-gray-700/30 p-6">
          <h2 className="text-xl font-semibold text-gray-100 mb-4">Active Risk Alerts</h2>
          <div className="space-y-3">
            {riskData.data.risk_alerts.map((alert, index) => (
              <div 
                key={index}
                className="flex items-center justify-between p-4 bg-gray-900/30 rounded"
              >
                <div className="flex items-center space-x-4">
                  <div className={`px-2 py-1 text-sm font-medium rounded-md ${getRiskLevelColor(alert.level)}`}>
                    {alert.level}
                  </div>
                  <div>
                    <div className="font-medium text-gray-300">{alert.title}</div>
                    <div className="text-sm text-gray-500">{alert.description}</div>
                  </div>
                </div>
                <div className="text-sm text-gray-500">
                  {new Date(alert.timestamp).toLocaleTimeString()}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Position Risk Analysis */}
      {riskData.data?.position_risks && (
        <div className="bg-gray-800/50 backdrop-blur-lg rounded-xl border border-gray-700/30 p-6">
          <h2 className="text-xl font-semibold text-gray-100 mb-4">Position Risk Analysis</h2>
          <div className="space-y-3">
            {riskData.data.position_risks.map((position, index) => (
              <div 
                key={index}
                className="grid grid-cols-1 md:grid-cols-4 gap-4 p-4 bg-gray-900/30 rounded items-center"
              >
                <div>
                  <div className="font-medium text-gray-300">{position.symbol}</div>
                  <div className="text-sm text-gray-500">Size: {position.position_size}%</div>
                </div>
                <div>
                  <div className="text-sm text-gray-400">Volatility</div>
                  <div className="text-sm text-blue-400">{(position.volatility * 100).toFixed(1)}%</div>
                </div>
                <div>
                  <div className="text-sm text-gray-400">Max Drawdown</div>
                  <div className="text-sm text-red-400">{(position.max_drawdown * 100).toFixed(1)}%</div>
                </div>
                <div>
                  <div className="text-sm text-gray-400">Risk Score</div>
                  <div className={`text-sm font-medium ${getRiskLevelColor(position.risk_level)}`}>
                    {position.risk_score}/10
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default RiskDashboard;