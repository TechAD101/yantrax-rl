import React, { useState, useEffect } from 'react';
import api from '../api/api';

const StrategyMarketplace = () => {
    const [strategies, setStrategies] = useState([]);
    const [contest, setContest] = useState(null);
    const [loading, setLoading] = useState(true);
    const [copyingId, setCopyingId] = useState(null);

    useEffect(() => {
        const loadData = async () => {
            try {
                const [stratData, contestData] = await Promise.all([
                    api.getTopStrategies(5),
                    api.getActiveContest()
                ]);
                setStrategies(stratData || []);
                setContest(contestData);
            } catch (err) {
                console.error("Marketplace load error", err);
            } finally {
                setLoading(false);
            }
        };
        loadData();
    }, []);

    const handleCopy = async (stratId, name) => {
        setCopyingId(stratId);
        try {
            await api.copyStrategy({ strategy_id: stratId, amount: 1000 });
            alert(`✅ Successfully copied ${name}!`);
        } catch (e) {
            alert("Copy failed (simulated).");
        } finally {
            setCopyingId(null);
        }
    };

    if (loading) return <div className="p-4 text-white/50 text-xs">Connecting to Global Strategy Network...</div>;

    return (
        <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl shadow-xl overflow-hidden flex flex-col h-full">

            {/* Header / Contest Banner */}
            <div className="p-4 border-b border-white/10 bg-gradient-to-r from-blue-900/40 to-purple-900/40">
                <div className="flex justify-between items-center">
                    <div>
                        <h3 className="text-white font-bold text-sm tracking-wider">STRATEGY MARKETPLACE</h3>
                        {contest && (
                            <div className="text-[10px] text-yellow-400 mt-1 animate-pulse">
                                🏆 ACTIVE: {contest.title} (Prize: {contest.prize_pool})
                            </div>
                        )}
                    </div>
                    <div className="bg-white/10 px-2 py-1 rounded text-[10px] text-white/70">
                        LIVE RANKINGS
                    </div>
                </div>
            </div>

            {/* Strategy List */}
            <div className="flex-1 overflow-auto p-2 space-y-2">
                {strategies.map((strat, index) => (
                    <div key={strat.id} className="flex items-center justify-between bg-white/5 p-3 rounded-lg hover:bg-white/10 transition-colors group">

                        <div className="flex items-center space-x-3">
                            {/* Rank Badge */}
                            <div className={`w-6 h-6 flex items-center justify-center rounded-full font-bold text-xs 
                                ${index === 0 ? 'bg-yellow-500 text-black' :
                                    index === 1 ? 'bg-gray-400 text-black' :
                                        index === 2 ? 'bg-orange-700 text-black' : 'bg-white/10 text-white'}`}>
                                {index + 1}
                            </div>

                            <div>
                                <div className="text-sm font-medium text-white group-hover:text-blue-400 transition-colors">
                                    {strat.name}
                                </div>
                                <div className="text-[10px] text-gray-400">
                                    by {strat.author} • <span className={`${strat.type === 'DEGEN' ? 'text-purple-400' : 'text-green-400'}`}>{strat.type}</span>
                                </div>
                            </div>
                        </div>

                        <div className="flex items-center space-x-4">
                            <div className="text-right hidden sm:block">
                                <div className="text-xs text-green-400 font-mono">Sharpe: {strat.sharpe_ratio}</div>
                                <div className="text-[10px] text-gray-500">AUM: ${strat.aum.toLocaleString()}</div>
                            </div>

                            <button
                                onClick={() => handleCopy(strat.id, strat.name)}
                                disabled={copyingId === strat.id}
                                className="px-3 py-1 bg-blue-600 hover:bg-blue-500 disabled:bg-gray-600 text-white text-xs rounded transition-all shadow-lg hover:shadow-blue-500/20 active:scale-95">
                                {copyingId === strat.id ? 'Start...' : 'COPY'}
                            </button>
                        </div>
                    </div>
                ))}
            </div>

            <div className="p-2 border-t border-white/5 text-center">
                <button className="text-[10px] text-gray-400 hover:text-white transition-colors">
                    VIEW ALL STRATEGIES →
                </button>
            </div>
        </div>
    );
};

export default StrategyMarketplace;
