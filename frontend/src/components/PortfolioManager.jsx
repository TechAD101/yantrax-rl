import React, { useState, useEffect } from 'react';
import { api } from '../api/api';

const PortfolioManager = () => {
  const [portfolio, setPortfolio] = useState({
    data: null,
    loading: true
  });

  useEffect(() => {
    const unsubscribe = api.subscribeToUpdates('getPortfolio', (data) => {
      setPortfolio({
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

  if (portfolio.loading) {
    return (
      <div className="flex items-center justify-center h-48">
        <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-400"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Portfolio Summary */}
      {portfolio.data && (
        <div className="bg-gray-800/50 backdrop-blur-lg rounded-xl border border-gray-700/30 p-6">
          <h2 className="text-xl font-semibold text-gray-100 mb-4">Portfolio Summary</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="p-4 bg-gray-900/30 rounded">
              <div className="text-sm text-gray-400">Total Value</div>
              <div className="text-xl text-green-400">
                {formatCurrency(portfolio.data.total_value)}
              </div>
            </div>
            <div className="p-4 bg-gray-900/30 rounded">
              <div className="text-sm text-gray-400">Daily P&L</div>
              <div className={`text-xl ${
                portfolio.data.daily_pnl >= 0 ? 'text-green-400' : 'text-red-400'
              }`}>
                {formatCurrency(portfolio.data.daily_pnl)}
              </div>
            </div>
            <div className="p-4 bg-gray-900/30 rounded">
              <div className="text-sm text-gray-400">Return</div>
              <div className={`text-xl ${
                portfolio.data.total_return >= 0 ? 'text-green-400' : 'text-red-400'
              }`}>
                {formatPercent(portfolio.data.total_return)}
              </div>
            </div>
            <div className="p-4 bg-gray-900/30 rounded">
              <div className="text-sm text-gray-400">Positions</div>
              <div className="text-xl text-blue-400">
                {portfolio.data.total_positions}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Active Positions */}
      {portfolio.data?.positions && (
        <div className="bg-gray-800/50 backdrop-blur-lg rounded-xl border border-gray-700/30 p-6">
          <h2 className="text-xl font-semibold text-gray-100 mb-4">Active Positions</h2>
          <div className="space-y-3">
            {portfolio.data.positions.map((position) => (
              <div 
                key={position.symbol}
                className="flex items-center justify-between p-4 bg-gray-900/30 rounded"
              >
                <div>
                  <div className="font-medium text-gray-300">{position.symbol}</div>
                  <div className="text-sm text-gray-500">{position.quantity} units</div>
                </div>
                <div className="text-right">
                  <div className={`font-medium ${
                    position.unrealized_pnl >= 0 ? 'text-green-400' : 'text-red-400'
                  }`}>
                    {formatCurrency(position.unrealized_pnl)}
                  </div>
                  <div className="text-sm text-gray-500">
                    Avg. {formatCurrency(position.avg_price)}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recent Trades */}
      {portfolio.data?.recent_trades && (
        <div className="bg-gray-800/50 backdrop-blur-lg rounded-xl border border-gray-700/30 p-6">
          <h2 className="text-xl font-semibold text-gray-100 mb-4">Recent Trades</h2>
          <div className="space-y-3">
            {portfolio.data.recent_trades.map((trade, index) => (
              <div 
                key={index}
                className="flex items-center justify-between p-4 bg-gray-900/30 rounded"
              >
                <div className="flex items-center space-x-4">
                  <div className={`px-2 py-1 text-sm font-medium ${
                    trade.side === 'BUY' 
                      ? 'bg-green-500/20 text-green-300'
                      : 'bg-red-500/20 text-red-300'
                  } rounded-md`}>
                    {trade.side}
                  </div>
                  <div>
                    <div className="font-medium text-gray-300">{trade.symbol}</div>
                    <div className="text-sm text-gray-500">
                      {trade.quantity} @ {formatCurrency(trade.price)}
                    </div>
                  </div>
                </div>
                <div className="text-sm text-gray-500">
                  {new Date(trade.timestamp).toLocaleTimeString()}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default PortfolioManager;