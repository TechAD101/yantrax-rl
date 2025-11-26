import React, { useState, useEffect } from 'react';
import { api } from '../api/api';

const PerformanceTracker = () => {
  const [performanceData, setPerformanceData] = useState({
    data: null,
    loading: true
  });

  useEffect(() => {
    const unsubscribe = api.subscribeToUpdates('getPerformanceMetrics', (data) => {
      setPerformanceData({
        data,
        loading: false
      });
    });

    return () => unsubscribe();
  }, []);

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(value);
  };

  const formatPercent = (value) => {
    return `${(value * 100).toFixed(2)}%`;
  };

  const getPerformanceColor = (value) => {
    if (value > 0) return 'text-green-400';
    if (value < 0) return 'text-red-400';
    return 'text-gray-400';
  };

  if (performanceData.loading) {
    return (
      <div className="flex items-center justify-center h-48">
        <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-400"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Performance Overview */}
      {performanceData.data && (
        <div className="bg-gray-800/50 backdrop-blur-lg rounded-xl border border-gray-700/30 p-6">
          <h2 className="text-xl font-semibold text-gray-100 mb-4">Performance Overview</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="p-4 bg-gray-900/30 rounded">
              <div className="text-sm text-gray-400">Total Returns</div>
              <div className={`text-xl ${getPerformanceColor(performanceData.data.total_returns)}`}>
                {formatPercent(performanceData.data.total_returns)}
              </div>
            </div>
            <div className="p-4 bg-gray-900/30 rounded">
              <div className="text-sm text-gray-400">Win Rate</div>
              <div className="text-xl text-blue-400">
                {formatPercent(performanceData.data.win_rate)}
              </div>
            </div>
            <div className="p-4 bg-gray-900/30 rounded">
              <div className="text-sm text-gray-400">Best Trade</div>
              <div className="text-xl text-green-400">
                {formatPercent(performanceData.data.best_trade)}
              </div>
            </div>
            <div className="p-4 bg-gray-900/30 rounded">
              <div className="text-sm text-gray-400">Profit Factor</div>
              <div className="text-xl text-purple-400">
                {performanceData.data.profit_factor.toFixed(2)}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Monthly Performance */}
      {performanceData.data?.monthly_performance && (
        <div className="bg-gray-800/50 backdrop-blur-lg rounded-xl border border-gray-700/30 p-6">
          <h2 className="text-xl font-semibold text-gray-100 mb-4">Monthly Performance</h2>
          <div className="space-y-3">
            {performanceData.data.monthly_performance.map((month, index) => (
              <div 
                key={index}
                className="grid grid-cols-1 md:grid-cols-4 gap-4 p-4 bg-gray-900/30 rounded items-center"
              >
                <div className="font-medium text-gray-300">
                  {month.month}
                </div>
                <div>
                  <div className="text-sm text-gray-400">Returns</div>
                  <div className={`text-sm ${getPerformanceColor(month.returns)}`}>
                    {formatPercent(month.returns)}
                  </div>
                </div>
                <div>
                  <div className="text-sm text-gray-400">Trades</div>
                  <div className="text-sm text-blue-400">{month.total_trades}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-400">Win Rate</div>
                  <div className="text-sm text-green-400">{formatPercent(month.win_rate)}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Strategy Performance */}
      {performanceData.data?.strategy_performance && (
        <div className="bg-gray-800/50 backdrop-blur-lg rounded-xl border border-gray-700/30 p-6">
          <h2 className="text-xl font-semibold text-gray-100 mb-4">Strategy Performance</h2>
          <div className="space-y-3">
            {performanceData.data.strategy_performance.map((strategy, index) => (
              <div 
                key={index}
                className="grid grid-cols-1 md:grid-cols-4 gap-4 p-4 bg-gray-900/30 rounded items-center"
              >
                <div>
                  <div className="font-medium text-gray-300">{strategy.name}</div>
                  <div className="text-sm text-gray-500">{strategy.type}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-400">Returns</div>
                  <div className={`text-sm ${getPerformanceColor(strategy.returns)}`}>
                    {formatPercent(strategy.returns)}
                  </div>
                </div>
                <div>
                  <div className="text-sm text-gray-400">Success Rate</div>
                  <div className="text-sm text-blue-400">
                    {formatPercent(strategy.success_rate)}
                  </div>
                </div>
                <div>
                  <div className="text-sm text-gray-400">Trades</div>
                  <div className="text-sm text-purple-400">{strategy.total_trades}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default PerformanceTracker;