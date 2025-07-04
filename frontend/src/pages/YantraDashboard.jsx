// src/pages/YantraDashboard.jsx
import React, { useState, useEffect } from "react";
import MarketStats from "../components/MarketStats";
import JournalCard from "../components/JournalCard";

const BASE_URL = import.meta.env.VITE_API_URL;

const YantraDashboard = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [journal, setJournal] = useState([]);

  const runCycle = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${BASE_URL}/run-cycle`, {
        method: "POST",
      });
      const result = await res.json();
      setData(result);
    } catch (error) {
      console.error("Error running cycle:", error);
      alert("❌ Error running cycle");
    }
    setLoading(false);
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

  useEffect(() => {
    fetchJournal();
  }, [data]);

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 to-black text-white p-6">
      <h1 className="text-4xl font-extrabold mb-6 text-center">🧠 Yantra X God Mode</h1>
      <div className="flex justify-center">
        <button
          onClick={runCycle}
          className="bg-indigo-600 hover:bg-indigo-700 px-6 py-3 text-lg rounded-xl shadow-xl"
          disabled={loading}
        >
          {loading ? "⏳ Running..." : "🚀 Run RL Cycle"}
        </button>
      </div>

      {data && <MarketStats data={data} />}

      <div className="mt-10 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {journal.map((entry, i) => (
          <JournalCard key={i} {...entry} />
        ))}
      </div>
    </div>
  );
};

export default YantraDashboard;
