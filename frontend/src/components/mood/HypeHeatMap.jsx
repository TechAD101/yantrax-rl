// src/components/mood/HypeHeatMap.jsx
import React, { useState, useEffect } from 'react';
import { getVisualMoodBoard } from '../../api/api';

// Sector Hype Map. Renders canonical mood-board data from
// /api/visual_mood_board; without backend data it shows an explicit
// unavailable state — no invented sector movements.
const HypeHeatMap = () => {
    const [sectors, setSectors] = useState([]);
    const [available, setAvailable] = useState(true);

    useEffect(() => {
        let cancelled = false;
        const load = async () => {
            try {
                const resp = await getVisualMoodBoard();
                if (cancelled) return;
                const data = resp?.data || resp || {};
                const emotion = data.current_mood || {};
                const moodLabel = typeof emotion === 'string' ? emotion : (emotion.label || emotion.mood);
                const pain = data.emotion_dial?.pain_meter ?? null;
                setSectors([
                    { name: 'Firm Mood', status: 'silent', change: moodLabel || 'unknown', icon: '🏛️' },
                    { name: 'Pain Meter', status: 'silent', change: pain == null ? 'unavailable' : `${pain}%`, icon: '⚡' },
                ]);
                setAvailable(true);
            } catch (err) {
                if (!cancelled) {
                    setSectors([]);
                    setAvailable(false);
                }
            }
        };
        load();
        const interval = setInterval(load, 30000);
        return () => { cancelled = true; clearInterval(interval); };
    }, []);

    const getStyles = (status) => {
        switch (status) {
            case 'surging': return 'bg-green-500/20 border-green-500/50 shadow-[0_0_15px_rgba(34,197,94,0.3)]';
            case 'bleeding': return 'bg-red-500/20 border-red-500/50 shadow-[0_0_15px_rgba(239,68,68,0.3)]';
            case 'cooling': return 'bg-yellow-500/10 border-yellow-500/30';
            case 'silent': return 'bg-blue-500/5 border-blue-500/20 grayscale opacity-70';
            default: return 'bg-gray-800 border-gray-700';
        }
    };

    const getStatusLabel = (status) => {
        switch (status) {
            case 'surging': return '🔥 SURGING';
            case 'bleeding': return '🩸 BLEEDING';
            case 'cooling': return '🧊 COOLING';
            case 'silent': return '💤 CANONICAL';
            default: return '';
        }
    };

    return (
        <div className="bg-gray-900/80 backdrop-blur rounded-2xl p-6 border border-gray-800">
            <h3 className="text-lg font-bold text-gray-200 mb-4 flex justify-between items-center">
                <span>Sector Hype Map</span>
                <span className="text-xs font-mono text-gray-500">
                    {available ? 'Canonical Data' : 'Backend Unavailable'}
                </span>
            </h3>

            {!available && (
                <div className="text-sm text-gray-500 py-8 text-center">
                    Mood-board data unavailable — showing no invented market activity.
                </div>
            )}

            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                {sectors.map((sector, idx) => (
                    <div
                        key={idx}
                        className={`p-4 rounded-xl border flex flex-col items-center justify-center text-center transition-all duration-300 hover:scale-105 cursor-pointer ${getStyles(sector.status)}`}
                    >
                        <span className="text-3xl mb-2">{sector.icon}</span>
                        <span className="font-bold text-gray-200 text-sm">{sector.name}</span>
                        <span className="text-xs font-mono mt-1 text-gray-300">
                            {sector.change}
                        </span>
                        <span className="text-[10px] font-bold mt-2 uppercase tracking-wider opacity-80">
                            {getStatusLabel(sector.status)}
                        </span>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default HypeHeatMap;