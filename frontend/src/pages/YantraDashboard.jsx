<<<<<<< HEAD
// src/pages/YantraDashboard.jsx
// 🔁 Force Vercel redeploy
// 🔁 Trigger rebuild for case-sensitive JournalCard fix

// 🚀 Trigger build
// src/pages/YantraDashboard.jsx
import React, { useState, useEffect } from "react";
import MarketStats from "../components/MarketStats";
import JournalCard from "../components/JournalCard";
import AgentCommentary from "../components/AgentCommentary";

const BASE_URL = "https://yantrax-backend.onrender.com";

const YantraDashboard = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [journal, setJournal] = useState([]);
  const [commentary, setCommentary] = useState([]);

  const runGodCycle = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${BASE_URL}/god-cycle`);
      if (!res.ok) throw new Error("Backend error");
      const result = await res.json();
      setData(result);
      await fetchJournal();
      await fetchCommentary();
    } catch (error) {
      console.error("❌ Error running god cycle:", error);
      setError("Backend might be unreachable or returned bad data.");
    } finally {
=======
import React, { useState, useEffect } from "react";
import {
  getGodCycle,
  getJournal,
  getCommentary,
  runRLCycle,
  getMarketPrice,
} from "../api/api";

const YantraDashboard = () => {
  const [data, setData] = useState(null);
  const [journal, setJournal] = useState([]);
  const [commentary, setCommentary] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [livePrice, setLivePrice] = useState(null);

  // 🚀 THIS BUTTON NOW USES POST /run-cycle instead of GET /god-cycle!
  const handleRunCycle = async () => {
    try {
      setLoading(true);
      const res = await runRLCycle();
      setData(res);
      setLoading(false);
    } catch (err) {
      console.error("❌ Run cycle failed:", err);
      setError("Run cycle failed. Backend might be down.");
>>>>>>> a77fc5118146028486e59aa4c855b92fa20c9563
      setLoading(false);
    }
  };

<<<<<<< HEAD
  const fetchJournal = async () => {
    try {
      const res = await fetch(`${BASE_URL}/journal`);
      const result = await res.json();
      setJournal(result);
    } catch (err) {
      console.error("Failed to fetch journal:", err);
    }
  };

  const fetchCommentary = async () => {
    try {
      const res = await fetch(`${BASE_URL}/commentary`);
      const result = await res.json();
      setCommentary(result);
    } catch (err) {
      console.error("Failed to fetch commentary:", err);
    }
  };

  useEffect(() => {
    fetchJournal();
    fetchCommentary();
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 to-black text-white p-6">
      <h1 className="text-4xl font-extrabold mb-6 text-center">🧠 Yantra X — RL God Mode</h1>

      <div className="flex justify-center mb-6">
        <button
          onClick={runGodCycle}
          className={`px-6 py-3 text-lg rounded-xl font-semibold shadow-xl transition-all ${
            loading ? "bg-gray-700 cursor-not-allowed" : "bg-indigo-600 hover:bg-indigo-700"
          }`}
          disabled={loading}
        >
          {loading ? "⏳ Running..." : "🚀 Run RL Cycle"}
        </button>
      </div>

      {error && <p className="text-center text-red-500 text-lg mb-4">❌ {error}</p>}

      {data && (
        <div className="mb-6">
          <MarketStats data={data} />
        </div>
      )}

      <AgentCommentary commentary={commentary} />

      <h2 className="text-2xl font-bold my-8 text-indigo-400">📜 Cycle History</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {journal.map((entry, i) => (
          <JournalCard key={i} {...entry} />
        ))}
      </div>
=======
  useEffect(() => {
    setLoading(true);
    Promise.all([
      getJournal(),
      getCommentary(),
      getMarketPrice("AAPL"),
    ])
      .then(([journalData, commentaryData, priceData]) => {
        setJournal(journalData);
        setCommentary(commentaryData);
        setLivePrice(
          priceData && priceData.price
            ? "$" + Number(priceData.price).toLocaleString()
            : "N/A"
        );
        setLoading(false);
        setError("");
      })
      .catch((err) => {
        setError("Failed to fetch data. Backend might be down.");
        setLoading(false);
      });
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-950 via-indigo-900/90 to-black text-white p-6 space-y-8">
      <header className="text-center">
        <h1 className="text-4xl font-bold mb-2">🧠 Yantra X — RL God Mode</h1>
        <button
          onClick={handleRunCycle}
          disabled={loading}
          className="bg-emerald-600 hover:bg-emerald-700 text-white px-5 py-2 rounded shadow mt-4"
        >
          🚀 {loading ? "Running..." : "Run RL Cycle"}
        </button>
        {error && <p className="text-red-400 mt-2">{error}</p>}
      </header>

      {livePrice && (
        <div className="text-2xl my-4 text-emerald-300 font-bold shadow rounded bg-indigo-950/80 w-fit px-6 py-2 mx-auto">
          💰 AAPL Live Price: {livePrice}
        </div>
      )}

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
                  {data.steps &&
                    data.steps.map((step, index) => (
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
          {Array.isArray(journal) && journal.length > 0
            ? journal.map((entry, index) => (
                <li key={index} className="bg-gray-800 p-3 rounded">
                  {typeof entry === "object"
                    ? `${entry.timestamp} | ${entry.signal} | ${entry.audit} | Reward: ${entry.reward}`
                    : entry}
                </li>
              ))
            : <li className="text-gray-400">No journal entries found.</li>}
        </ul>
      </section>

      {/* Agent Commentary */}
      <section className="bg-gray-900 p-4 rounded-xl shadow">
        <h2 className="text-xl font-semibold mb-2">🧠 Agent Commentary</h2>
        <div className="text-sm text-gray-300 whitespace-pre-wrap">
          {Array.isArray(commentary)
            ? commentary.map((entry, idx) =>
                typeof entry === "object"
                  ? (
                    <div key={idx}>
                      <span className="font-bold text-indigo-300">{entry.agent}:</span> {entry.comment}
                      <span className="block text-xs text-gray-500 ml-2">{entry.timestamp}</span>
                    </div>
                    )
                  : <div key={idx}>{entry}</div>
              )
            : commentary}
        </div>
      </section>
>>>>>>> a77fc5118146028486e59aa4c855b92fa20c9563
    </div>
  );
};

<<<<<<< HEAD
=======
const Card = ({ label, value }) => (
  <div className="bg-gray-900 p-4 rounded-xl shadow">
    <h3 className="text-gray-400 text-sm">{label}</h3>
    <p className="text-xl font-semibold text-emerald-400">{value}</p>
  </div>
);

>>>>>>> a77fc5118146028486e59aa4c855b92fa20c9563
export default YantraDashboard;
