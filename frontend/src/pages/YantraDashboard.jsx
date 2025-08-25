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
      setLoading(false);
    }
  };

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
    </div>
  );
};

export default YantraDashboard;
