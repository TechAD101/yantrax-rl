import React, { useState, useEffect } from 'react';
import { api, subscribeToUpdates } from '../api/api';
import Navigation from '../components/Navigation';

const YantraDashboard = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  
  // Market Data State
  const [marketData, setMarketData] = useState({
    symbol: 'BTC/USD',
    price: null,
    change: null,
    volume: null,
    loading: true
  });
  
  // AI Firm State
  const [aiData, setAiData] = useState({
    signal: null,
    confidence: null,
    nextAction: null,
    departments: [],
    total_agents: 0,
    loading: true
  });
  
  // Portfolio State
  const [portfolio, setPortfolio] = useState({
    total_value: 0,
    daily_pnl: 0,
    total_positions: 0,
    loading: true
  });

  // Setup real-time data subscriptions
  useEffect(() => {
    const subscriptions = [
      subscribeToUpdates('getMarketPrice', (data) => {
        setMarketData({
          ...data,
          loading: false
        });
      }),
      
      subscribeToUpdates('getAiFirmStatus', (data) => {
        setAiData({
          signal: data.latest_signal,
          confidence: data.signal_confidence,
          nextAction: data.recommended_action,
          departments: data.departments,
          total_agents: data.total_agents,
          loading: false
        });
      }),
      
      subscribeToUpdates('getPortfolio', (data) => {
        setPortfolio({
          ...data,
          loading: false
        });
      })
    ];

    // Cleanup subscriptions
    return () => subscriptions.forEach(unsub => unsub());
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black text-white">
      <header className="border-b border-gray-700/50 bg-gray-900/80 backdrop-blur-xl">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                YantraX RL Dashboard
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-400">Status: Active</span>
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
            </div>
          </div>
        </div>
      </header>

      <main className="p-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Market Data Card */}
          <div className="bg-gray-800/50 backdrop-blur-lg rounded-xl border border-gray-700/30 p-6">
            <h2 className="text-xl font-semibold mb-4 text-gray-100">Market Data</h2>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-400">Symbol:</span>
                <span className="font-mono text-blue-300">{marketData.symbol}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Price:</span>
                <span className="font-mono text-green-300">{marketData.price}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">24h Change:</span>
                <span className="font-mono text-green-300">{marketData.change}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Volume:</span>
                <span className="font-mono text-gray-300">{marketData.volume}</span>
              </div>
            </div>
          </div>

          {/* AI Signal Card */}
          <div className="bg-gray-800/50 backdrop-blur-lg rounded-xl border border-gray-700/30 p-6">
            <h2 className="text-xl font-semibold mb-4 text-gray-100">AI Signal</h2>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-400">Signal:</span>
                <span className="font-mono text-green-400 font-bold">{aiData.signal}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Confidence:</span>
                <span className="font-mono text-blue-300">{aiData.confidence}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Next Action:</span>
                <span className="font-mono text-yellow-300">{aiData.nextAction}</span>
              </div>
            </div>
          </div>

          {/* Portfolio Summary */}
          <div className="bg-gray-800/50 backdrop-blur-lg rounded-xl border border-gray-700/30 p-6">
            <h2 className="text-xl font-semibold mb-4 text-gray-100">Portfolio</h2>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-400">Total Value:</span>
                <span className="font-mono text-green-300">$12,430.50</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">P&L Today:</span>
                <span className="font-mono text-green-300">+$234.20</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Active Positions:</span>
                <span className="font-mono text-blue-300">3</span>
              </div>
            </div>
          </div>
        </div>

        {/* Charts Section */}
        <div className="mt-8">
          <div className="bg-gray-800/50 backdrop-blur-lg rounded-xl border border-gray-700/30 p-6">
            <h2 className="text-xl font-semibold mb-4 text-gray-100">Price Chart</h2>
            <div className="h-64 flex items-center justify-center bg-gray-900/50 rounded-lg border border-gray-700/30">
              <p className="text-gray-400">Chart visualization will be implemented here</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

export default YantraDashboard