import React from 'react';
import useMarketStream from '../hooks/useMarketStream';

const AssetMonitor = ({ symbol, interval = 5 }) => {
  const { price, isLoading, error, lastUpdate } = useMarketStream(symbol, { interval, count: 0 });

  const display = isLoading
    ? '⏳'
    : (price !== null && price !== undefined ? price.toFixed(2) : 'Data unavailable');

  const errorMessage = (() => {
    if (!error) return lastUpdate ? new Date(lastUpdate).toLocaleTimeString() : '';
    if (error === 'fallback') return 'Using cached price';
    if (typeof error === 'string' && error.startsWith('provider_error')) return 'Data unavailable';
    return `Error: ${error}`;
  })();

  return (
    <div className="bg-gray-900/40 rounded-lg p-3 border border-gray-700/20">
      <div className="font-semibold text-sm text-gray-200 mb-1">{symbol}</div>
      <div className="text-lg font-bold text-white">{display}</div>
      <div className={`text-xs font-medium text-gray-400`}> 
        {errorMessage}
      </div>
    </div>
  );
};

export default AssetMonitor;
