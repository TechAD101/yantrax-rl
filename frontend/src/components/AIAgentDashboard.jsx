import React from 'react'

const AIAgentDashboard = ({ aiData }) => {
  const agents = aiData?.agents || {}

  // Agent configuration with enhanced styling
  const agentConfig = {
    'macro_monk': {
      name: 'Macro Monk',
      icon: '🧘',
      color: 'from-purple-500 to-blue-600',
      description: 'Macroeconomic trend analysis',
      specialty: 'Trend Following'
    },
    'the_ghost': {
      name: 'The Ghost',
      icon: '👻',
      color: 'from-gray-500 to-gray-700',
      description: 'Stealth trading patterns',
      specialty: 'Pattern Recognition'
    },
    'data_whisperer': {
      name: 'Data Whisperer',
      icon: '🔮',
      color: 'from-cyan-500 to-teal-600',
      description: 'Deep data insights',
      specialty: 'Statistical Analysis'
    },
    'degen_auditor': {
      name: 'Degen Auditor',
      icon: '🔍',
      color: 'from-red-500 to-orange-600',
      description: 'Risk assessment specialist',
      specialty: 'Risk Management'
    }
  }

  if (!aiData || Object.keys(agents).length === 0) {
    return (
      <div className="bg-gray-800/50 backdrop-blur-lg rounded-xl border border-gray-700/30 p-6">
        <h2 className="text-xl font-semibold mb-4 text-gray-100">AI Agent Dashboard</h2>
        <div className="flex items-center justify-center h-32">
          <p className="text-gray-400">Loading AI agents...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
          AI Agent Command Center
        </h2>
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
          <span className="text-sm text-gray-400">All Agents Active</span>
        </div>
      </div>

      {/* Agent Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {Object.entries(agents).map(([agentKey, data]) => {
          const config = agentConfig[agentKey] || {
            name: agentKey.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()),
            icon: '🤖',
            color: 'from-gray-600 to-gray-800',
            description: 'AI Trading Agent',
            specialty: 'Trading'
          }

          return (
            <div
              key={agentKey}
              className="bg-gray-800/50 backdrop-blur-lg rounded-xl border border-gray-700/30 p-6 hover:border-gray-600/50 transition-all duration-300 hover:transform hover:scale-105"
            >
              {/* Agent Header */}
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className={`w-10 h-10 rounded-full bg-gradient-to-br ${config.color} flex items-center justify-center text-lg`}>
                    {config.icon}
                  </div>
                  <div>
                    <h3 className="font-semibold text-white text-sm">{config.name}</h3>
                    <p className="text-xs text-gray-400">{config.specialty}</p>
                  </div>
                </div>
                <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                  data.confidence > 0.8 ? 'bg-green-900/50 text-green-300 border border-green-700' :
                  data.confidence > 0.6 ? 'bg-yellow-900/50 text-yellow-300 border border-yellow-700' :
                  'bg-red-900/50 text-red-300 border border-red-700'
                }`}>
                  {data.confidence ? `${(data.confidence * 100).toFixed(0)}%` : 'N/A'}
                </div>
              </div>

              {/* Agent Metrics */}
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-gray-400 text-sm">Performance:</span>
                  <span className="text-green-300 font-mono text-sm font-bold">
                    {data.performance ? `${data.performance}%` : 'N/A'}
                  </span>
                </div>

                <div className="flex justify-between items-center">
                  <span className="text-gray-400 text-sm">Status:</span>
                  <span className="text-blue-300 text-xs">
                    {data.signal || data.analysis || data.audit || 'Active'}
                  </span>
                </div>

                {/* Confidence Bar */}
                <div className="mt-3">
                  <div className="flex justify-between text-xs text-gray-400 mb-1">
                    <span>Confidence</span>
                    <span>{data.confidence ? `${(data.confidence * 100).toFixed(1)}%` : '0%'}</span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full transition-all duration-1000 ${
                        data.confidence > 0.8 ? 'bg-gradient-to-r from-green-500 to-green-400' :
                        data.confidence > 0.6 ? 'bg-gradient-to-r from-yellow-500 to-yellow-400' :
                        'bg-gradient-to-r from-red-500 to-red-400'
                      }`}
                      style={{ width: `${(data.confidence || 0) * 100}%` }}
                    ></div>
                  </div>
                </div>
              </div>

              {/* Agent Description */}
              <div className="mt-4 pt-3 border-t border-gray-700/50">
                <p className="text-xs text-gray-500">{config.description}</p>
              </div>
            </div>
          )
        })}
      </div>

      {/* Agent Consensus Panel */}
      <div className="bg-gray-800/50 backdrop-blur-lg rounded-xl border border-gray-700/30 p-6">
        <h3 className="text-lg font-semibold mb-4 text-gray-100">Agent Consensus</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-300">
              {aiData?.signal || 'ANALYZING'}
            </div>
            <div className="text-sm text-gray-400">Trading Signal</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-300">
              {Object.values(agents).length > 0 ?
                `${(Object.values(agents).reduce((acc, agent) => acc + agent.confidence, 0) / Object.values(agents).length * 100).toFixed(1)}%` :
                '85%'
              }
            </div>
            <div className="text-sm text-gray-400">Avg Confidence</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-300">
              {Object.values(agents).length > 0 ?
                `${(Object.values(agents).reduce((acc, agent) => acc + agent.performance, 0) / Object.values(agents).length).toFixed(1)}%` :
                '17.2%'
              }
            </div>
            <div className="text-sm text-gray-400">Avg Performance</div>
          </div>
        </div>

        {/* Strategy Information */}
        <div className="mt-6 p-4 bg-gray-900/50 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <h4 className="font-medium text-gray-100">Active Strategy</h4>
              <p className="text-sm text-gray-400">{aiData?.strategy || 'AI_ENSEMBLE'}</p>
            </div>
            <div className="text-right">
              <div className="text-sm text-gray-400">Execution Time</div>
              <div className="font-mono text-green-300">
                {aiData?.executionTime ? `${aiData.executionTime}ms` : '<100ms'}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default AIAgentDashboard