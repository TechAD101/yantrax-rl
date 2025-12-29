import React, { useState, useEffect } from 'react';
import { getVotingHistory } from '../../api/api';

const TopSignals = () => {
    const [signals, setSignals] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchSignals = async () => {
            try {
                const data = await getVotingHistory(5);
                if (data && data.history) {
                    setSignals(data.history.map(s => ({
                        ticker: s.symbol || 'AAPL',
                        type: s.winning_signal?.includes('BUY') ? 'LONG' : s.winning_signal?.includes('SELL') ? 'SHORT' : 'HOLD',
                        conf: Math.round(s.consensus_strength * 100),
                        reason: s.divine_doubt_applied ? '👻 GHOST CIRCUIT BREAKER' : 'Multi-Agent Consensus',
                        time: new Date(s.timestamp).toLocaleTimeString()
                    })));
                }
            } catch (e) {
                console.error('Signals fetch failed', e);
            } finally {
                setLoading(false);
            }
        };
        fetchSignals();
        const interval = setInterval(fetchSignals, 60000); // Global Sync: 1 minute
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="bg-gray-900/80 backdrop-blur rounded-2xl p-6 border border-gray-800">
            <h3 className="text-lg font-bold text-gray-200 mb-4">Top Alpha Signals</h3>
            <div className="space-y-4">
                {loading && <div className="text-center py-10 animate-pulse text-gray-500 text-sm">Quantifying Alpha...</div>}
                {!loading && signals.length === 0 && <div className="text-center py-10 text-gray-600 text-xs italic">Waiting for institutional consensus...</div>}
                {!loading && signals.map((sig, i) => (
                    <div key={i} className="flex items-center justify-between p-3 bg-gray-800/50 rounded-lg border border-gray-700/50 hover:bg-gray-700/50 transition-colors">
                        <div className="flex items-center space-x-3">
                            <div className={`w-10 h-10 rounded-lg flex items-center justify-center font-bold text-sm
                                ${sig.type === 'LONG' ? 'bg-green-500/20 text-green-400' : sig.type === 'SHORT' ? 'bg-red-500/20 text-red-400' : 'bg-gray-700/20 text-gray-400'}`}>
                                {sig.ticker}
                            </div>
                            <div>
                                <div className="flex items-center space-x-2">
                                    <span className={`text-xs font-bold px-1.5 py-0.5 rounded ${sig.type === 'LONG' ? 'bg-green-500/20 text-green-400' : sig.type === 'SHORT' ? 'bg-red-500/20 text-red-400' : 'bg-gray-700/20 text-gray-400'}`}>
                                        {sig.type}
                                    </span>
                                    <span className="text-[10px] text-gray-500">{sig.time}</span>
                                </div>
                                <p className="text-xs text-gray-300 mt-1">{sig.reason}</p>
                            </div>
                        </div>
                        <div className="text-right">
                            <div className="text-xl font-bold font-mono text-gray-200">{sig.conf}%</div>
                            <div className="text-[10px] text-gray-500 uppercase">Confidence</div>
                        </div>
                    </div>
                ))}
            </div>
            <button className="w-full mt-4 py-2 text-xs text-blue-400 hover:bg-blue-900/20 rounded border border-blue-900/30 transition-colors">
                View All Signals
            </button>
        </div>
    );
};

export default TopSignals;
