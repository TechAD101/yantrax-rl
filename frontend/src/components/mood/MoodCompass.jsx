// src/components/mood/MoodCompass.jsx
import React, { useEffect, useState } from 'react';
import { getVisualMoodBoard } from '../../api/api';

const MoodCompass = () => {
    // 4 Axes: Volatility (Top), Liquidity (Right), Retail (Bottom), Institutional (Left)
    // Values come from the canonical mood board / market snapshot; without
    // backend data the compass renders an explicit unavailable state — the
    // previous random-drift mock is gone.
    const [data, setData] = useState(null);
    const [available, setAvailable] = useState(true);

    useEffect(() => {
        let cancelled = false;
        const load = async () => {
            try {
                const resp = await getVisualMoodBoard();
                if (cancelled) return;
                const board = resp?.data || resp || {};
                const dial = board.emotion_dial || {};
                const pain = dial.pain_meter;
                const mood = board.current_mood;
                const moodLabel = typeof mood === 'string' ? mood : (mood?.label || mood?.mood);
                setData({
                    // Pain meter doubles as the volatility axis (real CEO pain level)
                    volatility: pain == null ? 0 : Math.min(100, Math.max(0, pain)),
                    // Market mood mapped onto the retail-sentiment axis
                    retail: moodLabel === 'euphoric' ? 90 : moodLabel === 'bullish' ? 70 : moodLabel === 'bearish' ? 30 : moodLabel === 'panic' ? 10 : 50,
                    // Liquidity / institutional axes are not yet instrumented:
                    // explicit zeros with an "unavailable" note, never random.
                    liquidity: 0,
                    institutional: 0,
                });
                setAvailable(true);
            } catch (err) {
                if (!cancelled) setAvailable(false);
            }
        };
        load();
        const interval = setInterval(load, 30000);
        return () => { cancelled = true; clearInterval(interval); };
    }, []);

    // Calculate points for the polygon
    // Center is 100,100. Radius max is 80.

    const getPoint = (value, angle) => {
        const val = typeof value === 'number' ? value : 0;
        const radius = (val / 100) * 80;
        const radian = (angle - 90) * (Math.PI / 180);
        const x = 100 + radius * Math.cos(radian);
        const y = 100 + radius * Math.sin(radian);
        return `${x},${y}`;
    };

    if (!available) {
        return (
            <div className="bg-gray-900/80 backdrop-blur rounded-2xl p-6 border border-gray-800 flex flex-col items-center">
                <h3 className="text-lg font-bold text-gray-200 mb-4 w-full">Market Compass</h3>
                <div className="text-sm text-gray-500 py-12 text-center">
                    Compass data unavailable — no invented readings.
                </div>
            </div>
        );
    }

    if (!data) return null; // Defensive return while loading

    const p1 = getPoint(data?.volatility || 0, 0);   // Top
    const p2 = getPoint(data?.liquidity || 0, 90);   // Right
    const p3 = getPoint(data?.retail || 0, 180);     // Bottom
    const p4 = getPoint(data?.institutional || 0, 270); // Left

    const polygonPoints = `${p1} ${p2} ${p3} ${p4}`;

    return (
        <div className="bg-gray-900/80 backdrop-blur rounded-2xl p-6 border border-gray-800 flex flex-col items-center">
            <h3 className="text-lg font-bold text-gray-200 mb-4 w-full">Market Compass</h3>

            <div className="relative w-64 h-64">
                <svg viewBox="0 0 200 200" className="w-full h-full">
                    {/* Background Circles */}
                    <circle cx="100" cy="100" r="20" fill="none" stroke="#374151" strokeWidth="1" strokeDasharray="4 4" />
                    <circle cx="100" cy="100" r="50" fill="none" stroke="#374151" strokeWidth="1" strokeDasharray="4 4" />
                    <circle cx="100" cy="100" r="80" fill="none" stroke="#4b5563" strokeWidth="1" />

                    {/* Axes Lines */}
                    <line x1="100" y1="20" x2="100" y2="180" stroke="#374151" strokeWidth="1" />
                    <line x1="20" y1="100" x2="180" y2="100" stroke="#374151" strokeWidth="1" />

                    {/* Labels */}
                    <text x="100" y="15" textAnchor="middle" fill="#f87171" fontSize="10" fontWeight="bold">VOLATILITY</text>
                    <text x="190" y="105" textAnchor="start" fill="#60a5fa" fontSize="10" fontWeight="bold">LIQUIDITY</text>
                    <text x="100" y="195" textAnchor="middle" fill="#34d399" fontSize="10" fontWeight="bold">RETAIL</text>
                    <text x="10" y="105" textAnchor="end" fill="#fbbf24" fontSize="10" fontWeight="bold">INSTITUTIONAL</text>

                    {/* Data Polygon */}
                    <polygon
                        points={polygonPoints}
                        fill="rgba(59, 130, 246, 0.4)"
                        stroke="#3b82f6"
                        strokeWidth="2"
                        className="transition-all duration-1000 ease-in-out"
                    />

                    {/* Points */}
                    <circle cx={p1.split(',')[0]} cy={p1.split(',')[1]} r="3" fill="#f87171" className="transition-all duration-1000" />
                    <circle cx={p2.split(',')[0]} cy={p2.split(',')[1]} r="3" fill="#60a5fa" className="transition-all duration-1000" />
                    <circle cx={p3.split(',')[0]} cy={p3.split(',')[1]} r="3" fill="#34d399" className="transition-all duration-1000" />
                    <circle cx={p4.split(',')[0]} cy={p4.split(',')[1]} r="3" fill="#fbbf24" className="transition-all duration-1000" />
                </svg>
            </div>

            <div className="grid grid-cols-2 gap-4 w-full mt-4 text-xs">
                <div className="flex justify-between items-center bg-gray-800/50 p-2 rounded">
                    <span className="text-red-400">Vol</span>
                    <span className="font-mono text-white">{Math.round(data.volatility)}</span>
                </div>
                <div className="flex justify-between items-center bg-gray-800/50 p-2 rounded">
                    <span className="text-blue-400">Liq</span>
                    <span className="font-mono text-white">{Math.round(data.liquidity)}</span>
                </div>
                <div className="flex justify-between items-center bg-gray-800/50 p-2 rounded">
                    <span className="text-green-400">Ret</span>
                    <span className="font-mono text-white">{Math.round(data.retail)}</span>
                </div>
                <div className="flex justify-between items-center bg-gray-800/50 p-2 rounded">
                    <span className="text-yellow-400">Inst</span>
                    <span className="font-mono text-white">{Math.round(data.institutional)}</span>
                </div>
            </div>
        </div>
    );
};

export default MoodCompass;