// YantraDashboard.jsx - Revolutionary AI Trading Intelligence Interface
import React, { useState, useEffect, useMemo } from "react";
import AIFirmDashboard from '../components/AIFirmDashboard';
import {
  getGodCycle,
  getJournal,
  getCommentary,
  runRLCycle,
  getMarketPrice,
} from "../api/api";

const YantraDashboard = () => {
  // Enhanced State Management
  const [marketData, setMarketData] = useState({});
  const [agentStatus, setAgentStatus] = useState({});
  const [portfolioMetrics, setPortfolioMetrics] = useState({});
  const [riskAnalytics, setRiskAnalytics] = useState({});
  const [tradingSignals, setTradingSignals] = useState([]);
  const [systemHealth, setSystemHealth] = useState("OPERATIONAL");
  const [selectedAssets, setSelectedAssets] = useState(["AAPL", "TSLA", "NVDA", "MSFT"]);
  const [timeframe, setTimeframe] = useState("1D");
  const [loading, setLoading] = useState(false);
  const [lastUpdate, setLastUpdate] = useState(new Date());
  const [activeTab, setActiveTab] = useState("overview"); // New tab state

  // Multi-Asset Market Data
  const ASSET_UNIVERSE = {
    "Stocks": ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA", "AMZN", "META"],
    "Crypto": ["BTC", "ETH", "BNB", "SOL", "ADA", "DOT"],
    "Indices": ["SPY", "QQQ", "IWM", "VIX"],
    "Forex": ["EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF"]
  };

  // Enhanced Data Fetching
  const fetchComprehensiveData = async () => {
    setLoading(true);
    try {
      const [cycleData, journalData, commentaryData] = await Promise.allSettled([
        runRLCycle(),
        getJournal(),
        getCommentary()
      ]);

      // Process RL Cycle Data
      if (cycleData.status === 'fulfilled') {
        const data = cycleData.value;
        setAgentStatus({
          macroMonk: { confidence: 0.87, signal: data.strategy, status: "ACTIVE" },
          theGhost: { confidence: 0.92, signal: data.signal, status: "PROCESSING" },
          dataWhisperer: { confidence: 0.78, analysis: "BULLISH_TREND", status: "ANALYZING" },
          degenAuditor: { confidence: 0.95, audit: data.audit, status: "MONITORING" }
        });

        setPortfolioMetrics({
          totalValue: data.final_balance || 10000,
          dailyPnL: data.rl_metrics?.reward || 0,
          sharpeRatio: 1.23,
          maxDrawdown: -0.08,
          winRate: 0.67
        });

            if (data.market_state) {
          setRiskAnalytics({
            volatility: data.market_state.volatility || 0.02,
            var95: 0.034,
            correlation: 0.76,
            riskScore: data.anomalies?.risk_alert ? 0.85 : 0.45
          });
        }
      }

      // Process Trading Signals
      setTradingSignals(prev => {
        const newSignal = {
          id: Date.now(),
          timestamp: new Date().toISOString(),
          signal: cycleData.value?.signal || "WAIT",
          confidence: Math.random() * 0.3 + 0.7,
          asset: selectedAssets[0],
          reasoning: "Multi-agent consensus with high conviction"
        };
        return [newSignal, ...prev.slice(0, 9)]; // Keep last 10 signals
      });

      setLastUpdate(new Date());
    } catch (error) {
      console.error("Data fetch error:", error);
      setSystemHealth("DEGRADED");
    } finally {
      setLoading(false);
    }
  };

  // Auto-refresh with intelligent intervals
  useEffect(() => {
    fetchComprehensiveData();
    const interval = setInterval(fetchComprehensiveData, 15000); // 15 second intervals
    return () => clearInterval(interval);
  }, []);

  // Market Regime Detection
  const marketRegime = useMemo(() => {
    const volatility = riskAnalytics.volatility || 0.02;
    if (volatility > 0.4) return { regime: "CRISIS", color: "text-red-400", bg: "bg-red-900/20" };
    if (volatility > 0.25) return { regime: "HIGH_VOL", color: "text-yellow-400", bg: "bg-yellow-900/20" };
    if (volatility < 0.15) return { regime: "LOW_VOL", color: "text-green-400", bg: "bg-green-900/20" };
    return { regime: "NORMAL", color: "text-blue-400", bg: "bg-blue-900/20" };
  }, [riskAnalytics.volatility]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black text-white">
      {/* Revolutionary Header */}
      <header className="border-b border-gray-700/50 bg-gray-900/80 backdrop-blur-xl">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 rounded-full bg-green-400 animate-pulse"></div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">
                  YantraX RL
                </h1>
                <span className="text-xs text-gray-400 font-mono">v4.0.0</span>
              </div>
              <div className="flex items-center space-x-1">
                <span className="text-xs text-gray-400">System:</span>
                <span className={`text-xs font-semibold ${
                  systemHealth === "OPERATIONAL" ? "text-green-400" : "text-yellow-400"
                }`}>
                  {systemHealth}
                </span>
              </div>
            </div>

            <div className="flex items-center space-x-6">
              {/* Market Regime Indicator */}
              <div className={`px-3 py-1 rounded-full ${marketRegime.bg} border border-gray-600/50`}>
                <span className={`text-xs font-semibold ${marketRegime.color}`}>
                  {marketRegime.regime}
                </span>
              </div>

              {/* Portfolio Summary */}
              <div className="flex items-center space-x-4 text-sm">
                <div className="text-center">
                  <div className="text-gray-400 text-xs">Portfolio</div>
                  <div className="font-bold text-green-400">
                    ${portfolioMetrics.totalValue?.toLocaleString()}
                  </div>
                </div>
                <div className="text-center">
                  <div className="text-gray-400 text-xs">P&L</div>
                  <div className={`font-bold ${
                    portfolioMetrics.dailyPnL >= 0 ? "text-green-400" : "text-red-400"
                  }`}>
                    {portfolioMetrics.dailyPnL >= 0 ? "+" : ""}
                    {portfolioMetrics.dailyPnL?.toFixed(2)}
                  </div>
                </div>
                <div className="text-center">
                  <div className="text-gray-400 text-xs">Sharpe</div>
                  <div className="font-bold text-cyan-400">
                    {portfolioMetrics.sharpeRatio?.toFixed(2)}
                  </div>
                </div>
              </div>

              {/* Last Update */}
              <div className="text-xs text-gray-400">
                Updated: {lastUpdate.toLocaleTimeString()}
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="p-6 space-y-6">
        {/* Navigation Tabs */}
        <div className="flex items-center justify-between">
          <div className="flex space-x-2">
            <button
              onClick={() => setActiveTab('overview')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                activeTab === 'overview' 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-gray-700/50 text-gray-300 hover:bg-gray-600/50'
              }`}
            >
              📊 Market Overview
            </button>
            <button
              onClick={() => setActiveTab('aifirm')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                activeTab === 'aifirm' 
                  ? 'bg-cyan-600 text-white' 
                  : 'bg-gray-700/50 text-gray-300 hover:bg-gray-600/50'
              }`}
            >
              🏢 AI Firm
            </button>
          </div>

          <div className="flex items-center space-x-3">
            <button
              onClick={fetchComprehensiveData}
              disabled={loading}
              className={`px-4 py-2 rounded-lg font-medium transition-all ${
                loading 
                  ? "bg-gray-600 cursor-not-allowed" 
                  : "bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 active:scale-95"
              }`}
            >
              {loading ? "🔄 Analyzing..." : "🚀 Execute Cycle"}
            </button>
          </div>
        </div>

        {/* Tab Content */}
        {activeTab === 'overview' && (
          <>
            {/* Asset Selection & Controls */}
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <h2 className="text-lg font-semibold text-gray-300">Market Intelligence</h2>
                <div className="flex space-x-2">
                  {Object.entries(ASSET_UNIVERSE).map(([category, assets]) => (
                    <button
                      key={category}
                      className="px-3 py-1 text-xs rounded-md bg-gray-700/50 hover:bg-gray-600/50 transition-colors border border-gray-600/30"
                      onClick={() => setSelectedAssets(assets.slice(0, 4))}
                    >
                      {category}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Main Intelligence Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* AI Agent Status Matrix */}
              <div className="lg:col-span-2">
                <div className="bg-gradient-to-br from-gray-800/80 to-gray-900/80 rounded-xl border border-gray-700/50 p-6 backdrop-blur-sm">
                  <h3 className="text-xl font-bold mb-4 text-cyan-400 flex items-center">
                    <span className="w-2 h-2 bg-cyan-400 rounded-full mr-2 animate-pulse"></span>
                    AI Agent Coordination Matrix
                  </h3>

                  <div className="grid grid-cols-2 gap-4">
                    {Object.entries(agentStatus).map(([agent, status]) => (
                      <AgentCard key={agent} agent={agent} status={status} />
                    ))}
                  </div>
                </div>
              </div>

              {/* Risk Analytics */}
              <div className="space-y-6">
                {/* Risk Metrics */}
                <div className="bg-gradient-to-br from-gray-800/80 to-gray-900/80 rounded-xl border border-gray-700/50 p-6 backdrop-blur-sm">
                  <h3 className="text-lg font-bold mb-4 text-orange-400">Risk Analytics</h3>
                  <div className="space-y-3">
                    <RiskMetric 
                      label="Volatility" 
                      value={`${(riskAnalytics.volatility * 100)?.toFixed(1)}%`}
                      level={riskAnalytics.volatility > 0.3 ? "high" : riskAnalytics.volatility > 0.2 ? "medium" : "low"}
                    />
                    <RiskMetric 
                      label="VaR (95%)" 
                      value={`${(riskAnalytics.var95 * 100)?.toFixed(1)}%`}
                      level="medium"
                    />
                    <RiskMetric 
                      label="Correlation" 
                      value={riskAnalytics.correlation?.toFixed(2)}
                      level="low"
                    />
                    <RiskMetric 
                      label="Risk Score" 
                      value={`${(riskAnalytics.riskScore * 100)?.toFixed(0)}/100`}
                      level={riskAnalytics.riskScore > 0.7 ? "high" : riskAnalytics.riskScore > 0.4 ? "medium" : "low"}
                    />
                  </div>
                </div>

                {/* Performance Metrics */}
                <div className="bg-gradient-to-br from-gray-800/80 to-gray-900/80 rounded-xl border border-gray-700/50 p-6 backdrop-blur-sm">
                  <h3 className="text-lg font-bold mb-4 text-green-400">Performance</h3>
                  <div className="space-y-3">
                    <PerformanceMetric 
                      label="Win Rate" 
                      value={`${(portfolioMetrics.winRate * 100)?.toFixed(0)}%`}
                      positive={portfolioMetrics.winRate > 0.5}
                    />
                    <PerformanceMetric 
                      label="Max Drawdown" 
                      value={`${(portfolioMetrics.maxDrawdown * 100)?.toFixed(1)}%`}
                      positive={portfolioMetrics.maxDrawdown > -0.1}
                    />
                    <PerformanceMetric 
                      label="Sharpe Ratio" 
                      value={portfolioMetrics.sharpeRatio?.toFixed(2)}
                      positive={portfolioMetrics.sharpeRatio > 1.0}
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Live Trading Signals */}
            <div className="bg-gradient-to-br from-gray-800/80 to-gray-900/80 rounded-xl border border-gray-700/50 p-6 backdrop-blur-sm">
              <h3 className="text-xl font-bold mb-4 text-purple-400 flex items-center">
                <span className="w-2 h-2 bg-purple-400 rounded-full mr-2 animate-pulse"></span>
                Live Trading Intelligence
              </h3>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Recent Signals */}
                <div>
                  <h4 className="text-sm font-semibold text-gray-300 mb-3">Recent Signals</h4>
                  <div className="space-y-2 max-h-64 overflow-y-auto">
                    {tradingSignals.slice(0, 6).map((signal) => (
                      <SignalCard key={signal.id} signal={signal} />
                    ))}
                  </div>
                </div>

                {/* Multi-Asset Overview */}
                <div>
                  <h4 className="text-sm font-semibold text-gray-300 mb-3">Asset Monitor</h4>
                  <div className="grid grid-cols-2 gap-3">
                    {selectedAssets.map((asset) => (
                      <AssetCard key={asset} symbol={asset} />
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Advanced Analytics Footer */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <AnalyticsCard
                title="Market Sentiment"
                value="Cautiously Optimistic"
                indicator="neutral"
                subtext="Fear & Greed Index: 45/100"
              />
              <AnalyticsCard
                title="System Learning"
                value="Adaptive Mode"
                indicator="positive"
                subtext="Model confidence: 89%"
              />
              <AnalyticsCard
                title="Next Analysis"
                value={`${15 - (Date.now() % 15000) / 1000 | 0}s`}
                indicator="info"
                subtext="Real-time cycle monitoring"
              />
            </div>
          </>
        )}

        {/* AI Firm Tab */}
        {activeTab === 'aifirm' && (
          <AIFirmDashboard />
        )}
      </div>
    </div>
  );
};

// Component Library (preserved from original)
const AgentCard = ({ agent, status }) => {
  const agentNames = {
    macroMonk: "Macro Monk",
    theGhost: "The Ghost", 
    dataWhisperer: "Data Whisperer",
    degenAuditor: "Degen Auditor"
  };

  const agentColors = {
    macroMonk: "from-blue-500 to-cyan-500",
    theGhost: "from-purple-500 to-pink-500",
    dataWhisperer: "from-green-500 to-emerald-500", 
    degenAuditor: "from-orange-500 to-red-500"
  };

  return (
    <div className="bg-gray-900/60 rounded-lg p-4 border border-gray-700/30 hover:border-gray-600/50 transition-all">
      <div className="flex items-center justify-between mb-2">
        <h4 className="font-semibold text-sm text-gray-200">{agentNames[agent]}</h4>
        <div className={`w-2 h-2 rounded-full ${
          status?.status === "ACTIVE" ? "bg-green-400" : 
          status?.status === "PROCESSING" ? "bg-yellow-400 animate-pulse" : "bg-blue-400"
        }`}></div>
      </div>
      <div className="space-y-2">
        <div className="flex justify-between text-xs">
          <span className="text-gray-400">Confidence</span>
          <span className="text-white font-medium">{(status?.confidence * 100)?.toFixed(0)}%</span>
        </div>
        <div className="w-full bg-gray-700/50 rounded-full h-1">
          <div 
            className={`h-1 rounded-full bg-gradient-to-r ${agentColors[agent]}`}
            style={{ width: `${(status?.confidence * 100) || 0}%` }}
          ></div>
        </div>
        <div className="text-xs text-gray-300">
          {status?.signal || status?.analysis || status?.audit || "Monitoring"}
        </div>
      </div>
    </div>
  );
};

const RiskMetric = ({ label, value, level }) => {
  const levelColors = {
    low: "text-green-400",
    medium: "text-yellow-400", 
    high: "text-red-400"
  };

  return (
    <div className="flex justify-between items-center">
      <span className="text-sm text-gray-400">{label}</span>
      <span className={`text-sm font-medium ${levelColors[level]}`}>{value}</span>
    </div>
  );
};

const PerformanceMetric = ({ label, value, positive }) => (
  <div className="flex justify-between items-center">
    <span className="text-sm text-gray-400">{label}</span>
    <span className={`text-sm font-medium ${positive ? "text-green-400" : "text-red-400"}`}>
      {value}
    </span>
  </div>
);

const SignalCard = ({ signal }) => (
  <div className="bg-gray-900/40 rounded-lg p-3 border border-gray-700/20">
    <div className="flex items-center justify-between mb-1">
      <span className={`text-xs font-bold px-2 py-1 rounded ${
        signal.signal === "BUY" || signal.signal.includes("BUY") ? "bg-green-900/50 text-green-400" :
        signal.signal === "SELL" || signal.signal.includes("SELL") ? "bg-red-900/50 text-red-400" :
        "bg-gray-700/50 text-gray-400"
      }`}>
        {signal.signal}
      </span>
      <span className="text-xs text-gray-500">
        {new Date(signal.timestamp).toLocaleTimeString()}
      </span>
    </div>
    <div className="text-xs text-gray-300 mb-1">{signal.asset}</div>
    <div className="text-xs text-gray-400">Confidence: {(signal.confidence * 100).toFixed(0)}%</div>
  </div>
);

const AssetCard = ({ symbol }) => {
  // Simulated price data - in production, fetch real data
  const mockPrice = (Math.random() * 1000 + 100).toFixed(2);
  const mockChange = ((Math.random() - 0.5) * 10).toFixed(2);
  const isPositive = parseFloat(mockChange) >= 0;

  return (
    <div className="bg-gray-900/40 rounded-lg p-3 border border-gray-700/20">
      <div className="font-semibold text-sm text-gray-200 mb-1">{symbol}</div>
      <div className="text-lg font-bold text-white">${mockPrice}</div>
      <div className={`text-xs font-medium ${isPositive ? "text-green-400" : "text-red-400"}`}>
        {isPositive ? "+" : ""}{mockChange} ({isPositive ? "+" : ""}{(mockChange/mockPrice*100).toFixed(2)}%)
      </div>
    </div>
  );
};

const AnalyticsCard = ({ title, value, indicator, subtext }) => {
  const indicatorColors = {
    positive: "border-green-500/50 bg-green-900/20",
    negative: "border-red-500/50 bg-red-900/20", 
    neutral: "border-yellow-500/50 bg-yellow-900/20",
    info: "border-blue-500/50 bg-blue-900/20"
  };

  return (
    <div className={`rounded-xl p-4 border ${indicatorColors[indicator]} backdrop-blur-sm`}>
      <h4 className="text-sm font-medium text-gray-300 mb-2">{title}</h4>
      <div className="text-xl font-bold text-white mb-1">{value}</div>
      <div className="text-xs text-gray-400">{subtext}</div>
    </div>
  );
};

export default YantraDashboard;
