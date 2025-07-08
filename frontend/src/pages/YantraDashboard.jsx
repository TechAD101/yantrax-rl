// src/pages/YantraDashboard.jsx
import React, { useEffect, useState } from "react";
import JournalCard from "../components/JournalCard";

const YantraDashboard = () => {
  const [godCycle, setGodCycle] = useState(null);
  const [journal, setJournal] = useState([]);
  const [commentary, setCommentary] = useState([]);

  useEffect(() => {
    fetch("https://yantrax-backend.onrender.com/god-cycle")
      .then((res) => res.json())
      .then((data) => setGodCycle(data))
      .catch((err) => console.error("God Cycle Fetch Error:", err));
  }, []);

  useEffect(() => {
    fetch("https://yantrax-backend.onrender.com/journal")
      .then((res) => res.json())
      .then((data) => setJournal(data))
      .catch((err) => console.error("Journal Fetch Error:", err));
  }, []);

  useEffect(() => {
    fetch("https://yantrax-backend.onrender.com/commentary")
      .then((res) => res.json())
      .then((data) => setCommentary(data))
      .catch((err) => console.error("Commentary Fetch Error:", err));
  }, []);

  return (
    <div className="min-h-screen bg-black text-white p-4 space-y-6">
      <h1 className="text-2xl font-bold">🧠 Yantra X — RL God Mode</h1>

      {/* ✅ Safely render object */}
      {godCycle && typeof godCycle === "object" && (
        <div className="bg-gray-900 p-4 rounded-xl shadow-lg border border-gray-800">
          <h2 className="text-lg font-semibold mb-2">⚙️ God Mode Decision</h2>
          <p><strong>Action:</strong> {godCycle.action ?? "N/A"}</p>
          <p><strong>Reward:</strong> {godCycle.reward ?? "N/A"}</p>
          <p><strong>State:</strong> {godCycle.state ?? "N/A"}</p>
        </div>
      )}

      {/* ✅ Debug fallback if object fails */}
      {!godCycle && (
        <div className="text-red-500">⚠️ No God Mode data returned</div>
      )}

      {/* 📘 Journal logs */}
      <div>
        <h2 className="text-lg font-semibold mb-2">📘 Journal Logs</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {journal.map((entry, index) => (
            <JournalCard
              key={index}
              timestamp={entry.timestamp}
              signal={entry.signal}
              audit={entry.audit}
              reward={entry.reward}
            />
          ))}
        </div>
      </div>

      {/* 🧠 Commentary block */}
      <div>
        <h2 className="text-lg font-semibold mb-2">🗣️ Agent Commentary</h2>
        <div className="space-y-2">
          {commentary.map((line, index) => (
            <p key={index} className="text-gray-300">💬 {line}</p>
          ))}
        </div>
      </div>
    </div>
  );
};

export default YantraDashboard;
