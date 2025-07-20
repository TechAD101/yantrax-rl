// src/pages/YantraDashboard.jsx
import React, { useEffect, useState } from "react";
import JournalCard from "../components/JournalCard";
import CommentaryCard from "../components/CommentaryCard"; // If you plan to use cards instead of raw <pre>

const YantraDashboard = () => {
  const [godCycle, setGodCycle] = useState(null);
  const [journal, setJournal] = useState([]);
  const [commentary, setCommentary] = useState([]);
  const [commentary, setCommentary] = useState([]);

  useEffect(() => {
    fetch("https://yantrax-backend.onrender.com/god-cycle")
      .then((res) => res.json())
      .then((data) => setStats(data))
      .catch((err) => console.error("God Cycle Fetch Error:", err));

  useEffect(() => {
    fetch("https://yantrax-backend.onrender.com/journal")
      .then((res) => res.json())
      .then((data) => setJournal(data))
      .catch((err) => console.error("Journal Fetch Error:", err));

  useEffect(() => {
    fetch("https://yantrax-backend.onrender.com/commentary")
      .then((res) => res.json())
      .then((data) => setCommentary(data))
      .catch((err) => console.error("Commentary Fetch Error:", err));
      .then((res) => res.json())
      .then((data) => setCommentary(data))
      .catch((err) => console.error("Commentary Fetch Error:", err));
  }, []);

  return (
    <div className="p-6 space-y-6 bg-gray-950 text-white min-h-screen">
      <h1 className="text-3xl font-bold">🧠 Yantra X — RL God Mode</h1>

      <button
        onClick={() => {
          fetch("https://yantrax-backend.onrender.com/god-cycle")
            .then((res) => res.json())
            .then((data) => setStats(data))
            .catch((err) => console.error("RL Cycle Error:", err));
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

      {/* Journal Logs */}
      <div>
        <h2 className="text-2xl font-semibold mb-2">🧾 Journal Logs</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {Array.isArray(journal) &&
            journal.map((entry, index) =>
              entry && entry.timestamp && entry.signal && entry.audit !== undefined ? (
                <JournalCard
                  key={index}
                  timestamp={entry.timestamp}
                  signal={entry.signal}
                  audit={entry.audit}
                  reward={entry.reward}
                />
              ) : null
            )}
        </div>
      </div>

      {/* Agent Commentary */}
      <div>
        <h2 className="text-2xl font-semibold mt-4">🧠 Agent Commentary</h2>
        <div className="space-y-2">
          {Array.isArray(commentary) &&
            commentary.map((entry, index) =>
              entry && entry.agent && entry.comment ? (
                <CommentaryCard
                  key={index}
                  agent={entry.agent}
                  comment={entry.comment}
                  timestamp={entry.timestamp}
                />
              ) : null
            )}
        </div>
      </div>
    </div>
  );
};

export default YantraDashboard;
