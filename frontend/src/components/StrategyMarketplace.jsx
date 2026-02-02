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
            alert(`✅ Initiated Copy Protocol: ${name}`);
        } catch (e) {
            alert("Copy Protocol Failed.");
        } finally {
            setCopyingId(null);
        }
    };

    // Industrial Sparkline
    const Sparkline = ({ type }) => {
        const color = type === 'DEGEN' ? '#d946ef' : '#00ff94'; // Purple or Green
        const dataPoints = Array.from({ length: 8 }, () => Math.random() * 20 + 5);

        const createPath = (data) => {
            const width = 100;
            const height = 30;
            const step = width / (data.length - 1);
            let path = `M 0,${height - data[0]}`;

            for (let i = 0; i < data.length - 1; i++) {
                path += ` L ${(i + 1) * step},${height - data[i + 1]}`; // Sharp lines (L) instead of curves (Q)
            }
            return path;
        };

        return (
            <svg width="100" height="30" className="opacity-80">
                <path d={createPath(dataPoints)} fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="square" />
            </svg>
        );
    };

    if (loading) return (
        <div className="border border-[var(--border-muted)] bg-[var(--bg-panel)] p-4 h-full flex flex-col space-y-4 animate-pulse">
            <div className="h-8 bg-[var(--bg-surface)] w-1/3"></div>
            {[1, 2, 3].map(i => <div key={i} className="h-12 bg-[var(--bg-surface)] border border-[var(--border-muted)]"></div>)}
        </div>
    );

    return (
        <div className="border border-[var(--border-muted)] bg-[var(--bg-panel)] flex flex-col h-full overflow-hidden">

            {/* Header / Contest Banner */}
            <div className="p-4 border-b border-[var(--border-muted)] bg-[var(--bg-deep)]">
                <div className="flex justify-between items-center z-10">
                    <div>
                        <h3 className="text-[var(--text-primary)] font-bold text-sm tracking-[0.2em] flex items-center mb-1 font-mono">
                            STRATEGY.MARKET
                            <span className="ml-2 w-1.5 h-1.5 rounded-none bg-[var(--color-success)] animate-pulse"></span>
                        </h3>
                        {contest && (
                            <div className="text-[10px] text-[var(--color-warning)] mt-1 flex items-center space-x-2 font-mono uppercase">
                                <span className="">[🏆]</span>
                                <span>{contest.title}</span>
                                <span className="text-[var(--color-success)] border border-[var(--color-success)] px-1 opacity-80">
                                    {contest.prize_pool} REWARD
                                </span>
                            </div>
                        )}
                    </div>
                    <div className="text-[9px] text-[var(--color-info)] border border-[var(--color-info)] px-2 py-1 uppercase tracking-widest hover:bg-[var(--color-info)] hover:text-black cursor-pointer transition-colors font-mono">
                        Global Feed
                    </div>
                </div>
            </div>

            {/* Strategy List */}
            <div className="flex-1 overflow-auto p-0 scrollbar-hide">
                {strategies.map((strat, index) => (
                    <div key={strat.id} className="relative flex items-center justify-between p-4 border-b border-[var(--border-muted)] hover:bg-[var(--bg-surface)] transition-colors group">

                        {/* Interactive hover marker */}
                        <div className="absolute left-0 top-0 bottom-0 w-[2px] bg-[var(--color-success)] opacity-0 group-hover:opacity-100 transition-opacity"></div>

                        <div className="flex items-center space-x-4">
                            {/* Rank Badge */}
                            <div className="font-mono text-xs text-[var(--text-muted)] w-6 self-start mt-1">
                                {index + 1 < 10 ? `0${index + 1}` : index + 1}
                            </div>

                            <div>
                                <div className="text-sm font-bold text-[var(--text-primary)] group-hover:text-[var(--color-info)] transition-colors flex items-center space-x-2 font-mono uppercase">
                                    <span>{strat.name}</span>
                                    {strat.type === 'DEGEN' && <span className="text-[9px] text-[var(--color-danger)] border border-[var(--color-danger)] px-1 ml-2">UNK</span>}
                                </div>
                                <div className="text-[10px] text-[var(--text-muted)] font-mono uppercase mt-1">
                                    DEV: {strat.author}
                                </div>
                            </div>
                        </div>

                        {/* Mid Section: Sparkline (Hidden on mobile) */}
                        <div className="hidden md:block absolute left-1/2 transform -translate-x-1/2 w-20">
                            <Sparkline type={strat.type} />
                        </div>

                        <div className="flex items-center space-x-6">
                            <div className="text-right hidden sm:block">
                                <div className="text-xs text-[var(--color-success)] font-mono font-bold">SR: {strat.sharpe_ratio}</div>
                                <div className="text-[9px] text-[var(--text-muted)] font-mono tracking-wide uppercase">AUM: ${strat.aum.toLocaleString()}</div>
                            </div>

                            <button
                                onClick={() => handleCopy(strat.id, strat.name)}
                                disabled={copyingId === strat.id}
                                className="px-3 py-1 bg-transparent border border-[var(--border-active)] hover:border-[var(--color-success)] hover:text-[var(--color-success)] text-[var(--text-muted)] text-[10px] font-mono transition-all font-bold uppercase tracking-wider disabled:opacity-50 disabled:cursor-not-allowed">
                                {copyingId === strat.id ? 'INIT...' : 'COPY'}
                            </button>
                        </div>
                    </div>
                ))}
            </div>

            <div className="p-2 border-t border-[var(--border-muted)] text-center bg-[var(--bg-deep)]">
                <button className="text-[9px] text-[var(--text-muted)] hover:text-[var(--color-info)] transition-colors uppercase tracking-[0.2em] font-mono">
                    [ VIEW_FULL_INDEX ]
                </button>
            </div>
        </div>
    );
};

export default StrategyMarketplace;
