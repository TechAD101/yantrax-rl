import React, { useState, useEffect } from 'react';
import { api } from '../api/api';

const DepartmentView = () => {
  const [departments, setDepartments] = useState({
    data: null,
    loading: true
  });

  useEffect(() => {
    const unsubscribe = api.subscribeToUpdates('getAiFirmStatus', (data) => {
      setDepartments({
        data: data.departments,
        loading: false
      });
    });

    return () => unsubscribe();
  }, []);

  const getDepartmentColor = (dept) => {
    const colors = {
      market_intelligence: 'blue',
      risk_control: 'red',
      trade_operations: 'green',
      performance_lab: 'yellow',
      communications: 'purple'
    };
    return colors[dept] || 'gray';
  };

  if (departments.loading) {
    return (
      <div className="flex items-center justify-center h-48">
        <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-400"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Department Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
        {departments.data && Object.entries(departments.data).map(([dept, data]) => (
          <div 
            key={dept}
            className="bg-gray-800/50 backdrop-blur-lg rounded-xl border border-gray-700/30 p-4"
          >
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-medium text-gray-300">
                {dept.replace('_', ' ').toUpperCase()}
              </h3>
              <div className={`w-2 h-2 rounded-full bg-${getDepartmentColor(dept)}-500`}></div>
            </div>
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="text-gray-500">Agents</div>
              <div className="text-right text-blue-400">{data.agent_count}</div>
              <div className="text-gray-500">Confidence</div>
              <div className="text-right text-green-400">
                {(data.avg_confidence * 100).toFixed(1)}%
              </div>
              <div className="text-gray-500">Performance</div>
              <div className="text-right text-blue-400">
                {data.avg_performance?.toFixed(1) || 'N/A'}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Detailed Agent List */}
      {departments.data && Object.entries(departments.data).map(([dept, data]) => (
        <div key={dept} className="bg-gray-800/50 backdrop-blur-lg rounded-xl border border-gray-700/30 p-6">
          <h3 className="text-lg font-semibold text-gray-100 mb-4">
            {dept.replace('_', ' ').toUpperCase()} AGENTS
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {data.agents.map((agent) => (
              <div 
                key={agent.id}
                className="p-4 bg-gray-900/30 rounded-lg border border-gray-700/10"
              >
                <div className="flex items-center justify-between mb-2">
                  <div>
                    <div className="font-medium text-gray-300">{agent.name}</div>
                    <div className="text-xs text-gray-500">{agent.role}</div>
                  </div>
                  <div className={`px-2 py-1 text-xs font-medium bg-${getDepartmentColor(dept)}-500/20 text-${getDepartmentColor(dept)}-300 rounded-md`}>
                    {agent.specialty}
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div className="text-gray-500">Performance</div>
                  <div className="text-right text-blue-400">
                    {agent.performance.toFixed(1)}
                  </div>
                  <div className="text-gray-500">Confidence</div>
                  <div className="text-right text-green-400">
                    {(agent.confidence * 100).toFixed(1)}%
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
};

export default DepartmentView;