// src/components/wizard/StepMarkets.jsx
import React from 'react';

const StepMarkets = ({ config, setConfig }) => {
    const markets = [
        { id: 'us_stocks', label: 'US Stocks', icon: '🇺🇸', sub: 'NYSE/NASDAQ' },
        { id: 'indian_stocks', label: 'Indian Stocks', icon: '🇮🇳', sub: 'NSE/BSE' },
        { id: 'crypto', label: 'Crypto', icon: '₿', sub: 'Top 50 Coins' },
        { id: 'indices', label: 'Institutional Indices', icon: '📊', sub: 'S&P 500, QQQ, VIX' },
        { id: 'commodities', label: 'Commodities', icon: '🧱', sub: 'Gold, Crude Oil, Silver' },
        { id: 'global_etfs', label: 'Global ETFs', icon: '🌍', sub: 'Macro Exposure' }
    ];

    const toggleMarket = (id) => {
        const current = config.markets || [];
        const updated = current.includes(id)
            ? current.filter(m => m !== id)
            : [...current, id];
        setConfig({ ...config, markets: updated });
    };

    return (
        <div className="animate-fade-in-up">
            <h2 className="text-2xl font-bold text-gray-100 mb-2">Select Your Markets</h2>
            <p className="text-gray-400 mb-8">Where should the AI Firm deploy capital?</p>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                {markets.map(market => (
                    <div
                        key={market.id}
                        onClick={() => toggleMarket(market.id)}
                        className={`p-6 rounded-xl border-2 flex items-center space-x-4 cursor-pointer transition-all duration-300
                            ${config.markets?.includes(market.id)
                                ? 'bg-blue-900/10 border-blue-500 shadow-blue-500/10 shadow-lg scale-[1.02]'
                                : 'bg-gray-800 border-gray-700 hover:border-gray-500'}`}
                    >
                        <div className="text-4xl">{market.icon}</div>
                        <div className="flex-1">
                            <h3 className="text-lg font-bold text-gray-200">{market.label}</h3>
                            <p className="text-xs text-gray-400 font-mono tracking-wide">{market.sub}</p>
                        </div>
                        <div className={`w-6 h-6 rounded-md flex items-center justify-center border-2
                            ${config.markets?.includes(market.id) ? 'bg-blue-500 border-blue-500' : 'border-gray-600'}`}>
                            {config.markets?.includes(market.id) && <span className="text-white text-xs font-bold">✓</span>}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default StepMarkets;
