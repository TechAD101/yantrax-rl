// src/components/wizard/StepRisk.jsx
import React from 'react';

const StepRisk = ({ config, setConfig }) => {
    const riskLevels = ['Conservative', 'Moderate', 'Aggressive'];
    // Map string values to indices for slider
    const currentIndex = (() => {
        if (config.risk === 'aggressive') return 2;
        if (config.risk === 'moderate') return 1;
        return 0; // conservative
    })();

    const handleChange = (e) => {
        const val = parseInt(e.target.value);
        let level = 'conservative';
        if (val === 1) level = 'moderate';
        if (val === 2) level = 'aggressive';
        setConfig({ ...config, risk: level });
    };

    const getRiskInfo = () => {
        switch (config.risk) {
            case 'aggressive':
                return {
                    color: 'text-red-400',
                    bgColor: 'bg-red-500',
                    border: 'border-red-500',
                    desc: 'High volatility tolerance. Wide stop losses. Pursues max drawdown for alpha.',
                    stopLoss: '8-12%',
                    maxPos: '25%'
                };
            case 'moderate':
                return {
                    color: 'text-yellow-400',
                    bgColor: 'bg-yellow-500',
                    border: 'border-yellow-500',
                    desc: 'Balanced approach. Standard risk management rules apply.',
                    stopLoss: '4-7%',
                    maxPos: '15%'
                };
            case 'conservative':
            default:
                return {
                    color: 'text-green-400',
                    bgColor: 'bg-green-500',
                    border: 'border-green-500',
                    desc: 'Capital preservation first. Strict checks. Avoids black swan risks.',
                    stopLoss: '1-3%',
                    maxPos: '5%'
                };
        }
    };

    const info = getRiskInfo();

    return (
        <div className="animate-fade-in-up">
            <h2 className="text-2xl font-bold text-gray-100 mb-2">Risk Appetite</h2>
            <p className="text-gray-400 mb-8">Define your tolerance for market volatility.</p>

            <div className="mb-12 relative px-4">
                <input
                    type="range"
                    min="0"
                    max="2"
                    step="1"
                    value={currentIndex}
                    onChange={handleChange}
                    className="w-full h-4 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-transparent relative z-20"
                    style={{
                        background: `linear-gradient(to right, #22c55e 0%, #eab308 50%, #ef4444 100%)`
                    }}
                />

                {/* Custom thumb via CSS usually, but for standard range input, standard slider is cleaner for compatibility.
                    Adding visual markers below.
                */}
                <div className="flex justify-between mt-4 text-sm font-bold text-gray-500 uppercase tracking-widest">
                    <span className={currentIndex === 0 ? 'text-green-400' : ''}>Conservative</span>
                    <span className={currentIndex === 1 ? 'text-yellow-400' : ''}>Moderate</span>
                    <span className={currentIndex === 2 ? 'text-red-400' : ''}>Aggressive</span>
                </div>
            </div>

            <div className={`p-6 rounded-xl border-l-4 ${info.border} bg-gray-800 transition-all duration-300`}>
                <h3 className={`text-2xl font-bold mb-2 ${info.color} capitalize`}>
                    {config.risk} Profile
                </h3>
                <p className="text-gray-300 text-lg mb-4">{info.desc}</p>

                <div className="grid grid-cols-2 gap-4 mt-4 bg-gray-900/50 p-4 rounded-lg">
                    <div>
                        <span className="text-gray-500 text-xs uppercase block">Avg Stop Loss</span>
                        <span className="text-white font-mono">{info.stopLoss}</span>
                    </div>
                    <div>
                        <span className="text-gray-500 text-xs uppercase block">Max Position Size</span>
                        <span className="text-white font-mono">{info.maxPos}</span>
                    </div>
                </div>
            </div>

            {config.risk === 'aggressive' && (
                <div className="mt-4 text-center text-xs text-red-500 font-bold uppercase animate-pulse">
                    ⚠️ Degen Auditor will be highly active
                </div>
            )}
        </div>
    );
};

export default StepRisk;
