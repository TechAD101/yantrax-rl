// src/components/wizard/StepStrategy.jsx
import React from 'react';

const StepStrategy = ({ config, setConfig }) => {
    const strategies = [
        {
            id: 'ai_managed',
            label: 'Institutional Mode',
            desc: 'Warren, Cathie & Macro Monk manage portfolio with multi-agent consensus.',
            icon: '🏛️',
            personas: ['warren', 'cathie', 'macro_monk'],
            color: 'blue'
        },
        {
            id: 'degen_mode',
            label: 'Degen Mode',
            desc: 'High risk plays monitored by the Degen Auditor. No limiters except survival.',
            icon: '🧨',
            personas: ['degen_auditor', 'the_ghost'],
            color: 'purple'
        },
        {
            id: 'manual',
            label: 'CEO Mode (Manual)',
            desc: 'You are the CEO. AI agents act as the Council of Ghosts for advice only.',
            icon: '👨‍✈️',
            personas: ['the_ghost'],
            color: 'gray'
        }
    ];

    return (
        <div className="animate-fade-in-up">
            <h2 className="text-2xl font-bold text-gray-100 mb-2">Choose Your Strategy</h2>
            <p className="text-gray-400 mb-8">How autonomous should the firm be?</p>

            <div className="grid grid-cols-1 gap-6">
                {strategies.map(strategy => {
                    const isSelected = config.strategy === strategy.id;
                    const borderColor = isSelected
                        ? (strategy.color === 'purple' ? 'border-purple-500' : 'border-blue-500')
                        : 'border-gray-700';
                    const bgColor = isSelected
                        ? (strategy.color === 'purple' ? 'bg-purple-900/20' : 'bg-blue-900/10')
                        : 'bg-gray-800';

                    return (
                        <div
                            key={strategy.id}
                            onClick={() => setConfig({ ...config, strategy: strategy.id })}
                            className={`p-6 rounded-xl border-l-4 ${borderColor} ${bgColor} cursor-pointer transition-all duration-300 relative overflow-hidden`}
                        >
                            {isSelected && (
                                <div className={`absolute top-0 right-0 p-2 text-xs font-bold text-white uppercase rounded-bl-lg
                                    ${strategy.color === 'purple' ? 'bg-purple-600' : 'bg-blue-600'}`}>
                                    Selected
                                </div>
                            )}
                            <div className="flex items-start">
                                <span className="text-4xl mr-4">{strategy.icon}</span>
                                <div>
                                    <h3 className="text-xl font-bold text-gray-100">{strategy.label}</h3>
                                    <p className="text-gray-400 mt-1">{strategy.desc}</p>

                                    {strategy.personas.length > 0 && (
                                        <div className="flex mt-3 space-x-2">
                                            {strategy.personas.map(p => (
                                                <span key={p} className="text-xs px-2 py-1 rounded bg-gray-900 border border-gray-600 text-gray-300 uppercase font-mono">
                                                    {p}
                                                </span>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
};

export default StepStrategy;
