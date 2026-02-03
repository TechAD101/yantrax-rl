import React, { useState, useEffect, useCallback } from 'react';
import api from '../api/api';

const WisdomPulse = () => {
    const [stats, setStats] = useState(null);
    const [ingesting, setIngesting] = useState(false);
    const [lastIngest, setLastIngest] = useState(null);

    const fetchStats = useCallback(async () => {
        try {
            const data = await api.getKnowledgeStats();
            setStats(data);
        } catch (error) {
            console.error('Stats fetch failed:', error);
        }
    }, []);

    useEffect(() => {
        fetchStats();
        const interval = setInterval(fetchStats, 60000); // 1 min update
        return () => clearInterval(interval);
    }, [fetchStats]);

    const handleIngest = async () => {
        setIngesting(true);
        try {
            const result = await api.triggerKnowledgeIngest();
            if (result.success) {
                setLastIngest(result);
                await fetchStats();
            }
        } catch (error) {
            console.error('Ingestion failed:', error);
        } finally {
            setIngesting(false);
        }
    };

    if (!stats) return null;

    return (
        <div className="border border-[var(--border-muted)] bg-[var(--bg-deep)] p-4 relative overflow-hidden">
            {/* Neural Background Animation (subtle) */}
            <div className="absolute inset-0 opacity-10 pointer-events-none">
                <div className="absolute top-0 left-0 w-full h-full bg-[radial-gradient(circle_at_center,_var(--color-info)_0%,_transparent_70%)]"></div>
            </div>

            <div className="flex justify-between items-center mb-4 pb-2 border-b border-[var(--border-muted)]">
                <h3 className="text-[var(--text-muted)] text-xs font-bold uppercase tracking-[0.2em] font-mono flex items-center">
                    <span className="w-2 h-2 mr-2 bg-[var(--color-info)] animate-ping"></span>
                    NEURAL MEMORY (RAG)
                </h3>
                <button
                    onClick={handleIngest}
                    disabled={ingesting}
                    className={`text-[9px] font-mono border px-2 py-0.5 transition-all
                        ${ingesting ? 'border-[var(--color-warning)] text-[var(--color-warning)] animate-pulse' :
                            'border-[var(--border-muted)] text-[var(--text-muted)] hover:border-[var(--color-info)] hover:text-white'}`}
                >
                    {ingesting ? 'INGESTING...' : 'SYNC NEURAL LINK'}
                </button>
            </div>

            <div className="grid grid-cols-2 gap-4">
                {/* Stats */}
                <div className="space-y-4">
                    <div>
                        <div className="text-2xl font-bold font-mono text-white">
                            {stats.total_items}
                        </div>
                        <div className="text-[10px] text-[var(--text-muted)] uppercase tracking-wider">Stored Insights</div>
                    </div>
                    <div className="flex gap-4">
                        <div>
                            <div className="text-sm font-mono text-[var(--color-info)]">
                                {stats.investor_wisdom_count}
                            </div>
                            <div className="text-[8px] text-[var(--text-muted)] uppercase">Wisdom</div>
                        </div>
                        <div>
                            <div className="text-sm font-mono text-[var(--color-success)]">
                                {stats.market_insights_count}
                            </div>
                            <div className="text-[8px] text-[var(--text-muted)] uppercase">Insights</div>
                        </div>
                    </div>
                </div>

                {/* Activity Visualizer */}
                <div className="flex items-end justify-between gap-1 h-12 pt-2 pr-2">
                    {[0.4, 0.7, 0.5, 0.9, 0.3, 0.6, 0.8, 0.5, 1.0, 0.4].map((h, i) => (
                        <div
                            key={i}
                            className="w-1 bg-[var(--color-info)] animate-pulse"
                            style={{
                                height: `${h * 100}%`,
                                animationDelay: `${i * 0.1}s`,
                                opacity: 0.3 + (h * 0.7)
                            }}
                        />
                    ))}
                </div>
            </div>

            {/* Neural Growth Message */}
            {lastIngest && (
                <div className="mt-3 text-[10px] font-mono text-[var(--color-success)] border-t border-[var(--color-success)]/20 pt-2 animate-fade-in">
                    ✓ NEURAL EXPANSION COMPLETE: +{lastIngest.ingested_count} BYTES
                </div>
            )}

            <div className="mt-4 text-[9px] font-mono text-[var(--text-muted)] uppercase tracking-widest text-right">
                Status: Fully Operational
            </div>
        </div>
    );
};

export default WisdomPulse;
