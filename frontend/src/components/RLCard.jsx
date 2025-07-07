import React from "react";

const RLCard = ({ signal, mood, reward, audit }) => {
  const getSignalColor = (signal) => {
    switch (signal) {
      case "CONFIDENT BUY":
        return "bg-green-600";
      case "CAUTIOUS SELL":
        return "bg-yellow-500";
      case "WAIT":
      default:
        return "bg-gray-700";
    }
  };

  const getMoodEmoji = (mood) => {
    switch (mood) {
      case "Approved":
        return "✅";
      case "Warning":
        return "⚠️";
      case "Neutral":
      default:
        return "😐";
    }
  };

  return (
    <div className="p-4 bg-gray-800 rounded-2xl shadow-lg flex flex-col gap-3 w-full md:w-96 mx-auto mt-6">
      <h2 className="text-2xl font-bold text-center">🎯 RL Signal Summary</h2>
      <div className={`text-white text-center py-2 rounded-xl ${getSignalColor(signal)}`}>
        <p className="text-lg font-semibold">{signal || "WAIT"}</p>
      </div>
      <div className="flex justify-between text-sm text-gray-300 px-2">
        <span>Audit:</span>
        <span>{audit || "Neutral"}</span>
      </div>
      <div className="flex justify-between text-sm text-gray-300 px-2">
        <span>Mood:</span>
        <span>{getMoodEmoji(mood)} {mood || "Unknown"}</span>
      </div>
      <div className="flex justify-between text-sm text-gray-300 px-2">
        <span>Reward:</span>
        <span>{reward ?? "—"}</span>
      </div>
    </div>
  );
};

export default RLCard;
