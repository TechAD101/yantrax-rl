// src/components/CommentaryCard.jsx
import React from "react";

const CommentaryCard = ({ agent, comment, timestamp }) => {
  return (
    <div className="bg-gray-900 text-white rounded-xl p-4 border border-gray-800 shadow hover:shadow-lg transition-all">
      <p className="text-xs text-gray-400 mb-1">{new Date(timestamp).toLocaleString()}</p>
      <p className="text-sm text-blue-400 font-semibold">{agent}</p>
      <p className="mt-1 text-md">{comment}</p>
    </div>
  );
};

export default CommentaryCard;
