import React from 'react';

const MarketMoodDial = ({ mood = 'neutral' }) => {
    const moods = {
        euphoria: { color: '#ec4899', label: 'EUPHORIA', angle: -60, emoji: '🚀' },
        greed: { color: '#10b981', label: 'GREED', angle: -30, emoji: '🤑' },
        neutral: { color: '#6b7280', label: 'NEUTRAL', angle: 0, emoji: '⚖️' },
        fear: { color: '#f59e0b', label: 'FEAR', angle: 30, emoji: '😨' },
        despair: { color: '#ef4444', label: 'DESPAIR', angle: 60, emoji: '💀' }
    };

    const current = moods[mood.toLowerCase()] || moods.neutral;

    return (
        <div className="relative flex flex-col items-center p-6 bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl shadow-xl group">
            <div className="absolute bottom-0 right-0 w-24 h-24 bg-blue-500/5 blur-3xl rounded-full" />

            <h3 className="text-gray-400 text-sm font-medium mb-6 uppercase tracking-wider">Institutional Mood</h3>

            <div className="relative w-40 h-40">
                {/* Outer Ring */}
                <div className="absolute inset-0 border-2 border-dashed border-white/10 rounded-full animate-[spin_20s_linear_infinite]" />

                {/* Glow behind center */}
                <div
                    className="absolute inset-4 rounded-full blur-xl transition-colors duration-1000"
                    style={{ backgroundColor: `${current.color}22` }}
                />

                {/* Dial Scale */}
                <svg className="absolute inset-0 w-full h-full -rotate-90">
                    <circle
                        cx="80" cy="80" r="75"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeDasharray="4 8"
                        className="text-white/5"
                    />
                </svg>

                {/* Needle/Indicator */}
                <div
                    className="absolute inset-0 flex items-center justify-center transition-transform duration-1000 cubic-bezier(0.4, 0, 0.2, 1)"
                    style={{ transform: `rotate(${current.angle}deg)` }}
                >
                    <div className="w-1 h-32 bg-gradient-to-t from-transparent via-white to-transparent opacity-80" />
                    <div
                        className="absolute top-0 w-3 h-3 rounded-full shadow-[0_0_15px_currentColor]"
                        style={{ backgroundColor: current.color, color: current.color }}
                    />
                </div>

                {/* Center Display */}
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <span className="text-4xl mb-1">{current.emoji}</span>
                    <div className="h-4 overflow-hidden">
                        <span className="text-[10px] font-black tracking-[0.2em] text-white/40 uppercase block animate-pulse">
                            SYSTEM SENSING
                        </span>
                    </div>
                </div>
            </div>

            <div className="mt-6 flex flex-col items-center">
                <div
                    className="px-4 py-1 rounded-full text-xs font-bold tracking-widest border transition-all duration-500"
                    style={{
                        borderColor: `${current.color}44`,
                        backgroundColor: `${current.color}11`,
                        color: current.color,
                        boxShadow: `0 0 15px ${current.color}22`
                    }}
                >
                    {current.label}
                </div>
                <p className="text-[10px] text-gray-500 mt-3 italic text-center max-w-[150px]">
                    "The market is a mirror of collective emotion."
                </p>
            </div>
        </div>
    );
};

export default MarketMoodDial;
