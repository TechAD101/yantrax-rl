// src/components/mood/HypeHeatMap.jsx
import React from 'react';

const HypeHeatMap = () => {
    // Mock data
    const sectors = [
        { name: 'AI / Compute', status: 'surging', change: '+12.5%', icon: '🤖' },
        { name: 'DeFi 2.0', status: 'bleeding', change: '-5.2%', icon: '💸' },
        { name: 'Metaverse', status: 'silent', change: '+0.1%', icon: '🥽' },
        { name: 'Layer 1s', status: 'cooling', change: '-1.2%', icon: '⛓️' },
        { name: 'Gaming', status: 'surging', change: '+8.4%', icon: '🎮' },
        { name: 'Storage', status: 'silent', change: '0.0%', icon: '💾' }
    ];

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
            case 'silent': return '💤 SILENT';
            default: return '';
        }
    };

    return (
        <div className="bg-gray-900/80 backdrop-blur rounded-2xl p-6 border border-gray-800">
            <h3 className="text-lg font-bold text-gray-200 mb-4 flex justify-between items-center">
                <span>Sector Hype Map</span>
                <span className="text-xs font-mono text-gray-500">Live Updates</span>
            </h3>

            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                {sectors.map((sector, idx) => (
                    <div
                        key={idx}
                        className={`p-4 rounded-xl border flex flex-col items-center justify-center text-center transition-all duration-300 hover:scale-105 cursor-pointer ${getStyles(sector.status)}`}
                    >
                        <span className="text-3xl mb-2">{sector.icon}</span>
                        <span className="font-bold text-gray-200 text-sm">{sector.name}</span>
                        <span className={`text-xs font-mono mt-1 ${sector.change.startsWith('+') ? 'text-green-400' : sector.change.startsWith('-') ? 'text-red-400' : 'text-gray-400'}`}>
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
