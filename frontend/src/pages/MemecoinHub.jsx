import React, { useState, useEffect } from 'react';
import { BASE_URL, scanMemecoins, getTopMemecoins, simulateMemecoin } from '../api/api';

const MemecoinHub = () => {
  const [candidates, setCandidates] = useState([]);
  const [top, setTop] = useState([]);
  const [loading, setLoading] = useState(false);
  const [symbol, setSymbol] = useState('');
  const [usd, setUsd] = useState(100);
  const [result, setResult] = useState(null);

  useEffect(() => {
    loadTop();
  }, []);

  const loadTop = async () => {
    try {
      const res = await getTopMemecoins(5);
      setTop(res.memecoins || []);
    } catch (e) {
      console.error('Failed load top memecoins', e);
    }
  };

  const doScan = async () => {
    setLoading(true);
    try {
      const res = await scanMemecoins(['DOGE', 'SHIB', 'PEPE', 'WOJAK', 'MEME', 'TEST1']);
      setCandidates(res.results || []);
      await loadTop();
    } catch (e) {
      console.error('Scan failed', e);
    } finally {
      setLoading(false);
    }
  };

  const doSimulate = async () => {
    try {
      const r = await simulateMemecoin(symbol, usd);
      setResult(r.result);
      await loadTop();
    } catch (e) {
      console.error('Simulate failed', e);
    }
  };

  return (
    <div className="p-6 bg-gray-900/80 rounded-xl border border-gray-700/40">
      <h2 className="text-xl font-bold text-white mb-4">Memecoin Engine (Prototype)</h2>

      <div className="mb-4">
        <button onClick={doScan} className="px-3 py-2 bg-indigo-600 rounded text-white">{loading ? 'Scanning…' : 'Scan Market'}</button>
      </div>

      {candidates.length > 0 && (
        <div className="mb-4">
          <h4 className="text-sm text-gray-300 mb-2">Candidates</h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
            {candidates.map(c => (
              <div key={c.symbol} className="bg-gray-800/40 p-3 rounded">
                <div className="font-bold text-white">{c.symbol}</div>
                <div className="text-xs text-gray-400">Score: {c.degen_score}</div>
                <div className="text-xs text-gray-400">Social: {c.social} • Mentions: {c.mentions}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="mb-4">
        <h4 className="text-sm text-gray-300 mb-2">Top Memecoins</h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
          {top.map(m => (
            <div key={m.symbol} className="bg-gray-800/40 p-3 rounded">
              <div className="font-bold text-white">{m.symbol}</div>
              <div className="text-xs text-gray-400">Score: {m.score}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="mb-4">
        <h4 className="text-sm text-gray-300 mb-2">Simulate Trade (Paper)</h4>
        <div className="flex items-center space-x-2">
          <input placeholder="Symbol" value={symbol} onChange={e => setSymbol(e.target.value)} className="px-2 py-1 rounded bg-gray-900/50" />
          <input type="number" value={usd} onChange={e => setUsd(Number(e.target.value))} className="px-2 py-1 rounded bg-gray-900/50 w-24" />
          <button onClick={doSimulate} className="px-3 py-1 bg-green-600 rounded text-white">Simulate</button>
        </div>
        {result && (
          <div className="mt-2 text-sm text-gray-300">Purchased {result.quantity} {result.symbol} @ ${result.price} ({result.usd} USD)</div>
        )}
      </div>
    </div>
  );
};

export default MemecoinHub;
