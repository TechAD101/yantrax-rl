// src/pages/YantraDashboard.jsx
import React, { useState, useEffect } from "react";

const YantraDashboard = () => {
  const [data, setData] = useState(null);
  const [journal, setJournal] = useState([]);
  const [commentary, setCommentary] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const runCycle = async () => {
    try {
      setLoading(true);
      const res = await fetch("https://yantrax-backend.onrender.com/god-cycle");
      const json = await res.json();
      setData(json);
      setLoading(false);
    } catch (err) {
      console.error("❌ Run cycle failed:", err);
      setError("Run cycle failed. Backend might be down.");
      setLoading(false);
    }
  };

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const [journalRes, commentaryRes] = await Promise.all([
          fetch("https://yantrax-backend.onrender.com/journal"),
          fetch("https://yantrax-backend.onrender.com/commentary"),
        ]);
        const journalData = await journalRes.json();
        const commentaryData = await commentaryRes.text();
        setJournal(journalData);
        setCommentary(commentaryData);
      } catch (err) {
        console.error("❌ Error loading logs:", err);
      }
    };
    fetchLogs();
  }, []);

  return (
    <div className="min-h-screen bg-gray-950 text-white p-6 space-y-8">
      <header className="text-center">
        <h1 className="text-4xl font-bold mb-2">🧠 Yantra X — RL God Mode</h1>
        <button
          onClick={runCycle}
          disabled={loading}
          className="bg-emerald-600 hover:bg-emerald-700 text-white px-5 py-2 rounded shadow mt-4"
        >
          🚀 {loading ? "Running..." : "Run RL Cycle"}
        </button>
        {error && <p className="text-red-400 mt-2">{error}</p>}
      </header>

      {data && (
        <>
          {/* Metrics */}
          <section className="grid grid-cols-2 md:grid-cols-3 gap-4">
            <Card label="Curiosity" value={data.curiosity} />
            <Card label="Final Balance" value={data.final_balance} />
            <Card label="Cycle" value={data.final_cycle} />
            <Card label="Mood" value={data.final_mood} />
            <Card label="Total Reward" value={data.total_reward} />
          </section>

          {/* RL Steps Table */}
          <section className="bg-gray-900 p-4 rounded-xl shadow mt-4">
            <h2 className="text-xl font-semibold mb-2">📊 RL Steps</h2>
            <div className="overflow-auto max-h-[300px]">
              <table className="w-full text-sm">
                <thead className="bg-gray-800">
                  <tr>
                    <th className="p-2 text-left">#</th>
                    <th className="p-2 text-left">Action</th>
                    <th className="p-2 text-left">Reward</th>
                    <th className="p-2 text-left">State Summary</th>
                  </tr>
                </thead>
                <tbody>
                  {data.steps.map((step, index) => (
                    <tr key={index} className="border-b border-gray-700">
                      <td className="p-2">{index + 1}</td>
                      <td className="p-2">{step.action}</td>
                      <td className="p-2">{step.reward.toFixed(3)}</td>
                      <td className="p-2 text-xs text-gray-300">
                        Position: {step.state.position}, Price: {step.state.price}, Volatility: {step.state.volatility}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        </>
      )}

      {/* Journal Logs */}
      <section className="bg-gray-900 p-4 rounded-xl shadow">
        <h2 className="text-xl font-semibold mb-2">🧾 Journal Logs</h2>
        <ul className="space-y-2 max-h-[200px] overflow-y-auto">
          {journal.map((entry, index) => (
            <li key={index} className="bg-gray-800 p-3 rounded">
              {entry}
            </li>
          ))}
        </ul>
      </section>

      {/* Agent Commentary */}
      <section className="bg-gray-900 p-4 rounded-xl shadow">
        <h2 className="text-xl font-semibold mb-2">🧠 Agent Commentary</h2>
        <div className="text-sm text-gray-300 whitespace-pre-wrap">{commentary}</div>
      </section>
    </div>
  );
};

const Card = ({ label, value }) => (
  <div className="bg-gray-900 p-4 rounded-xl shadow">
    <h3 className="text-gray-400 text-sm">{label}</h3>
    <p className="text-xl font-semibold text-emerald-400">{value}</p>
  </div>
);

export default YantraDashboard;
