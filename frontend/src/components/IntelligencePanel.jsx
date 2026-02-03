import React, { useState, useEffect, useCallback } from 'react';
import api from '../api/api';

const IntelligencePanel = ({ ticker = 'AAPL', showNews = true }) => {
    const [sentiment, setSentiment] = useState(null);
    const [news, setNews] = useState([]);
    const [loading, setLoading] = useState(true);
    const [status, setStatus] = useState(null);
    const [debate, setDebate] = useState(null);
    const [debating, setDebating] = useState(false);

    const fetchIntelligence = useCallback(async () => {
        setLoading(true);
        try {
            const [sentimentData, statusData] = await Promise.all([
                api.getMarketSentiment(ticker),
                api.getIntelligenceStatus()
            ]);

            setSentiment(sentimentData);
            setStatus(statusData);

            if (showNews && statusData?.configured) {
                const newsData = await api.getTickerNews(ticker, 'all');
                setNews(newsData?.results || []);
            }
        } catch (error) {
            console.error('Intelligence fetch failed:', error);
        } finally {
            setLoading(false);
        }
    }, [ticker, showNews]);

    const handleTriggerDebate = async () => {
        setDebating(true);
        setDebate(null);
        try {
            const data = await api.triggerAIDebate(ticker);
            setDebate(data);
        } catch (error) {
            console.error('Debate trigger failed:', error);
        } finally {
            setDebating(false);
        }
    };

    useEffect(() => {
        fetchIntelligence();
        const interval = setInterval(fetchIntelligence, 300000); // 5 min refresh
        return () => clearInterval(interval);
    }, [fetchIntelligence]);

    const moodColors = {
        bullish: '#10b981',
        bearish: '#ef4444',
        neutral: '#6b7280',
        mixed: '#f59e0b'
    };

    const getMoodIcon = (mood) => {
        switch (mood?.toLowerCase()) {
            case 'bullish': return '📈';
            case 'bearish': return '📉';
            case 'mixed': return '⚖️';
            default: return '📊';
        }
    };

    if (loading) return (
        <div className="border border-[var(--border-muted)] bg-[var(--bg-panel)] p-4 h-[200px] flex items-center justify-center">
            <div className="text-[var(--color-info)] font-mono text-xs tracking-widest flex items-center">
                <span className="animate-pulse mr-3">🧠</span>
                ANALYZING MARKET SIGNALS...
            </div>
        </div>
    );

    const confidence = sentiment?.confidence || 0;
    const mood = sentiment?.mood?.toLowerCase() || 'neutral';
    const moodColor = moodColors[mood] || moodColors.neutral;

    return (
        <div className="border border-[var(--border-muted)] bg-[var(--bg-deep)] relative p-4 overflow-hidden">
            {/* Header */}
            <div className="flex justify-between items-center mb-4 pb-2 border-b border-[var(--border-muted)]">
                <h3 className="text-[var(--text-muted)] text-xs font-bold uppercase tracking-[0.2em] font-mono flex items-center">
                    <span className="w-2 h-2 mr-2 animate-pulse" style={{ backgroundColor: moodColor }}></span>
                    AI.INTELLIGENCE
                </h3>
                <div className="flex gap-2">
                    <button
                        onClick={handleTriggerDebate}
                        disabled={debating}
                        className={`text-[9px] font-mono border px-2 py-0.5 transition-all
                            ${debating ? 'border-[var(--color-warning)] text-[var(--color-warning)] animate-pulse' :
                                'border-[var(--border-muted)] text-[var(--text-muted)] hover:border-[var(--color-info)] hover:text-white'}`}
                    >
                        {debating ? 'DEBATING...' : 'TRIGGER DEBATE'}
                    </button>
                    <span className="text-[10px] text-[var(--text-muted)] font-mono border-l border-[var(--border-muted)] pl-2">
                        {status?.configured ? '🟢 LIVE' : '🔴 OFFLINE'}
                    </span>
                </div>
            </div>

            {/* Sentiment Display */}
            <div className="mb-4">
                <div className="flex items-center gap-3 mb-2">
                    <span className="text-3xl">{getMoodIcon(mood)}</span>
                    <div>
                        <div className="text-xl font-bold uppercase tracking-wide" style={{ color: moodColor }}>
                            {mood}
                        </div>
                        <div className="text-[10px] text-[var(--text-muted)] font-mono">
                            ${ticker} SENTIMENT
                        </div>
                    </div>
                    <div className="ml-auto text-right">
                        <div className="text-lg font-mono" style={{ color: moodColor }}>
                            {(confidence * 100).toFixed(0)}%
                        </div>
                        <div className="text-[10px] text-[var(--text-muted)]">CONFIDENCE</div>
                    </div>
                </div>

                {/* Confidence Bar */}
                <div className="h-1.5 w-full bg-[var(--bg-surface)] rounded-full overflow-hidden">
                    <div
                        className="h-full transition-all duration-1000 rounded-full"
                        style={{
                            width: `${confidence * 100}%`,
                            backgroundColor: moodColor,
                            boxShadow: `0 0 8px ${moodColor}66`
                        }}
                    />
                </div>
            </div>

            {/* Summary */}
            {sentiment?.summary && (
                <div className="text-xs text-[var(--text-secondary)] mb-4 p-2 bg-[var(--bg-surface)] border-l-2" style={{ borderColor: moodColor }}>
                    {sentiment.summary}
                </div>
            )}

            {/* Key Factors */}
            {sentiment?.key_factors?.length > 0 && (
                <div className="mb-4">
                    <div className="text-[10px] text-[var(--text-muted)] font-mono mb-2 uppercase">Key Factors</div>
                    <div className="flex flex-wrap gap-1.5">
                        {sentiment.key_factors.slice(0, 4).map((factor, i) => (
                            <span key={i} className="text-[10px] px-2 py-0.5 bg-[var(--bg-surface)] border border-[var(--border-muted)] text-[var(--text-secondary)]">
                                {factor}
                            </span>
                        ))}
                    </div>
                </div>
            )}

            {/* Debate Results (Overlay/Insert) */}
            {debate && (
                <div className="mb-4 bg-black/40 border border-[var(--color-info)]/30 p-3 rounded-sm animate-fade-in">
                    <div className="text-[10px] text-[var(--color-info)] font-mono mb-2 flex justify-between items-center">
                        <span>🏛️ THE FIRM HAS DECIDED: {debate.winning_signal}</span>
                        <button onClick={() => setDebate(null)} className="opacity-50 hover:opacity-100">✕</button>
                    </div>
                    <div className="space-y-3">
                        {debate.arguments?.slice(0, 2).map((arg, i) => (
                            <div key={i} className="border-l border-[var(--color-info)]/20 pl-2">
                                <div className="text-[9px] font-bold text-white uppercase">{arg.agent} ({arg.role})</div>
                                <div className="text-[10px] text-[var(--text-secondary)] italic">"{arg.reasoning.substring(0, 80)}..."</div>
                                {arg.rebuttals?.length > 0 && (
                                    <div className="mt-1 text-[9px] text-[var(--color-warning)] font-mono">
                                        ↳ REBUTTAL: {arg.rebuttals[0]}
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                    <div className="mt-2 pt-2 border-t border-[var(--border-muted)] text-[8px] text-[var(--text-muted)] font-mono flex justify-between">
                        <span>CONSENSUS: {(debate.consensus_score * 100).toFixed(0)}%</span>
                        <span>ID: {debate.id.split('-')[0]}</span>
                    </div>
                </div>
            )}

            {/* News Section */}
            {showNews && news.length > 0 && (
                <div className="border-t border-[var(--border-muted)] pt-3">
                    <div className="text-[10px] text-[var(--text-muted)] font-mono mb-2 uppercase flex items-center gap-2">
                        <span>📰</span> LIVE NEWS
                    </div>
                    <div className="space-y-2 max-h-32 overflow-y-auto">
                        {news.slice(0, 3).map((item, i) => (
                            <a
                                key={i}
                                href={item.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="block text-[11px] text-[var(--text-secondary)] hover:text-[var(--color-info)] truncate transition-colors"
                            >
                                <span className="text-[var(--text-muted)]">[{item.source}]</span> {item.title}
                            </a>
                        ))}
                    </div>
                </div>
            )}

            {/* Footer */}
            <div className="mt-4 pt-2 border-t border-[var(--border-muted)] flex justify-between text-[9px] text-[var(--text-muted)] font-mono">
                <span>POWERED BY PERPLEXITY AI</span>
                <span>{new Date().toLocaleTimeString()}</span>
            </div>
        </div>
    );
};

export default IntelligencePanel;
