import React, { useState, useEffect } from 'react';
import { api } from '../api/api';

const CEOPanel = () => {
  const [ceoData, setCeoData] = useState({
    decisions: [],
    metrics: {},
    loading: true
  });

  useEffect(() => {
    const unsubscribe = api.subscribeToUpdates('getAiFirmStatus', (data) => {
      setCeoData({
        decisions: data.ceo_oversight?.recent_decisions || [],
        metrics: {
          confidence: data.ceo_oversight?.average_confidence || 0,
          success_rate: data.system_performance?.success_rate || 0,
          portfolio_balance: data.system_performance?.portfolio_balance || 0,
          supernatural_mode: data.system_performance?.supernatural_mode || false
        },
        loading: false
      });
    });

    return () => unsubscribe();
  }, []);

  if (ceoData.loading) {
    return (
      <div className="flex items-center justify-center h-48">
        <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-400"></div>
      </div>
    );
  }

  return (
    <div className="bg-gray-800/50 backdrop-blur-lg rounded-xl border border-gray-700/30 p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-gray-100">CEO Strategic Oversight</h2>
        <div className="flex items-center space-x-2">
          <span className={`px-2 py-1 text-xs font-medium rounded-md ${
            ceoData.metrics.supernatural_mode 
              ? 'bg-purple-500/20 text-purple-300'
              : 'bg-blue-500/20 text-blue-300'
          }`}>
            {ceoData.metrics.supernatural_mode ? 'SUPERNATURAL' : 'ENHANCED'}
          </span>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="p-4 bg-gray-900/30 rounded">
          <div className="text-sm text-gray-400">Strategic Confidence</div>
          <div className="text-xl text-green-400">
            {(ceoData.metrics.confidence * 100).toFixed(1)}%
          </div>
        </div>
        <div className="p-4 bg-gray-900/30 rounded">
          <div className="text-sm text-gray-400">Success Rate</div>
          <div className="text-xl text-blue-400">
            {ceoData.metrics.success_rate}%
          </div>
        </div>
        <div className="p-4 bg-gray-900/30 rounded">
          <div className="text-sm text-gray-400">Portfolio Value</div>
          <div className="text-xl text-green-400">
            ${ceoData.metrics.portfolio_balance.toLocaleString()}
          </div>
        </div>
      </div>

      {/* Recent Decisions */}
      <div>
        <h3 className="text-sm font-medium text-gray-400 mb-3">Recent Strategic Decisions</h3>
        <div className="space-y-2">
          {ceoData.decisions.map((decision, index) => (
            <div 
              key={index}
              className="flex items-center justify-between p-3 bg-gray-900/30 rounded"
            >
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 rounded-full bg-green-500"></div>
                <span className="text-sm text-gray-300">{decision.action}</span>
              </div>
              <div className="text-xs text-gray-500">
                {new Date(decision.timestamp).toLocaleTimeString()}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default CEOPanel;