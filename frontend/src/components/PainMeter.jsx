import React from 'react';

const PainMeter = ({ painLevel = 0 }) => {
    // painLevel is 0-100
    const getColor = (level) => {
        if (level < 30) return '#10b981'; // Green
        if (level < 60) return '#f59e0b'; // Amber
        return '#ef4444'; // Red
    };

    const color = getColor(painLevel);
    const rotation = (painLevel / 100) * 180 - 90; // -90 to 90 degrees

    return (
        <div className="relative flex flex-col items-center p-6 bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl shadow-xl overflow-hidden group">
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-blue-500/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

            <h3 className="text-gray-400 text-sm font-medium mb-4 uppercase tracking-wider">Internal Pain Level</h3>

            <div className="relative w-48 h-24 overflow-hidden">
                {/* Semi-circle track */}
                <div className="absolute bottom-0 left-0 w-full h-48 border-[12px] border-white/5 rounded-full" />

                {/* Progress Arc */}
                <div
                    className="absolute bottom-0 left-0 w-full h-48 border-[12px] rounded-full transition-all duration-1000 ease-out"
                    style={{
                        borderColor: color,
                        clipPath: `inset(${100 - (painLevel / 2)}% 0 0 0)`, // Simplified arc clip
                        opacity: 0.8,
                        boxShadow: `0 0 20px ${color}44`
                    }}
                />

                {/* Needle */}
                <div
                    className="absolute bottom-0 left-1/2 w-1 h-20 bg-white origin-bottom -translate-x-1/2 transition-transform duration-1000 ease-out z-10"
                    style={{ transform: `translateX(-50%) rotate(${rotation}deg)` }}
                >
                    <div className="absolute -top-1 left-1/2 -translate-x-1/2 w-3 h-3 bg-white rounded-full shadow-[0_0_10px_rgba(255,255,255,0.8)]" />
                </div>

                {/* Center Point */}
                <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-4 h-4 bg-gray-800 border-2 border-white/20 rounded-full z-20" />
            </div>

            <div className="mt-4 flex flex-col items-center">
                <span className="text-4xl font-bold font-mono tracking-tighter" style={{ color }}>
                    {painLevel}%
                </span>
                <span className="text-xs text-gray-500 font-medium mt-1">
                    {painLevel < 30 ? 'OPTIMAL' : painLevel < 60 ? 'CAUTION' : 'HIGH STRESS'}
                </span>
            </div>

            <div className="mt-4 w-full grid grid-cols-3 gap-1 text-[10px] text-gray-600 font-bold uppercase">
                <div className="text-left">SAFE</div>
                <div className="text-center">RISK</div>
                <div className="text-right">PAIN</div>
            </div>
        </div>
    );
};

export default PainMeter;
