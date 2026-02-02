import React, { useState, useEffect } from 'react';
import api from '../api/api';

const MarketMoodDial = () => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const result = await api.getVisualMoodBoard();
                setData(result);
            } catch (error) {
                console.error("Failed to load mood board", error);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
        const interval = setInterval(fetchData, 60000); // Update every minute
        return () => clearInterval(interval);
    }, []);

    const mood = data?.emotion_dial?.current_mood || 'neutral';

    const moods = {
        euphoria: { color: '#ec4899', label: 'EUPHORIA', angle: -60, emoji: '🚀' },
        greed: { color: '#10b981', label: 'GREED', angle: -30, emoji: '🤑' },
        neutral: { color: '#6b7280', label: 'NEUTRAL', angle: 0, emoji: '⚖️' },
        fear: { color: '#f59e0b', label: 'FEAR', angle: 30, emoji: '😨' },
        despair: { color: '#ef4444', label: 'DESPAIR', angle: 60, emoji: '💀' }
    };

    const current = moods[mood.toLowerCase()] || moods.neutral;

    if (loading) return (
        <div className="border border-[var(--border-muted)] bg-[var(--bg-panel)] p-6 flex items-center justify-center h-[300px]">
            <div className="text-[var(--color-info)] font-mono text-xs tracking-widest flex items-center">
                <span className="animate-spin mr-3 text-xl">⚙️</span>
                CALIBRATING SENSORS...
            </div>
        </div>
    );

    return (
        <div className="border border-[var(--border-muted)] bg-[var(--bg-deep)] relative flex flex-col items-center p-6 transition-all duration-700 overflow-hidden">
            {/* Background Grid Pattern */}
            <div className="absolute inset-0 opacity-10 bg-[linear-gradient(rgba(255,255,255,0.05)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.05)_1px,transparent_1px)] bg-[size:20px_20px]"></div>

            <div className="flex justify-between w-full mb-6 px-2 relative z-10 border-b border-[var(--border-muted)] pb-2">
                <h3 className="text-[var(--text-muted)] text-xs font-bold uppercase tracking-[0.2em] flex items-center font-mono">
                    <span className="w-2 h-2 mr-2 animate-pulse" style={{ backgroundColor: current.color }}></span>
                    MOOD.INDEX
                </h3>
                <span className="text-[10px] text-[var(--color-info)] font-mono border border-[var(--border-muted)] px-2 py-0.5 bg-[var(--bg-surface)] uppercase">
                    {data?.market_weather || 'SYNCING...'}
                </span>
            </div>

            <div className="relative w-48 h-48 my-2">
                {/* Outer Rotators - Industrial Rings */}
                <div className="absolute inset-0 border border-[var(--border-muted)] rounded-full border-dashed animate-[spin_60s_linear_infinite]" />
                <div className="absolute inset-4 border border-[var(--border-muted)] rounded-full animate-[spin_40s_linear_infinite_reverse]" />

                {/* Dial Scale */}
                <svg className="absolute inset-0 w-full h-full -rotate-90">
                    {/* Ticks */}
                    {Array.from({ length: 12 }).map((_, i) => (
                        <line key={i} x1="96" y1="10" x2="96" y2="20" stroke="var(--border-muted)" strokeWidth="2"
                            transform={`rotate(${i * 30} 96 96)`} />
                    ))}
                </svg>

                {/* Needle/Indicator - Sharp & Precise */}
                <div className="absolute inset-0 flex items-center justify-center transition-transform duration-[1500ms] cubic-bezier(0.2, 0.8, 0.2, 1)"
                    style={{ transform: `rotate(${current.angle}deg)` }}>
                    <div className="w-1 h-24 bg-[var(--text-primary)]" style={{ transformOrigin: 'bottom' }}></div>
                    <div className="absolute top-2 w-3 h-3 border border-black"
                        style={{ backgroundColor: current.color }} />
                </div>

                {/* Center Display */}
                <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                    <span className="text-4xl mb-4 opacity-80 filter grayscale hover:grayscale-0 transition-all">
                        {current.emoji}
                    </span>
                    <span className="text-[9px] font-mono font-bold tracking-[0.3em] text-[var(--text-muted)] uppercase block bg-[var(--bg-deep)] px-2 border border-[var(--border-muted)]">
                        STATUS
                    </span>
                </div>
            </div>

            {/* Pain Meter & Labels */}
            <div className="mt-8 flex flex-col items-center z-10 w-full relative">
                <div className="px-6 py-1 text-xs font-mono font-bold tracking-[0.2em] border transition-all duration-300 uppercase"
                    style={{
                        borderColor: current.color,
                        color: current.color,
                        boxShadow: `0 0 10px ${current.color}33`
                    }}>
                    {current.label}
                </div>

                {/* Pain Level Bar */}
                <div className="w-full mt-6 px-4">
                    <div className="flex justify-between text-[9px] text-[var(--text-muted)] mb-1.5 uppercase tracking-wider font-mono">
                        <span>ZERO PAIN</span>
                        <span style={{ color: current.color }}>MAX: {data?.emotion_dial?.pain_meter}%</span>
                    </div>
                    <div className="h-2 w-full bg-[var(--bg-surface)] border border-[var(--border-muted)] overflow-hidden">
                        <div className="h-full transition-all duration-1000 ease-out relative"
                            style={{ width: `${data?.emotion_dial?.pain_meter}%`, backgroundColor: current.color }}>
                            {/* Stripes */}
                            <div className="absolute inset-0" style={{ backgroundImage: 'linear-gradient(45deg,rgba(0,0,0,0.3) 25%,transparent 25%,transparent 50%,rgba(0,0,0,0.3) 50%,rgba(0,0,0,0.3) 75%,transparent 75%,transparent)', backgroundSize: '4px 4px' }}></div>
                        </div>
                    </div>
                </div>

                {/* AI Philosophy Quote */}
                <div className="mt-6 text-center w-full border-t border-[var(--border-muted)] pt-4 relative">
                    <p className="text-[10px] text-[var(--text-secondary)] font-mono leading-relaxed uppercase tracking-wide">
                        <span className="text-[var(--color-info)] mr-2">>></span>
                        {data?.philosophy_quote || 'SILENCE IS STRATEGY.'}
                    </p>
                </div>

                {/* Trivia Ticker */}
                {data?.trivia_ticker && (
                    <div className="mt-4 w-full bg-[var(--bg-surface)] border-l-2 border-[var(--color-info)] p-2">
                        <div className="text-[9px] text-[var(--color-info)] font-mono uppercase truncate">
                            NET_INFO: {data.trivia_ticker}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default MarketMoodDial;
