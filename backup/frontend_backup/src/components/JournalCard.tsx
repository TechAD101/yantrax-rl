import React from "react";

interface Props {
  timestamp: string;
  signal: string;
  audit: string;
  reward: number;
}

const JournalCard = ({ timestamp, signal, audit, reward }: Props) => {
  const color = reward >= 0 ? "text-green-400" : "text-red-400";

  return (
    <div className="bg-gray-900 text-white rounded-xl p-4 border border-gray-800 shadow-lg hover:shadow-2xl transition-all">
      <p className="text-xs text-gray-400">{new Date(timestamp).toLocaleString()}</p>
      <p className="text-xl font-bold mt-1">{signal}</p>
      <p className="text-sm text-blue-400">{audit}</p>
      <p className={`text-md font-semibold mt-2 ${color}`}>Reward: {reward}</p>
    </div>
  );
};

export default JournalCard;
