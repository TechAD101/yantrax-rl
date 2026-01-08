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

    if (loading) return <div className="text-white/50 animate-pulse text-xs">Calibrating AI Mood...</div>;

    return (
        <div className="relative flex flex-col items-center p-6 bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl shadow-xl group transition-all hover:scale-105 duration-500">
            {/* Ambient Background Glow based on Mood */}
            <div className="absolute inset-0 opacity-20 transition-colors duration-1000 rounded-2xl"
                style={{ background: `radial-gradient(circle at center, ${current.color}, transparent 70%)` }} />

            <div className="flex justify-between w-full mb-4 px-2">
                <h3 className="text-gray-400 text-sm font-medium uppercase tracking-wider">Institutional Mood</h3>
                <span className="text-xs text-white/60 font-mono">{data?.market_weather || 'Loading...'}</span>
            </div>

            <div className="relative w-40 h-40">
                {/* Outer Ring */}
                <div className="absolute inset-0 border-2 border-dashed border-white/10 rounded-full animate-[spin_30s_linear_infinite]" />

                {/* Dial Scale */}
                <svg className="absolute inset-0 w-full h-full -rotate-90">
                    <circle cx="80" cy="80" r="75" fill="none" stroke="currentColor" strokeWidth="2" strokeDasharray="4 8" className="text-white/5" />
                </svg>

                {/* Needle/Indicator */}
                <div className="absolute inset-0 flex items-center justify-center transition-transform duration-1000 cubic-bezier(0.4, 0, 0.2, 1)" style={{ transform: `rotate(${current.angle}deg)` }}>
                    <div className="w-1 h-32 bg-gradient-to-t from-transparent via-white to-transparent opacity-80" />
                    <div className="absolute top-0 w-3 h-3 rounded-full shadow-[0_0_15px_currentColor]" style={{ backgroundColor: current.color }} />
                </div>

                {/* Center Display */}
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <span className="text-4xl mb-1 animate-bounce duration-[3000ms]">{current.emoji}</span>
                    <span className="text-[9px] font-black tracking-[0.2em] text-white/40 uppercase block animate-pulse">SENSING</span>
                </div>
            </div>

            {/* Pain Meter & Labels */}
            <div className="mt-6 flex flex-col items-center z-10">
                <div className="px-4 py-1 rounded-full text-xs font-bold tracking-widest border transition-all duration-500"
                    style={{
                        borderColor: `${current.color}44`,
                        backgroundColor: `${current.color}11`,
                        color: current.color,
                        boxShadow: `0 0 15px ${current.color}22`
                    }}>
                    {current.label}
                </div>

                {/* Pain Level Bar */}
                <div className="w-full mt-3 px-4">
                    <div className="flex justify-between text-[9px] text-gray-500 mb-1">
                        <span>CALM</span>
                        <span>PAIN: {data?.emotion_dial?.pain_meter}%</span>
                    </div>
                    <div className="h-1 w-full bg-white/10 rounded-full overflow-hidden">
                        <div className="h-full bg-red-500 transition-all duration-1000" style={{ width: `${data?.emotion_dial?.pain_meter}%` }}></div>
                    </div>
                </div>

                {/* AI Philosophy Quote */}
                <p className="text-[10px] text-gray-400 mt-4 italic text-center max-w-[200px] leading-relaxed border-t border-white/5 pt-2">
                    "{data?.philosophy_quote || 'Silence is also a strategy.'}"
                </p>

                {/* Trivia Ticker */}
                {data?.trivia_ticker && (
                    <div className="mt-2 text-[9px] text-blue-400/80 animate-pulse text-center">
                        💡 {data.trivia_ticker}
                    </div>
                )}
            </div>
        </div>
    );
};

export default MarketMoodDial;
