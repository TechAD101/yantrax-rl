// src/components/AgentCommentary.jsx
import React from "react";

const AgentCommentary = ({ commentary }) => {
  if (!commentary || commentary.length === 0) return null;

  return (
    <div className="bg-black/30 rounded-xl p-6 mt-10 shadow-2xl border border-gray-700">
      <h2 className="text-2xl font-bold mb-4 text-indigo-400">🤖 Agent Commentary</h2>
      <div className="space-y-4">
        {commentary.map((entry, index) => (
          <div
            key={index}
            className="bg-gray-800/70 rounded-lg p-4 border border-gray-600"
          >
            <div className="flex justify-between text-sm text-gray-400 mb-2">
              <span>{entry.agent}</span>
              <span>{new Date(entry.timestamp).toLocaleString()}</span>
            </div>
            <p className="text-lg text-white">{entry.comment}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default AgentCommentary;
