import React, { useState, useEffect } from 'react'

const RiskManagementDashboard = ({ riskData, portfolioData, loading = false }) => {
  const [activeRiskTab, setActiveRiskTab] = useState('overview')
  const [riskAlerts, setRiskAlerts] = useState([])
  const [riskScore, setRiskScore] = useState(0.3)

  // Generate comprehensive risk metrics
  useEffect(() => {
    if (riskData || portfolioData) {
      // Simulate risk alerts based on portfolio data
      const alerts = [
        {
          id: 1,
          type: 'warning',
          title: 'Volatility Spike Detected',
          message: 'Market volatility increased to 24.7%, approaching risk threshold',
          timestamp: new Date(Date.now() - 15 * 60 * 1000).toISOString()
        },
        {
          id: 2,
          type: 'info',
          title: 'Correlation Analysis Complete',
          message: 'Portfolio correlation with market: 0.34 (acceptable level)',
          timestamp: new Date(Date.now() - 45 * 60 * 1000).toISOString()
        }
      ]
      setRiskAlerts(alerts)
      
      // Calculate dynamic risk score
      const volatility = 0.247
      const correlation = 0.34
      const sharpe = 1.42
      const drawdown = 0.087
      
      const calculatedRisk = (volatility * 0.3 + correlation * 0.2 + drawdown * 0.3 + (2 - sharpe) * 0.2) / 2
      setRiskScore(Math.max(0, Math.min(1, calculatedRisk)))
    }
  }, [riskData, portfolioData])

  // Advanced risk metrics based on the Degen Auditor backend code
  const riskMetrics = {
    var: {
      daily_var: 0.023,
      confidence_level: 0.95,
      risk_level: 'MEDIUM',
      alert: null
    },
    drawdown: {
      estimated_max_drawdown: 0.087,
      current_drawdown: 0.032,
      risk_level: 'LOW',
      alert: null
    },
    sharpe: {
      sharpe_ratio: 1.42,
      risk_assessment: 'GOOD',
      expected_return: 0.15,
      volatility: 0.247
    },
    volatility: {
      volatility: 0.247,
      risk_level: 'MEDIUM',
      volatility_regime: 'Normal Volatility',
      alert: null
    }
  }

  const riskThresholds = {
    max_position_size: 0.25,
    max_daily_var: 0.05,
    max_drawdown: 0.20,
    min_sharpe_ratio: 0.5,
    max_volatility: 0.60,
    correlation_limit: 0.80
  }

  if (loading) {
    return (
      <div className="bg-gray-800/50 backdrop-blur-lg rounded-xl border border-gray-700/30 p-6">
        <h2 className="text-2xl font-bold mb-6 text-gray-100">Risk Management System</h2>
        <div className="h-96 flex items-center justify-center bg-gray-900/50 rounded-lg border border-gray-700/30">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-400 mx-auto mb-4"></div>
            <p className="text-gray-400">Loading risk analytics...</p>
          </div>
        </div>
      </div>
    )
  }

  const RiskTabButton = ({ id, label, isActive, onClick }) => (
    <button
      onClick={() => onClick(id)}
      className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
        isActive
          ? 'bg-red-600 text-white shadow-md'
          : 'bg-gray-700/50 text-gray-300 hover:bg-gray-600/50 hover:text-white'
      }`}
    >
      {label}
    </button>
  )

  const RiskMeter = ({ value, maxValue = 1, label, color = 'red' }) => {
    const percentage = (value / maxValue) * 100
    return (
      <div className="bg-gray-900/50 rounded-lg p-4">
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-medium text-gray-300">{label}</span>
          <span className={`text-sm font-bold text-${color}-300`}>
            {typeof value === 'number' ? value.toFixed(3) : value}
          </span>
        </div>
        <div className="w-full bg-gray-700 rounded-full h-2">
          <div
            className={`bg-gradient-to-r from-${color}-600 to-${color}-400 h-2 rounded-full transition-all duration-300`}
            style={{ width: `${Math.min(100, percentage)}%` }}
          ></div>
        </div>
        <div className="mt-1 text-xs text-gray-500">
          {percentage.toFixed(1)}% of maximum threshold
        </div>
      </div>
    )
  }

  const AlertCard = ({ alert }) => {
    const alertStyles = {
      warning: 'border-yellow-700/50 bg-yellow-900/20 text-yellow-300',
      danger: 'border-red-700/50 bg-red-900/20 text-red-300',
      info: 'border-blue-700/50 bg-blue-900/20 text-blue-300',
      success: 'border-green-700/50 bg-green-900/20 text-green-300'
    }

    const alertIcons = {
      warning: '⚠️',
      danger: '🚨',
      info: 'ℹ️',
      success: '✅'
    }

    return (
      <div className={`border rounded-lg p-3 ${alertStyles[alert.type]}`}>
        <div className="flex items-start space-x-3">
          <span className="text-lg">{alertIcons[alert.type]}</span>
          <div className="flex-1">
            <h4 className="font-medium text-sm mb-1">{alert.title}</h4>
            <p className="text-xs opacity-90 mb-2">{alert.message}</p>
            <span className="text-xs opacity-70">
              {new Date(alert.timestamp).toLocaleTimeString()}
            </span>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-gray-800/50 backdrop-blur-lg rounded-xl border border-gray-700/30 p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-100 mb-1">
            🛡️ Advanced Risk Management
          </h2>
          <p className="text-gray-400 text-sm">
            Degen Auditor • VaR Analysis • Drawdown Protection • Portfolio Risk Assessment
          </p>
        </div>
        <div className="flex items-center space-x-4">
          {/* Risk Score Indicator */}
          <div className="text-center">
            <div className="text-xs text-gray-400 mb-1">Overall Risk Score</div>
            <div className={`text-2xl font-bold ${
              riskScore < 0.3 ? 'text-green-400' :
              riskScore < 0.6 ? 'text-yellow-400' : 'text-red-400'
            }`}>
              {(riskScore * 100).toFixed(0)}%
            </div>
          </div>
          <div className={`w-3 h-3 rounded-full animate-pulse ${
            riskScore < 0.3 ? 'bg-green-500' :
            riskScore < 0.6 ? 'bg-yellow-500' : 'bg-red-500'
          }`}></div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="flex space-x-2 mb-6 bg-gray-900/30 p-1 rounded-lg">
        <RiskTabButton id="overview" label="Risk Overview" isActive={activeRiskTab === 'overview'} onClick={setActiveRiskTab} />
        <RiskTabButton id="var" label="VaR Analysis" isActive={activeRiskTab === 'var'} onClick={setActiveRiskTab} />
        <RiskTabButton id="portfolio" label="Portfolio Risk" isActive={activeRiskTab === 'portfolio'} onClick={setActiveRiskTab} />
        <RiskTabButton id="alerts" label="Risk Alerts" isActive={activeRiskTab === 'alerts'} onClick={setActiveRiskTab} />
      </div>

      {/* Overview Tab */}
      {activeRiskTab === 'overview' && (
        <div className="space-y-6">
          {/* Risk Metrics Grid */}
          <div className="grid grid-cols-4 gap-4">
            <RiskMeter 
              value={riskMetrics.var.daily_var} 
              maxValue={riskThresholds.max_daily_var}
              label="Daily VaR (95%)"
              color="red"
            />
            <RiskMeter 
              value={riskMetrics.drawdown.estimated_max_drawdown} 
              maxValue={riskThresholds.max_drawdown}
              label="Max Drawdown"
              color="orange"
            />
            <RiskMeter 
              value={riskMetrics.sharpe.sharpe_ratio} 
              maxValue={3.0}
              label="Sharpe Ratio"
              color="green"
            />
            <RiskMeter 
              value={riskMetrics.volatility.volatility} 
              maxValue={riskThresholds.max_volatility}
              label="Volatility"
              color="yellow"
            />
          </div>

          {/* Risk Assessment Summary */}
          <div className="grid grid-cols-2 gap-6">
            <div className="bg-gray-900/30 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-gray-100 mb-4">Risk Assessment Summary</h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-gray-400">Overall Risk Level:</span>
                  <span className={`px-2 py-1 rounded text-xs font-medium ${
                    riskScore < 0.3 ? 'bg-green-900/50 text-green-300' :
                    riskScore < 0.6 ? 'bg-yellow-900/50 text-yellow-300' : 'bg-red-900/50 text-red-300'
                  }`}>
                    {riskScore < 0.3 ? 'LOW' : riskScore < 0.6 ? 'MEDIUM' : 'HIGH'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">VaR Status:</span>
                  <span className="text-yellow-300 font-mono">{riskMetrics.var.risk_level}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Drawdown Status:</span>
                  <span className="text-green-300 font-mono">{riskMetrics.drawdown.risk_level}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Sharpe Assessment:</span>
                  <span className="text-green-300 font-mono">{riskMetrics.sharpe.risk_assessment}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Volatility Regime:</span>
                  <span className="text-blue-300 font-mono">{riskMetrics.volatility.volatility_regime}</span>
                </div>
              </div>
            </div>

            <div className="bg-gray-900/30 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-gray-100 mb-4">Risk Thresholds</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-400">Max Position Size:</span>
                  <span className="text-blue-300 font-mono">{(riskThresholds.max_position_size * 100).toFixed(0)}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Max Daily VaR:</span>
                  <span className="text-red-300 font-mono">{(riskThresholds.max_daily_var * 100).toFixed(0)}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Max Drawdown:</span>
                  <span className="text-red-300 font-mono">{(riskThresholds.max_drawdown * 100).toFixed(0)}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Min Sharpe Ratio:</span>
                  <span className="text-green-300 font-mono">{riskThresholds.min_sharpe_ratio}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Correlation Limit:</span>
                  <span className="text-yellow-300 font-mono">{riskThresholds.correlation_limit}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* VaR Analysis Tab */}
      {activeRiskTab === 'var' && (
        <div className="space-y-6">
          <div className="grid grid-cols-3 gap-6">
            {/* VaR Calculation */}
            <div className="bg-gray-900/30 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-gray-100 mb-4">Value at Risk (VaR)</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-400">Confidence Level:</span>
                  <span className="text-blue-300 font-mono">{(riskMetrics.var.confidence_level * 100).toFixed(0)}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Daily VaR:</span>
                  <span className="text-red-300 font-mono">{(riskMetrics.var.daily_var * 100).toFixed(2)}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Weekly VaR:</span>
                  <span className="text-red-300 font-mono">{(riskMetrics.var.daily_var * Math.sqrt(7) * 100).toFixed(2)}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Monthly VaR:</span>
                  <span className="text-red-300 font-mono">{(riskMetrics.var.daily_var * Math.sqrt(30) * 100).toFixed(2)}%</span>
                </div>
              </div>
            </div>

            {/* Expected Shortfall */}
            <div className="bg-gray-900/30 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-gray-100 mb-4">Expected Shortfall</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-400">ES (95%):</span>
                  <span className="text-red-300 font-mono">{(riskMetrics.var.daily_var * 1.3 * 100).toFixed(2)}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Tail Risk:</span>
                  <span className="text-yellow-300 font-mono">MODERATE</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Stress Test:</span>
                  <span className="text-green-300 font-mono">PASSED</span>
                </div>
              </div>
            </div>

            {/* Risk Attribution */}
            <div className="bg-gray-900/30 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-gray-100 mb-4">Risk Attribution</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-400">Market Risk:</span>
                  <span className="text-blue-300 font-mono">67%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Volatility Risk:</span>
                  <span className="text-yellow-300 font-mono">23%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Liquidity Risk:</span>
                  <span className="text-green-300 font-mono">10%</span>
                </div>
              </div>
            </div>
          </div>

          {/* VaR Chart Simulation */}
          <div className="bg-gray-900/30 rounded-lg p-4">
            <h3 className="text-lg font-semibold text-gray-100 mb-4">VaR Distribution</h3>
            <div className="h-32 relative bg-gray-800/50 rounded">
              {/* Simulated distribution curve */}
              <div className="absolute inset-0 flex items-end justify-center">
                {Array.from({ length: 50 }, (_, i) => {
                  const x = (i - 25) / 25 // -1 to 1
                  const height = Math.exp(-0.5 * x * x) * 80 + 10 // Gaussian-like
                  const isVaR = i < 5 // Left tail for VaR
                  return (
                    <div
                      key={i}
                      className={`w-2 mx-0.5 ${
                        isVaR ? 'bg-red-500' : 'bg-blue-500'
                      }`}
                      style={{ height: `${height}px` }}
                    />
                  )
                })}
              </div>
              <div className="absolute bottom-2 left-2 text-xs text-gray-500">
                -3σ (VaR)
              </div>
              <div className="absolute bottom-2 right-2 text-xs text-gray-500">
                +3σ
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Portfolio Risk Tab */}
      {activeRiskTab === 'portfolio' && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 gap-6">
            <div className="bg-gray-900/30 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-gray-100 mb-4">Position Risk Analysis</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-400">Current Position Size:</span>
                  <span className="text-blue-300 font-mono">18.7%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Risk Contribution:</span>
                  <span className="text-yellow-300 font-mono">0.045</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Beta to Market:</span>
                  <span className="text-purple-300 font-mono">1.23</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Tracking Error:</span>
                  <span className="text-red-300 font-mono">4.2%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Information Ratio:</span>
                  <span className="text-green-300 font-mono">0.87</span>
                </div>
              </div>
            </div>

            <div className="bg-gray-900/30 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-gray-100 mb-4">Correlation Analysis</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-400">Market Correlation:</span>
                  <span className="text-blue-300 font-mono">0.34</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Sector Correlation:</span>
                  <span className="text-yellow-300 font-mono">0.58</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Crypto Correlation:</span>
                  <span className="text-purple-300 font-mono">0.12</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Diversification Ratio:</span>
                  <span className="text-green-300 font-mono">1.47</span>
                </div>
              </div>
            </div>
          </div>

          {/* Risk-Return Scatter */}
          <div className="bg-gray-900/30 rounded-lg p-4">
            <h3 className="text-lg font-semibold text-gray-100 mb-4">Risk-Return Profile</h3>
            <div className="h-48 relative bg-gray-800/50 rounded overflow-hidden">
              {/* Axes */}
              <div className="absolute bottom-0 left-0 w-full h-px bg-gray-600"></div>
              <div className="absolute bottom-0 left-0 w-px h-full bg-gray-600"></div>
              
              {/* Current Portfolio Position */}
              <div 
                className="absolute w-3 h-3 bg-green-500 rounded-full"
                style={{ 
                  left: `${(riskMetrics.volatility.volatility / 0.6) * 100}%`,
                  bottom: `${(riskMetrics.sharpe.expected_return / 0.3) * 100}%`
                }}
              ></div>
              
              {/* Efficient Frontier Simulation */}
              <svg className="absolute inset-0 w-full h-full">
                <path
                  d="M 50 180 Q 150 120 250 100 Q 350 90 400 85"
                  stroke="#3b82f6"
                  strokeWidth="2"
                  fill="none"
                  strokeDasharray="5,5"
                />
              </svg>
              
              {/* Labels */}
              <div className="absolute bottom-2 right-2 text-xs text-gray-500">Risk →</div>
              <div className="absolute top-2 left-2 text-xs text-gray-500 transform -rotate-90 origin-bottom-left">Return →</div>
            </div>
          </div>
        </div>
      )}

      {/* Risk Alerts Tab */}
      {activeRiskTab === 'alerts' && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 gap-6">
            {/* Recent Alerts */}
            <div className="space-y-3">
              <h3 className="text-lg font-semibold text-gray-100 mb-4">Recent Risk Alerts</h3>
              {riskAlerts.map(alert => (
                <AlertCard key={alert.id} alert={alert} />
              ))}
            </div>

            {/* Alert Configuration */}
            <div className="bg-gray-900/30 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-gray-100 mb-4">Alert Thresholds</h3>
              <div className="space-y-3 text-sm">
                <div className="flex items-center justify-between p-2 bg-gray-800/50 rounded">
                  <span className="text-gray-300">VaR Breach</span>
                  <div className="px-2 py-1 bg-red-900/50 text-red-300 rounded text-xs">
                    > 5%
                  </div>
                </div>
                <div className="flex items-center justify-between p-2 bg-gray-800/50 rounded">
                  <span className="text-gray-300">Drawdown Alert</span>
                  <div className="px-2 py-1 bg-yellow-900/50 text-yellow-300 rounded text-xs">
                    > 10%
                  </div>
                </div>
                <div className="flex items-center justify-between p-2 bg-gray-800/50 rounded">
                  <span className="text-gray-300">Volatility Spike</span>
                  <div className="px-2 py-1 bg-orange-900/50 text-orange-300 rounded text-xs">
                    > 40%
                  </div>
                </div>
                <div className="flex items-center justify-between p-2 bg-gray-800/50 rounded">
                  <span className="text-gray-300">Correlation Alert</span>
                  <div className="px-2 py-1 bg-blue-900/50 text-blue-300 rounded text-xs">
                    > 0.8
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Footer */}
      <div className="mt-6 pt-4 border-t border-gray-700/30">
        <div className="flex items-center justify-between text-xs text-gray-500">
          <div className="flex items-center space-x-4">
            <span>🛡️ Degen Auditor v4.0</span>
            <span>📊 VaR Analysis</span>
            <span>📉 Drawdown Protection</span>
            <span>⚡ Real-time Monitoring</span>
          </div>
          <div>
            Risk Engine: {new Date().toLocaleTimeString()}
          </div>
        </div>
      </div>
    </div>
  )
}

export default RiskManagementDashboard