import React from 'react'

const LiveMarketData = ({ marketData, loading = false }) => {
  if (loading) {
    return (
      <div className="bg-gray-800/50 backdrop-blur-lg rounded-xl border border-gray-700/30 p-6">
        <h2 className="text-xl font-semibold mb-4 text-gray-100">Market Data</h2>
        <div className="space-y-3">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="flex justify-between">
              <div className="h-4 bg-gray-700 rounded animate-pulse w-20"></div>
              <div className="h-4 bg-gray-700 rounded animate-pulse w-16"></div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="bg-gray-800/50 backdrop-blur-lg rounded-xl border border-gray-700/30 p-6 hover:border-gray-600/50 transition-all duration-300">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold text-gray-100">Live Market Data</h2>
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
        </div>
      </div>
      
      <div className="space-y-4">
        {/* Primary Symbol */}
        <div className="flex justify-between items-center py-2 border-b border-gray-700/50">
          <span className="text-gray-400 font-medium">Symbol:</span>
          <div className="text-right">
            <span className="font-mono text-blue-300 text-lg font-bold">
              {marketData?.symbol || 'Loading...'}
            </span>
            <div className="text-xs text-gray-600">
              {marketData?.error ? 'Data Unavailable' : 'Live Feed'}
            </div>
          </div>
        </div>

        {/* Current Price */}
        <div className="flex justify-between items-center py-2">
          <span className="text-gray-400 font-medium">Current Price:</span>
          <div className="text-right">
            <span className={`font-mono text-xl font-bold ${
              marketData?.changePercent >= 0 ? 'text-green-300' : 'text-red-300'
            }`}>
              {marketData?.price || 'Loading...'}
            </span>
            <div className="text-xs text-gray-500">
              Live Price
            </div>
          </div>
        </div>

        {/* Price Change */}
        <div className="flex justify-between items-center py-2">
          <span className="text-gray-400 font-medium">24h Change:</span>
          <div className="text-right">
            <span className={`font-mono font-bold ${
              marketData?.changePercent >= 0 ? 'text-green-300' : 'text-red-300'
            }`}>
              {marketData?.change || 'Loading...'}
            </span>
            <div className={`text-xs ${
              marketData?.changePercent >= 0 ? 'text-green-400' : 'text-red-400'
            }`}>
              {marketData?.changePercent !== undefined ? 
                `${marketData.changePercent >= 0 ? '+' : ''}${marketData.changePercent.toFixed(2)}%` : 
                'Loading...'
              }
            </div>
          </div>
        </div>

        {/* Volume */}
        <div className="flex justify-between items-center py-2">
          <span className="text-gray-400 font-medium">Volume:</span>
          <div className="text-right">
            <span className="font-mono text-gray-300 font-bold">
              {marketData?.volume || 'Loading...'}
            </span>
            <div className="text-xs text-gray-500">
              24h Volume
            </div>
          </div>
        </div>

        {/* Data Source */}
        <div className="flex justify-between items-center py-2 pt-4 border-t border-gray-700/30">
          <span className="text-gray-400 font-medium text-sm">Data Source:</span>
          <div className="text-right">
            <span className="text-xs text-gray-400 capitalize">
              {marketData?.source?.replace('_', ' ') || 'Loading...'}
            </span>
            <div className="text-xs text-gray-600">
              {marketData?.timestamp ? 
                new Date(marketData.timestamp).toLocaleTimeString() : 
                'Updating...'
              }
            </div>
          </div>
        </div>
      </div>

      {/* Market Status Indicator */}
      <div className="mt-4 p-3 bg-gray-900/50 rounded-lg">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className={`w-3 h-3 rounded-full ${
              marketData?.changePercent >= 0 ? 'bg-green-500' : 'bg-red-500'
            } animate-pulse`}></div>
            <span className="text-sm font-medium text-gray-300">
              {marketData?.changePercent >= 0 ? 'Market Up' : 'Market Down'}
            </span>
          </div>
          <div className="text-xs text-gray-500">
            {marketData?.error ? 'Data Unavailable' : 'Live Feed'}
          </div>
        </div>
      </div>

      {/* Quick Stats */}
      {marketData && (
        <div className="mt-4 grid grid-cols-2 gap-3">
          <div className="bg-gray-900/30 rounded-lg p-3">
            <div className="text-xs text-gray-400">Prev Close</div>
            <div className="font-mono text-sm text-gray-300">
              ${marketData.previousClose || 'N/A'}
            </div>
          </div>
          <div className="bg-gray-900/30 rounded-lg p-3">
            <div className="text-xs text-gray-400">Market Cap</div>
            <div className="font-mono text-sm text-gray-300">
              {marketData.marketCap ? 
                `$${(marketData.marketCap / 1e9).toFixed(1)}B` : 'N/A'
              }
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default LiveMarketData