// src/pages/YantraDashboard.jsx - Enhanced Trading Dashboard
import React, { useState, useEffect } from "react";
import {
  getGodCycle,
  getJournal,
  getCommentary,
  runRLCycle,
  getMarketPrice,
} from "../api/api";

const YantraDashboard = () => {
  // State management
  const [data, setData] = useState(null);
  const [journal, setJournal] = useState([]);
  const [commentary, setCommentary] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [livePrice, setLivePrice] = useState(null);
  const [systemStatus, setSystemStatus] = useState("idle");
  const [autoRefresh, setAutoRefresh] = useState(false);

  // Auto-refresh functionality
  useEffect(() => {
    const interval = autoRefresh ? setInterval(fetchAllData, 10000) : null;
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [autoRefresh]);

  // Initial data load
  useEffect(() => {
    fetchAllData();
  }, []);

  const fetchAllData = async () => {
    setLoading(true);
    setError("");
    
    try {
      const [journalData, commentaryData, priceData] = await Promise.all([
        getJournal().catch(() => []),
        getCommentary().catch(() => []),
        getMarketPrice("AAPL").catch(() => null),
      ]);

      setJournal(journalData);
      setCommentary(commentaryData);
      setLivePrice(
        priceData && priceData.price
          ? "$" + Number(priceData.price).toLocaleString()
          : "N/A"
      );
      setSystemStatus("ready");
    } catch (err) {
      console.error("Failed to fetch data:", err);
      setError("Failed to fetch data. Backend might be down.");
      setSystemStatus("error");
    } finally {
      setLoading(false);
    }
  };

  const handleRunCycle = async () => {
    try {
      setLoading(true);
      setSystemStatus("running");
      setError("");
      
      const res = await runRLCycle();
      setData(res);
      
      // Refresh data after successful cycle
      await fetchAllData();
      setSystemStatus("completed");
      
      // Auto-reset status after 3 seconds
      setTimeout(() => setSystemStatus("ready"), 3000);
    } catch (err) {
      console.error("❌ Run cycle failed:", err);
      setError("Run cycle failed. Backend might be down.");
      setSystemStatus("error");
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case "running": return "text-yellow-400";
      case "completed": return "text-green-400";
      case "error": return "text-red-400";
      case "ready": return "text-blue-400";
      default: return "text-gray-400";
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case "running": return "🔄";
      case "completed": return "✅";
      case "error": return "❌";
      case "ready": return "🚀";
      default: return "⚪";
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      {/* Header Section */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-blue-400 to-purple-600 bg-clip-text text-transparent">
          🧠 YantraX RL — AI Trading Intelligence
        </h1>
        <div className="flex items-center gap-4 text-lg">
          <span className={`flex items-center gap-2 ${getStatusColor(systemStatus)}`}>
            {getStatusIcon(systemStatus)} System Status: {systemStatus.toUpperCase()}
          </span>
          {livePrice && (
            <span className="text-green-400">💰 AAPL Live: {livePrice}</span>
          )}
        </div>
      </div>

      {/* Control Panel */}
      <div className="mb-8 flex gap-4 items-center">
        <button
          onClick={handleRunCycle}
          disabled={loading || systemStatus === "running"}
          className={`px-6 py-3 rounded-lg font-semibold transition-all ${
            loading || systemStatus === "running"
              ? "bg-gray-600 cursor-not-allowed"
              : "bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 active:scale-95"
          }`}
        >
          {loading ? "🔄 Processing..." : "🚀 Run RL God Cycle"}
        </button>
        
        <button
          onClick={() => setAutoRefresh(!autoRefresh)}
          className={`px-4 py-2 rounded transition-all ${
            autoRefresh
              ? "bg-green-600 hover:bg-green-700"
              : "bg-gray-600 hover:bg-gray-700"
          }`}
        >
          {autoRefresh ? "⏹️ Stop Auto-Refresh" : "🔄 Auto-Refresh (10s)"}
        </button>
        
        <button
          onClick={fetchAllData}
          disabled={loading}
          className="px-4 py-2 bg-gray-600 hover:bg-gray-700 rounded transition-all disabled:opacity-50"
        >
          🔃 Refresh Data
        </button>
      </div>

      {/* Error Display */}
      {error && (
        <div className="mb-6 p-4 bg-red-900/50 border border-red-500 rounded-lg">
          ❌ {error}
        </div>
      )}

      {/* RL Cycle Results */}
      {data && (
        <div className="mb-8 p-6 bg-gray-800 rounded-lg border border-gray-700">
          <h2 className="text-2xl font-bold mb-4 text-blue-400">📊 Latest RL Cycle Results</h2>
          
          {/* Metrics Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <MetricCard label="Final Balance" value={`$${data.final_balance?.toLocaleString()}`} />
            <MetricCard label="Total Reward" value={data.total_reward?.toFixed(3)} />
            <MetricCard label="Market Mood" value={data.final_mood} />
            <MetricCard label="Curiosity Level" value={data.curiosity?.toFixed(2)} />
          </div>

          {/* RL Steps Table */}
          {data.steps && data.steps.length > 0 && (
            <div className="overflow-x-auto">
              <h3 className="text-xl font-semibold mb-3 text-purple-400">🎯 RL Training Steps</h3>
              <table className="w-full border border-gray-600 rounded">
                <thead className="bg-gray-700">
                  <tr>
                    <th className="p-3 text-left">#</th>
                    <th className="p-3 text-left">Action</th>
                    <th className="p-3 text-left">Reward</th>
                    <th className="p-3 text-left">Price</th>
                    <th className="p-3 text-left">Position</th>
                    <th className="p-3 text-left">Mood</th>
                  </tr>
                </thead>
                <tbody>
                  {data.steps.map((step, index) => (
                    <tr key={index} className="border-t border-gray-600 hover:bg-gray-750">
                      <td className="p-3">{index + 1}</td>
                      <td className="p-3 font-mono">{step.action}</td>
                      <td className={`p-3 ${step.reward > 0 ? 'text-green-400' : step.reward < 0 ? 'text-red-400' : 'text-gray-400'}`}>
                        {step.reward.toFixed(3)}
                      </td>
                      <td className="p-3">${step.state?.price?.toLocaleString()}</td>
                      <td className="p-3">{step.state?.position || 'none'}</td>
                      <td className="p-3">{step.state?.mood}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Dashboard Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Journal Logs */}
        <div className="p-6 bg-gray-800 rounded-lg border border-gray-700">
          <h2 className="text-2xl font-bold mb-4 text-green-400">🧾 Trading Journal</h2>
          <div className="max-h-96 overflow-y-auto space-y-2">
            {Array.isArray(journal) && journal.length > 0 ? (
              journal.map((entry, index) => (
                <div key={index} className="p-3 bg-gray-900 rounded border border-gray-600">
                  {typeof entry === "object" ? (
                    <div>
                      <div className="text-sm text-gray-400 mb-1">{entry.timestamp}</div>
                      <div className="flex gap-4 text-sm">
                        <span className="text-blue-400">Signal: {entry.signal}</span>
                        <span className="text-purple-400">Audit: {entry.audit}</span>
                        <span className={entry.reward > 0 ? 'text-green-400' : 'text-red-400'}>
                          Reward: {entry.reward}
                        </span>
                      </div>
                    </div>
                  ) : (
                    <div className="text-sm">{entry}</div>
                  )}
                </div>
              ))
            ) : (
              <div className="text-gray-400 italic">No journal entries found.</div>
            )}
          </div>
        </div>

        {/* Agent Commentary */}
        <div className="p-6 bg-gray-800 rounded-lg border border-gray-700">
          <h2 className="text-2xl font-bold mb-4 text-orange-400">🧠 Agent Commentary</h2>
          <div className="max-h-96 overflow-y-auto space-y-2">
            {Array.isArray(commentary) && commentary.length > 0 ? (
              commentary.map((entry, idx) =>
                typeof entry === "object" ? (
                  <div key={idx} className="p-3 bg-gray-900 rounded border border-gray-600">
                    <div className="flex justify-between items-start mb-2">
                      <span className="font-semibold text-blue-400">{entry.agent}:</span>
                      <span className="text-xs text-gray-400">{entry.timestamp}</span>
                    </div>
                    <div className="text-sm">{entry.comment}</div>
                  </div>
                ) : (
                  <div key={idx} className="p-3 bg-gray-900 rounded border border-gray-600 text-sm">
                    {entry}
                  </div>
                )
              )
            ) : (
              <div className="text-gray-400 italic">No agent commentary available.</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

// Reusable MetricCard component
const MetricCard = ({ label, value }) => (
  <div className="p-4 bg-gray-900 rounded border border-gray-600">
    <div className="text-sm text-gray-400 mb-1">{label}</div>
    <div className="text-xl font-bold text-white">{value || 'N/A'}</div>
  </div>
);

export default YantraDashboard;
