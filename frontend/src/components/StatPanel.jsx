import React from "react";

const StatBox = ({ label, value }) => (
  <div className="bg-gray-700 text-white rounded-xl p-4 flex flex-col items-center justify-center shadow-md">
    <div className="text-xs text-gray-300 uppercase">{label}</div>
    <div className="text-xl font-bold">{value ?? "—"}</div>
  </div>
);

const StatPanel = ({ data }) => {
  const { balance, curiosity, position, price, volatility } = data || {};

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 gap-4 my-6 max-w-4xl mx-auto">
      <StatBox label="Balance" value={`$${balance?.toFixed(2)}`} />
      <StatBox label="Curiosity" value={curiosity?.toFixed(2)} />
      <StatBox label="Position" value={position} />
      <StatBox label="Price" value={`$${price?.toFixed(2)}`} />
      <StatBox label="Volatility" value={volatility?.toFixed(2)} />
    </div>
  );
};

export default StatPanel;
