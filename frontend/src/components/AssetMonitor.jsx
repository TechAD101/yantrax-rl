import React from 'react';
import useMarketStream from '../hooks/useMarketStream';

const AssetMonitor = ({ symbol, interval = 5 }) => {
  const { price, isLoading, error, lastUpdate } = useMarketStream(symbol, { interval, count: 0 });

  const display = isLoading ? '⏳' : (price !== null && price !== undefined ? price.toFixed(2) : '--');

  return (
    <div className="bg-gray-900/40 rounded-lg p-3 border border-gray-700/20">
      <div className="font-semibold text-sm text-gray-200 mb-1">{symbol}</div>
      <div className="text-lg font-bold text-white">{display}</div>
      <div className={`text-xs font-medium text-gray-400`}> 
        {error ? `Error: ${error}` : (lastUpdate ? new Date(lastUpdate).toLocaleTimeString() : '')}
      </div>
    </div>
  );
};

export default AssetMonitor;
