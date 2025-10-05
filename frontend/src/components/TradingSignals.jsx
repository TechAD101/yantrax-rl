import React, { useState, useEffect } from 'react';
import { api } from '../api/api';

const TradingSignals = () => {
  const [signals, setSignals] = useState({
    current: null,
    history: [],
    loading: true
  });

  useEffect(() => {
    const unsubscribe = api.subscribeToUpdates('getGodCycle', (data) => {
      setSignals({
        current: {
          signal: data.signal,
          strategy: data.strategy,
          confidence: data.performance_metrics?.coordination_strength || 0,
          timestamp: data.timestamp
        },
        history: data.signal_history || [],
        loading: false
      });
    });

    return () => unsubscribe();
  }, []);

  const getSignalColor = (signal) => {
    switch (signal?.toUpperCase()) {
      case 'BUY': return 'green';
      case 'SELL': return 'red';
      case 'HOLD': return 'yellow';
      default: return 'gray';
    }
  };

  if (signals.loading) {
    return (
      <div className="flex items-center justify-center h-48">
        <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-400"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Current Signal */}
      {signals.current && (
        <div className="bg-gray-800/50 backdrop-blur-lg rounded-xl border border-gray-700/30 p-6">
          <h2 className="text-xl font-semibold text-gray-100 mb-4">Current Signal</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="p-4 bg-gray-900/30 rounded">
              <div className="text-sm text-gray-400">Signal</div>
              <div className={`text-xl text-${getSignalColor(signals.current.signal)}-400`}>
                {signals.current.signal}
              </div>
            </div>
            <div className="p-4 bg-gray-900/30 rounded">
              <div className="text-sm text-gray-400">Strategy</div>
              <div className="text-xl text-blue-400">
                {signals.current.strategy}
              </div>
            </div>
            <div className="p-4 bg-gray-900/30 rounded">
              <div className="text-sm text-gray-400">Confidence</div>
              <div className="text-xl text-green-400">
                {(signals.current.confidence * 100).toFixed(1)}%
              </div>
            </div>
            <div className="p-4 bg-gray-900/30 rounded">
              <div className="text-sm text-gray-400">Time</div>
              <div className="text-xl text-gray-300">
                {new Date(signals.current.timestamp).toLocaleTimeString()}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Signal History */}
      <div className="bg-gray-800/50 backdrop-blur-lg rounded-xl border border-gray-700/30 p-6">
        <h2 className="text-xl font-semibold text-gray-100 mb-4">Signal History</h2>
        <div className="space-y-3">
          {signals.history.map((signal, index) => (
            <div 
              key={index}
              className="flex items-center justify-between p-4 bg-gray-900/30 rounded"
            >
              <div className="flex items-center space-x-4">
                <div className={`px-2 py-1 text-sm font-medium bg-${getSignalColor(signal.signal)}-500/20 text-${getSignalColor(signal.signal)}-300 rounded-md`}>
                  {signal.signal}
                </div>
                <div className="text-sm text-gray-400">
                  {signal.strategy}
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <div className="text-sm text-green-400">
                  {(signal.confidence * 100).toFixed(1)}%
                </div>
                <div className="text-sm text-gray-500">
                  {new Date(signal.timestamp).toLocaleTimeString()}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default TradingSignals;