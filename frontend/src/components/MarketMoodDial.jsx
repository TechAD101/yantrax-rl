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
        <div className="glass-card rounded-2xl p-6 flex items-center justify-center animate-pulse h-[300px]">
            <div className="text-cyan-400 font-mono text-xs tracking-widest flex items-center">
                <span className="animate-spin mr-3 text-xl">⚙️</span>
                CALIBRATING AI SENSO-MATRIX...
            </div>
        </div>
    );

    return (
        <div className="glass-card relative flex flex-col items-center p-6 rounded-2xl shadow-2xl group transition-all duration-700 hover:shadow-cyan-900/30 overflow-hidden">
            {/* Ambient Background Glow based on Mood */}
            <div className="absolute inset-0 opacity-10 transition-colors duration-1000"
                style={{ background: `radial-gradient(circle at center, ${current.color}, transparent 70%)` }} />

            {/* Breathing Border Glow */}
            <div className="absolute inset-0 rounded-2xl transition-all duration-1000 opacity-50"
                style={{ boxShadow: `inset 0 0 50px ${current.color}11` }}></div>

            <div className="flex justify-between w-full mb-6 px-2 relative z-10">
                <h3 className="text-gray-400 text-xs font-bold uppercase tracking-[0.2em] flex items-center">
                    <span className="w-1.5 h-1.5 rounded-full mr-2 animate-pulse" style={{ backgroundColor: current.color }}></span>
                    Institutional Mood
                </h3>
                <span className="text-[10px] text-white/40 font-mono border border-white/10 px-2 py-0.5 rounded-full bg-black/20 backdrop-blur-sm">
                    {data?.market_weather || 'SYNCING...'}
                </span>
            </div>

            <div className="relative w-48 h-48 my-2">
                {/* Outer Rotators */}
                <div className="absolute inset-0 border border-white/5 rounded-full animate-[spin_60s_linear_infinite]" />
                <div className="absolute inset-2 border border-dashed border-white/10 rounded-full animate-[spin_40s_linear_infinite_reverse]" />

                {/* Dial Scale */}
                <svg className="absolute inset-0 w-full h-full -rotate-90">
                    <defs>
                        <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="0%">
                            <stop offset="0%" style={{ stopColor: current.color, stopOpacity: 0.1 }} />
                            <stop offset="100%" style={{ stopColor: current.color, stopOpacity: 0.5 }} />
                        </linearGradient>
                    </defs>
                    <circle cx="96" cy="96" r="88" fill="none" stroke="url(#grad1)" strokeWidth="1" className="opacity-30" />
                    {/* Ticks */}
                    {Array.from({ length: 12 }).map((_, i) => (
                        <line key={i} x1="96" y1="10" x2="96" y2="20" stroke="white" strokeWidth="1"
                            transform={`rotate(${i * 30} 96 96)`} className="opacity-20" />
                    ))}
                </svg>

                {/* Needle/Indicator */}
                <div className="absolute inset-0 flex items-center justify-center transition-transform duration-[1500ms] cubic-bezier(0.34, 1.56, 0.64, 1)"
                    style={{ transform: `rotate(${current.angle}deg)` }}>
                    <div className="w-0.5 h-20 bg-gradient-to-t from-transparent via-white to-transparent opacity-80" />
                    <div className="absolute top-8 w-2 h-2 rounded-full shadow-[0_0_15px_currentColor] animate-pulse"
                        style={{ backgroundColor: current.color, boxShadow: `0 0 20px ${current.color}` }} />
                </div>

                {/* Center Display */}
                <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                    <span className="text-5xl mb-2 filter drop-shadow-[0_0_15px_rgba(255,255,255,0.2)] animate-float">
                        {current.emoji}
                    </span>
                    <span className="text-[9px] font-black tracking-[0.3em] text-white/30 uppercase block animate-pulse">
                        SENSING
                    </span>
                </div>
            </div>

            {/* Pain Meter & Labels */}
            <div className="mt-8 flex flex-col items-center z-10 w-full relative">
                <div className="px-6 py-1.5 rounded-full text-xs font-bold tracking-[0.2em] border transition-all duration-1000 backdrop-blur-md"
                    style={{
                        borderColor: `${current.color}44`,
                        backgroundColor: `${current.color}08`,
                        color: current.color,
                        boxShadow: `0 0 30px ${current.color}15`
                    }}>
                    {current.label}
                </div>

                {/* Pain Level Bar */}
                <div className="w-full mt-6 px-4">
                    <div className="flex justify-between text-[9px] text-gray-500 mb-1.5 uppercase tracking-wider font-medium">
                        <span>Zero Pain</span>
                        <span style={{ color: current.color }}>Max Pain: {data?.emotion_dial?.pain_meter}%</span>
                    </div>
                    <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden backdrop-blur-sm border border-white/5">
                        <div className="h-full transition-all duration-1000 ease-out relative overflow-hidden"
                            style={{ width: `${data?.emotion_dial?.pain_meter}%`, backgroundColor: current.color }}>
                            <div className="absolute inset-0 bg-white/20 animate-[shimmer_2s_infinite]"></div>
                        </div>
                    </div>
                </div>

                {/* AI Philosophy Quote */}
                <div className="mt-6 text-center max-w-[240px] relative">
                    <span className="absolute -top-2 left-1/2 transform -translate-x-1/2 text-2xl text-white/5 font-serif">"</span>
                    <p className="text-[11px] text-gray-400 italic leading-relaxed">
                        {data?.philosophy_quote || 'Silence is also a strategy.'}
                    </p>
                </div>

                {/* Trivia Ticker */}
                {data?.trivia_ticker && (
                    <div className="mt-4 px-3 py-1 rounded bg-blue-500/10 border border-blue-500/10">
                        <div className="text-[9px] text-blue-300 animate-pulse text-center font-mono">
                            ⚡ {data.trivia_ticker}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default MarketMoodDial;
