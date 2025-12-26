// src/components/wizard/StepCapital.jsx
import React from 'react';

const StepCapital = ({ config, setConfig }) => {
    // Default to 100k if not set
    const capital = config.capital || 100000;

    const handleSliderChange = (e) => {
        setConfig({ ...config, capital: parseInt(e.target.value) });
    };

    const formatCurrency = (val) => {
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR',
            maximumFractionDigits: 0
        }).format(val);
    };

    return (
        <div className="animate-fade-in-up">
            <h2 className="text-2xl font-bold text-gray-100 mb-2">Capital Allocation</h2>
            <p className="text-gray-400 mb-8">Set your initial virtual balance for papertrading.</p>

            <div className="bg-gray-800 p-8 rounded-2xl border border-gray-700 text-center">
                <div className="text-5xl font-bold text-blue-400 mb-2 font-mono tracking-tight">
                    {formatCurrency(capital)}
                </div>
                <p className="text-gray-500 uppercase text-sm tracking-widest mb-8">Virtual Buying Power</p>

                <input
                    type="range"
                    min="10000"
                    max="10000000"
                    step="10000"
                    value={capital}
                    onChange={handleSliderChange}
                    className="w-full h-3 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-blue-500 hover:accent-blue-400"
                />

                <div className="flex justify-between text-xs text-gray-500 mt-4 font-mono">
                    <span>₹10,000</span>
                    <span>₹1 Cr</span>
                </div>
            </div>

            <div className="mt-6 flex items-start space-x-3 p-4 bg-blue-900/20 border border-blue-800 rounded-lg">
                <span className="text-2xl">ℹ️</span>
                <p className="text-sm text-blue-200">
                    This is <strong>virtual capital</strong>. YantraX RL will treat this amount as real money for risk management and position sizing calculations, but no real funds are at risk.
                </p>
            </div>
        </div>
    );
};

export default StepCapital;
