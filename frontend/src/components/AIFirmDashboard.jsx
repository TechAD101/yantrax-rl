import React, { useState, useEffect } from 'react';
import { api } from '../api/api';
import PortfolioManager from './PortfolioManager';
import RiskDashboard from './RiskDashboard';
import PerformanceTracker from './PerformanceTracker';

const AIFirmDashboard = () => {
  const [firmData, setFirmData] = useState({
    departments: {},
    ceo_oversight: {},
    system_performance: {},
    loading: true
  });

  useEffect(() => {
    const unsubscribe = api.subscribeToUpdates('getAiFirmStatus', (data) => {
      setFirmData({
        ...data,
        loading: false
      });
    });

    return () => unsubscribe();
  }, []);

  // Render department section
  const renderDepartment = (dept, data) => (
    <div key={dept} className="bg-gray-800/50 backdrop-blur-lg rounded-xl border border-gray-700/30 p-6">
      <h3 className="text-xl font-semibold mb-4 text-gray-100">
        {dept.replace('_', ' ').toUpperCase()}
      </h3>
      <div className="space-y-4">
        {/* Department Stats */}
        <div className="grid grid-cols-2 gap-4">
          <div className="text-gray-400">
            Agents: <span className="text-blue-300">{data.agent_count}</span>
          </div>
          <div className="text-gray-400">
            Avg Confidence: <span className="text-green-300">{(data.avg_confidence * 100).toFixed(1)}%</span>
          </div>
        </div>
        
        {/* Agent List */}
        <div className="space-y-2">
          {data.agents.map((agent) => (
            <div key={agent.id} className="flex items-center justify-between p-2 bg-gray-900/30 rounded">
              <div>
                <div className="text-sm font-medium text-gray-300">{agent.name}</div>
                <div className="text-xs text-gray-500">{agent.specialty}</div>
              </div>
              <div className="text-xs">
                <span className="text-blue-400">{(agent.performance).toFixed(1)}</span>
                <span className="text-gray-500 mx-1">•</span>
                <span className="text-green-400">{(agent.confidence * 100).toFixed(0)}%</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  // Loading state
  if (firmData.loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-400"></div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* CEO Overview */}
      <div className="bg-gray-800/50 backdrop-blur-lg rounded-xl border border-gray-700/30 p-6">
        <h2 className="text-xl font-semibold mb-4 text-gray-100">CEO Oversight</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="p-4 bg-gray-900/30 rounded">
            <div className="text-sm text-gray-400">Average Confidence</div>
            <div className="text-xl text-green-400">
              {(firmData.ceo_oversight?.average_confidence * 100).toFixed(1)}%
            </div>
          </div>
          <div className="p-4 bg-gray-900/30 rounded">
            <div className="text-sm text-gray-400">Recent Decisions</div>
            <div className="text-xl text-blue-400">
              {firmData.ceo_oversight?.recent_decisions}
            </div>
          </div>
          <div className="p-4 bg-gray-900/30 rounded">
            <div className="text-sm text-gray-400">Success Rate</div>
            <div className="text-xl text-green-400">
              {firmData.system_performance?.success_rate}%
            </div>
          </div>
          <div className="p-4 bg-gray-900/30 rounded">
            <div className="text-sm text-gray-400">Portfolio Balance</div>
            <div className="text-xl text-blue-400">
              ${firmData.system_performance?.portfolio_balance.toLocaleString()}
            </div>
          </div>
        </div>
      </div>

      {/* Portfolio Management */}
      <div className="bg-gray-800/50 backdrop-blur-lg rounded-xl border border-gray-700/30">
        <PortfolioManager />
      </div>

      {/* Risk Dashboard */}
      <div className="bg-gray-800/50 backdrop-blur-lg rounded-xl border border-gray-700/30">
        <RiskDashboard />
      </div>

      {/* Performance Tracker */}
      <div className="bg-gray-800/50 backdrop-blur-lg rounded-xl border border-gray-700/30">
        <PerformanceTracker />
      </div>

      {/* Departments Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {Object.entries(firmData.departments || {}).map(([dept, data]) => 
          renderDepartment(dept, data)
        )}
      </div>
    </div>
  );
};

export default AIFirmDashboard;