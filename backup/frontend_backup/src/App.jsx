import React, { useState } from "react";

const App = () => {
  const [info, setInfo] = useState(null);
  const [loading, setLoading] = useState(false);

  const runCycle = async () => {
    setLoading(true);
    try {
      const res = await fetch("http://localhost:5000/run-cycle", {
        method: "POST",
      });
      const data = await res.json();
      setInfo(data);
    } catch (err) {
      alert("❌ Run failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white flex flex-col items-center justify-center px-4">
      <h1 className="text-4xl font-bold mb-6">🧠 Yantra X: RL God Mode</h1>

      <button
        onClick={runCycle}
        className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-xl mb-6 shadow-lg"
      >
        {loading ? "⏳ Running..." : "🚀 Run RL Cycle"}
      </button>

      {info && (
        <div className="grid grid-cols-2 gap-4 text-lg bg-gray-800 p-6 rounded-xl shadow-inner w-full max-w-md">
          <div>🧠 Mood:</div> <div>{info.mood}</div>
          <div>💹 Price:</div> <div>{info.price}</div>
          <div>📉 Volatility:</div> <div>{info.volatility}</div>
          <div>📊 Balance:</div> <div>{info.balance}</div>
          <div>🧘 Curiosity:</div> <div>{info.curiosity}</div>
          <div>🪙 Position:</div> <div>{info.position}</div>
          <div>🧠 Cycle:</div> <div>{info.cycle}</div>
          <div>💰 Reward:</div> <div>{info.reward}</div>
        </div>
      )}
    </div>
  );
};

export default App;
