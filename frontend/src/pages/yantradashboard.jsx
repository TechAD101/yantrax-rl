// src/pages/YantraDashboard.jsx
import React, { useState, useEffect } from "react";
import MarketStats from "../components/MarketStats";
import JournalCard from "../components/JournalCard";

const YantraDashboard = () => {
  const [stats, setStats] = useState(null);
  const [journal, setJournal] = useState([]);
  const [commentary, setCommentary] = useState("");

  useEffect(() => {
    fetch("https://yantrax-backend.onrender.com/god-cycle")
      .then((res) => res.json())
      .then((data) => setStats(data));

    fetch("https://yantrax-backend.onrender.com/journal")
      .then((res) => res.json())
      .then((data) => setJournal(data));

    fetch("https://yantrax-backend.onrender.com/commentary")
      .then((res) => res.text())
      .then((data) => setCommentary(data));
  }, []);

  return (
    <div className="p-6 space-y-6 bg-gray-950 text-white min-h-screen">
      <h1 className="text-3xl font-bold">🧠 Yantra X — RL God Mode</h1>
      <button
        onClick={() => {
          fetch("https://yantrax-backend.onrender.com/god-cycle")
            .then((res) => res.json())
            .then((data) => setStats(data));
        }}
        className="bg-blue-600 hover:bg-blue-800 text-white px-4 py-2 rounded-xl shadow"
      >
        🚀 Run RL Cycle
      </button>

      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {Object.entries(stats).map(([key, value]) => (
            <div
              key={key}
              className="bg-gray-900 p-4 rounded-xl border border-gray-700 shadow-lg"
            >
              <p className="text-sm text-gray-400">{key}</p>
              <p className="text-xl font-bold">{value}</p>
            </div>
          ))}
        </div>
      )}

      <div>
        <h2 className="text-2xl font-semibold mb-2">🧾 Journal Logs</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {journal.map((entry, index) => (
            <JournalCard key={index} {...entry} />
          ))}
        </div>
      </div>

      <div>
        <h2 className="text-2xl font-semibold mt-4">🧠 Agent Commentary</h2>
        <pre className="bg-gray-900 p-4 rounded-xl border border-gray-700 whitespace-pre-wrap">
          {commentary}
        </pre>
      </div>
    </div>
  );
};

export default YantraDashboard;
