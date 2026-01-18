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

    // Simulated Smooth Sparkline Generator (Cubic Bezier)
    const Sparkline = ({ type }) => {
        const color = type === 'DEGEN' ? '#a855f7' : '#10b981'; // Purple or Green
        // Generate reduced noise data for smoother look
        const dataPoints = Array.from({ length: 8 }, () => Math.random() * 20 + 5);

        // Helper to create smooth path command
        const createPath = (data) => {
            const width = 100;
            const height = 30;
            const step = width / (data.length - 1);

            // Start point
            let path = `M 0,${height - data[0]}`;

            for (let i = 0; i < data.length - 1; i++) {
                const x0 = i * step;
                const y0 = height - data[i];
                const x1 = (i + 1) * step;
                const y1 = height - data[i + 1];
                const xc = (x0 + x1) / 2;
                const yc = (y0 + y1) / 2;

                path += ` Q ${xc},${yc} ${x1},${y1}`;
            }
            return path;
        };

        return (
            <svg width="100" height="30" className="opacity-60 group-hover:opacity-100 transition-all duration-500 ease-in-out">
                {/* Glow Filter */}
                <defs>
                    <filter id={`glow-${type}`} x="-20%" y="-20%" width="140%" height="140%">
                        <feGaussianBlur stdDeviation="2" result="blur" />
                        <feComposite in="SourceGraphic" in2="blur" operator="over" />
                    </filter>
                </defs>
                <path d={createPath(dataPoints)} fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" filter={`url(#glow-${type})`} />
            </svg>
        );
    };

    if (loading) return (
        // Skeleton Loader
        <div className="glass-card rounded-2xl p-4 h-full flex flex-col space-y-4 animate-pulse">
            <div className="h-8 bg-white/10 rounded w-1/3"></div>
            {[1, 2, 3].map(i => <div key={i} className="h-16 bg-white/5 rounded-lg"></div>)}
        </div>
    );

    return (
        <div className="glass-card rounded-2xl shadow-2xl overflow-hidden flex flex-col h-full ring-1 ring-white/5 transition-all duration-500 hover:shadow-cyan-900/20">

            {/* Header / Contest Banner */}
            <div className="p-4 border-b border-white/5 bg-gradient-to-r from-blue-900/40 to-purple-900/40 relative overflow-hidden">
                <div className="absolute inset-0 bg-grid-white/[0.03] bg-[length:20px_20px]" />
                <div className="relative flex justify-between items-center z-10">
                    <div>
                        <h3 className="text-white font-bold text-sm tracking-[0.2em] flex items-center">
                            STRATEGY MARKETPLACE
                            <span className="ml-2 w-2 h-2 rounded-full bg-emerald-500 animate-pulse-glow"></span>
                        </h3>
                        {contest && (
                            <div className="text-[10px] text-amber-400 mt-1 flex items-center space-x-2 animate-fade-in-scale">
                                <span className="animate-bounce">🏆</span>
                                <span className="font-mono">{contest.title}</span>
                                <span className="bg-amber-500/10 px-1 rounded text-amber-300 border border-amber-500/20 shadow-[0_0_10px_rgba(251,191,36,0.2)]">
                                    {contest.prize_pool} PRIZE
                                </span>
                            </div>
                        )}
                    </div>
                    <div className="bg-white/5 px-3 py-1 rounded-full text-[9px] text-white/50 border border-white/5 hover:border-white/20 hover:text-white hover:bg-white/10 transition-all cursor-pointer">
                        LIVE GLOBAL FEED
                    </div>
                </div>
            </div>

            {/* Strategy List */}
            <div className="flex-1 overflow-auto p-2 space-y-2 custom-scrollbar">
                {strategies.map((strat, index) => (
                    <div key={strat.id} className="relative flex items-center justify-between bg-white/5 p-3 rounded-xl hover:bg-white/10 transition-all duration-300 group hover:scale-[1.02] hover:-translate-y-0.5 hover:shadow-lg hover:shadow-purple-500/10 border border-transparent hover:border-white/10">

                        <div className="flex items-center space-x-4 z-10">
                            {/* Rank Badge */}
                            <div className={`w-8 h-8 flex items-center justify-center rounded-lg font-black text-sm shadow-lg
                                ${index === 0 ? 'bg-gradient-to-br from-amber-300 to-amber-600 text-black shadow-amber-500/20 scale-110' :
                                    index === 1 ? 'bg-gradient-to-br from-gray-300 to-gray-500 text-black shadow-gray-500/20' :
                                        index === 2 ? 'bg-gradient-to-br from-orange-400 to-orange-700 text-black shadow-orange-500/20' : 'bg-white/5 text-white/50'}`}>
                                {index + 1}
                            </div>

                            <div>
                                <div className="text-sm font-bold text-white group-hover:text-cyan-400 transition-colors flex items-center space-x-2">
                                    <span>{strat.name}</span>
                                    {strat.type === 'DEGEN' && <span className="text-[10px] bg-purple-500/20 text-purple-300 px-1 rounded border border-purple-500/20">DEGEN</span>}
                                </div>
                                <div className="text-[10px] text-gray-400 flex items-center space-x-2">
                                    <span className="opacity-70 group-hover:opacity-100 transition-opacity">by {strat.author}</span>
                                </div>
                            </div>
                        </div>

                        {/* Mid Section: Sparkline (Hidden on mobile) */}
                        <div className="hidden md:block absolute left-1/2 transform -translate-x-1/2 w-24">
                            <Sparkline type={strat.type} />
                        </div>

                        <div className="flex items-center space-x-4 z-10">
                            <div className="text-right hidden sm:block">
                                <div className="text-xs text-emerald-400 font-mono font-bold tracking-tight shadow-emerald-500/10 drop-shadow-sm">SR: {strat.sharpe_ratio}</div>
                                <div className="text-[9px] text-gray-500 font-mono tracking-widest uppercase group-hover:text-gray-400 transition-colors">AUM: ${strat.aum.toLocaleString()}</div>
                            </div>

                            <button
                                onClick={() => handleCopy(strat.id, strat.name)}
                                disabled={copyingId === strat.id}
                                className="px-4 py-1.5 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 disabled:from-gray-700 disabled:to-gray-700 text-white text-[10px] font-bold rounded-lg transition-all shadow-lg hover:shadow-blue-500/30 active:scale-95 border border-white/10 uppercase tracking-wider group-hover:ring-1 group-hover:ring-white/20">
                                {copyingId === strat.id ? 'Start...' : 'COPY'}
                            </button>
                        </div>
                    </div>
                ))}
            </div>

            <div className="p-3 border-t border-white/5 text-center bg-black/20 backdrop-blur-sm">
                <button className="text-[10px] text-gray-400 hover:text-white transition-colors uppercase tracking-widest hover:underline decoration-cyan-500 underline-offset-4 decoration-2">
                    View Complete Leaderboard
                </button>
            </div>
        </div>
    );
};

export default StrategyMarketplace;
