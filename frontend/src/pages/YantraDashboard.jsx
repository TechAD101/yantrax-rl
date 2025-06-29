import React, { useState } from "react";

export default function YantraDashboard() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const runCycle = async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await fetch("http://localhost:5000/run-cycle", {
        method: "POST",
      });

      if (!res.ok) {
        throw new Error("❌ Backend returned bad response.");
      }

      const data = await res.json();

      if (!data.signal || !data.audit || data.reward === undefined) {
        throw new Error("❌ Incomplete data from backend.");
      }

      setResult(data);
    } catch (err) {
      setError(err.message || "❌ Run cycle failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ fontFamily: "Arial, sans-serif", padding: "2rem" }}>
      <h1 style={{ fontSize: "2rem", marginBottom: "1rem" }}>
        🧠 Yantra X — RL God Mode
      </h1>
      <button
        onClick={runCycle}
        style={{
          fontSize: "1.5rem",
          padding: "0.75rem 2rem",
          backgroundColor: "#000",
          color: "#fff",
          borderRadius: "10px",
          border: "none",
          cursor: "pointer",
        }}
      >
        🚀 Run RL Cycle
      </button>

      {loading && <p style={{ marginTop: "1rem" }}>⏳ Running...</p>}

      {error && (
        <p style={{ marginTop: "1rem", color: "red", fontWeight: "bold" }}>
          {error}
        </p>
      )}

      {result && (
        <div style={{ marginTop: "2rem", fontSize: "1.2rem" }}>
          <p>📈 Signal: <strong>{result.signal}</strong></p>
          <p>🧾 Audit: <strong>{result.audit}</strong></p>
          <p>🎯 Reward: <strong>{result.reward}</strong></p>
          <p>💡 Market Mood: <strong>{result.mood || "N/A"}</strong></p>
          <p>🔁 Cycle #: <strong>{result.cycle || "N/A"}</strong></p>
          <p>💰 Balance: <strong>{result.balance || "N/A"}</strong></p>
          <p>📊 Price: <strong>{result.price || "N/A"}</strong></p>
        </div>
      )}
    </div>
  );
}
