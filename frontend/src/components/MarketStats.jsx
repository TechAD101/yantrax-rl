// src/components/MarketStats.jsx
import React from "react";

const MarketStats = ({ data }) => {
  const stats = [
    { label: "Signal", value: data.signal, color: "text-yellow-400" },
    { label: "Audit", value: data.audit, color: "text-blue-400" },
    { label: "Reward", value: data.reward, color: "text-green-400" },
    { label: "Mood", value: data.state?.mood, color: "text-purple-400" },
    { label: "Price", value: data.state?.price, color: "text-orange-400" },
    { label: "Volatility", value: data.state?.volatility, color: "text-pink-400" },
    { label: "Balance", value: data.state?.balance, color: "text-cyan-400" },
    { label: "Curiosity", value: data.state?.curiosity, color: "text-red-400" },
    { label: "Position", value: data.state?.position, color: "text-lime-400" },
    { label: "Cycle", value: data.state?.cycle, color: "text-sky-400" },
  ];

  return (
    <div className="mt-8 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
      {stats.map(({ label, value, color }) => (
        <StatCard key={label} title={label} value={value} color={color} />
      ))}
    </div>
  );
};

const StatCard = ({ title, value, color }) => (
  <div className="bg-gray-800 p-6 rounded-xl shadow-md">
    <h2 className="text-sm text-gray-400">{title}</h2>
    <p className={`text-2xl font-bold mt-2 ${color}`}>{value}</p>
  </div>
);

export default MarketStats;
