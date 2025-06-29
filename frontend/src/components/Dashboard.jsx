// src/main.jsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);


// src/App.jsx
import React from 'react';
import YantraDashboard from './pages/YantraDashboard';

const App = () => {
  return <YantraDashboard />;
};

export default App;


// src/pages/YantraDashboard.jsx
import React, { useState } from 'react';
import MarketStats from '../components/MarketStats';

const YantraDashboard = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  const runCycle = async () => {
    setLoading(true);
    try {
      const res = await fetch('http://localhost:5000/run-cycle', {
        method: 'POST'
      });
      const result = await res.json();
      setData(result);
    } catch (error) {
      alert("❌ Error running cycle");
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 to-black text-white p-6">
      <h1 className="text-4xl font-extrabold mb-6 text-center">🧠 Yantra X God Mode</h1>
      <div className="flex justify-center">
        <button
          onClick={runCycle}
          className="bg-indigo-600 hover:bg-indigo-700 px-6 py-3 text-lg rounded-xl shadow-xl"
          disabled={loading}
        >
          {loading ? 'Running...' : '🚀 Run RL Cycle'}
        </button>
      </div>
      {data && <MarketStats data={data} />}
    </div>
  );
};

export default YantraDashboard;


// src/components/MarketStats.jsx
import React from 'react';

const MarketStats = ({ data }) => {
  return (
    <div className="mt-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <StatCard title="Signal" value={data.signal} color="text-yellow-400" />
      <StatCard title="Audit" value={data.audit} color="text-blue-400" />
      <StatCard title="Reward" value={data.reward} color="text-green-400" />
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
