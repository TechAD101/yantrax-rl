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
            // Confetti or visual feedback would go here
            alert(`✅ Successfully copied ${name}!`);
        } catch (e) {
            alert("Copy failed (simulated).");
        } finally {
            setCopyingId(null);
        }
    };

    // Simulated Sparkline Generator
    const Sparkline = ({ type }) => {
        const color = type === 'DEGEN' ? '#a855f7' : '#22c55e'; // Purple or Green
        const points = Array.from({ length: 10 }, (_, i) =>
            `${i * 10},${30 - Math.random() * 20}`
        ).join(' ');

        return (
            <svg width="100" height="30" className="opacity-50 group-hover:opacity-100 transition-opacity">
                <polyline points={points} fill="none" stroke={color} strokeWidth="2" />
            </svg>
        );
    };

    if (loading) return (
        // Skeleton Loader
        <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-4 h-full flex flex-col space-y-4 animate-pulse">
            <div className="h-8 bg-white/10 rounded w-1/3"></div>
            {[1, 2, 3].map(i => <div key={i} className="h-16 bg-white/5 rounded-lg"></div>)}
        </div>
    );

    return (
        <div className="bg-gradient-to-br from-gray-900/50 to-gray-800/30 backdrop-blur-xl border border-white/10 rounded-2xl shadow-2xl overflow-hidden flex flex-col h-full ring-1 ring-white/5">

            {/* Header / Contest Banner */}
            <div className="p-4 border-b border-white/10 bg-gradient-to-r from-blue-900/20 to-purple-900/20 relative overflow-hidden">
                <div className="absolute inset-0 bg-grid-white/[0.02] bg-[length:20px_20px]" />
                <div className="relative flex justify-between items-center z-10">
                    <div>
                        <h3 className="text-white font-bold text-sm tracking-[0.2em] flex items-center">
                            STRATEGY MARKETPLACE
                            <span className="ml-2 w-2 h-2 rounded-full bg-green-500 animate-ping"></span>
                        </h3>
                        {contest && (
                            <div className="text-[10px] text-yellow-400 mt-1 flex items-center space-x-2">
                                <span className="animate-pulse">🏆</span>
                                <span className="font-mono">{contest.title}</span>
                                <span className="bg-yellow-500/10 px-1 rounded text-yellow-300 border border-yellow-500/20">
                                    {contest.prize_pool} PRIZE
                                </span>
                            </div>
                        )}
                    </div>
                    <div className="bg-white/5 px-3 py-1 rounded-full text-[9px] text-white/50 border border-white/5 hover:border-white/20 transition-colors cursor-pointer">
                        LIVE GLOBAL FEED
                    </div>
                </div>
            </div>

            {/* Strategy List */}
            <div className="flex-1 overflow-auto p-2 space-y-2 custom-scrollbar">
                {strategies.map((strat, index) => (
                    <div key={strat.id} className="relative flex items-center justify-between bg-white/5 p-3 rounded-xl hover:bg-white/10 transition-all duration-300 group hover:scale-[1.01] hover:shadow-lg hover:shadow-purple-500/5 border border-transparent hover:border-white/10">

                        <div className="flex items-center space-x-4 z-10">
                            {/* Rank Badge */}
                            <div className={`w-8 h-8 flex items-center justify-center rounded-lg font-black text-sm shadow-inner
                                ${index === 0 ? 'bg-gradient-to-br from-yellow-300 to-yellow-600 text-black shadow-yellow-500/20' :
                                    index === 1 ? 'bg-gradient-to-br from-gray-300 to-gray-500 text-black' :
                                        index === 2 ? 'bg-gradient-to-br from-orange-400 to-orange-700 text-black' : 'bg-white/5 text-white/50'}`}>
                                {index + 1}
                            </div>

                            <div>
                                <div className="text-sm font-bold text-white group-hover:text-blue-400 transition-colors flex items-center space-x-2">
                                    <span>{strat.name}</span>
                                    {strat.type === 'DEGEN' && <span className="text-[10px] bg-purple-500/20 text-purple-300 px-1 rounded">DEGEN</span>}
                                </div>
                                <div className="text-[10px] text-gray-400 flex items-center space-x-2">
                                    <span className="opacity-70">by {strat.author}</span>
                                </div>
                            </div>
                        </div>

                        {/* Mid Section: Sparkline (Hidden on mobile) */}
                        <div className="hidden md:block absolute left-1/2 transform -translate-x-1/2">
                            <Sparkline type={strat.type} />
                        </div>

                        <div className="flex items-center space-x-4 z-10">
                            <div className="text-right hidden sm:block">
                                <div className="text-xs text-green-400 font-mono font-bold tracking-tight">SR: {strat.sharpe_ratio}</div>
                                <div className="text-[9px] text-gray-500 font-mono tracking-widest uppercase">AUM: ${strat.aum.toLocaleString()}</div>
                            </div>

                            <button
                                onClick={() => handleCopy(strat.id, strat.name)}
                                disabled={copyingId === strat.id}
                                className="px-4 py-1.5 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 disabled:from-gray-700 disabled:to-gray-700 text-white text-[10px] font-bold rounded-lg transition-all shadow-lg hover:shadow-blue-500/30 active:scale-95 border border-white/10 uppercase tracking-wider">
                                {copyingId === strat.id ? 'Start...' : 'COPY'}
                            </button>
                        </div>
                    </div>
                ))}
            </div>

            <div className="p-3 border-t border-white/5 text-center bg-black/20">
                <button className="text-[10px] text-gray-400 hover:text-white transition-colors uppercase tracking-widest hover:underline decoration-blue-500 underline-offset-4">
                    View Complete Leaderboard
                </button>
            </div>
        </div>
    );
};

export default StrategyMarketplace;
