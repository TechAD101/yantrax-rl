import React, { useState, useEffect } from 'react';
import { api } from '../api/api';

const PersonaAnalysis = () => {
  const [personaData, setPersonaData] = useState({
    warren: null,
    cathie: null,
    loading: true
  });

  useEffect(() => {
    const loadPersonaData = async () => {
      try {
        const [warrenData, cathieData] = await Promise.all([
          api.getWarrenAnalysis(),
          api.getCathieAnalysis()
        ]);
        
        setPersonaData({
          warren: warrenData,
          cathie: cathieData,
          loading: false
        });
      } catch (error) {
        console.error('Failed to load persona data:', error);
        setPersonaData(prev => ({ ...prev, loading: false }));
      }
    };

    // Initial load
    loadPersonaData();

    // Subscribe to updates
    const timer = setInterval(loadPersonaData, 15000);
    return () => clearInterval(timer);
  }, []);

  if (personaData.loading) {
    return (
      <div className="flex items-center justify-center h-48">
        <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-400"></div>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      {/* Warren's Analysis */}
      <div className="bg-gray-800/50 backdrop-blur-lg rounded-xl border border-gray-700/30 p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-gray-100">Warren's Analysis</h2>
          <div className="px-2 py-1 text-xs font-medium bg-blue-500/20 text-blue-300 rounded-md">
            VALUE FOCUS
          </div>
        </div>

        {personaData.warren && (
          <>
            {/* Metrics */}
            <div className="grid grid-cols-2 gap-4 mb-6">
              <div className="p-3 bg-gray-900/30 rounded">
                <div className="text-sm text-gray-400">Confidence</div>
                <div className="text-lg text-blue-400">
                  {(personaData.warren.confidence * 100).toFixed(1)}%
                </div>
              </div>
              <div className="p-3 bg-gray-900/30 rounded">
                <div className="text-sm text-gray-400">Performance</div>
                <div className="text-lg text-green-400">
                  {personaData.warren.performance.toFixed(1)}
                </div>
              </div>
            </div>

            {/* Analysis */}
            <div className="space-y-3">
              <div className="text-sm text-gray-400">Latest Analysis</div>
              <div className="p-3 bg-gray-900/30 rounded text-sm text-gray-300">
                {personaData.warren.latest_analysis}
              </div>
            </div>
          </>
        )}
      </div>

      {/* Cathie's Analysis */}
      <div className="bg-gray-800/50 backdrop-blur-lg rounded-xl border border-gray-700/30 p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-gray-100">Cathie's Analysis</h2>
          <div className="px-2 py-1 text-xs font-medium bg-purple-500/20 text-purple-300 rounded-md">
            INNOVATION FOCUS
          </div>
        </div>

        {personaData.cathie && (
          <>
            {/* Metrics */}
            <div className="grid grid-cols-2 gap-4 mb-6">
              <div className="p-3 bg-gray-900/30 rounded">
                <div className="text-sm text-gray-400">Confidence</div>
                <div className="text-lg text-blue-400">
                  {(personaData.cathie.confidence * 100).toFixed(1)}%
                </div>
              </div>
              <div className="p-3 bg-gray-900/30 rounded">
                <div className="text-sm text-gray-400">Performance</div>
                <div className="text-lg text-green-400">
                  {personaData.cathie.performance.toFixed(1)}
                </div>
              </div>
            </div>

            {/* Analysis */}
            <div className="space-y-3">
              <div className="text-sm text-gray-400">Latest Analysis</div>
              <div className="p-3 bg-gray-900/30 rounded text-sm text-gray-300">
                {personaData.cathie.latest_analysis}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default PersonaAnalysis;