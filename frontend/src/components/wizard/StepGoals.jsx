// src/components/wizard/StepGoals.jsx
import React from 'react';

const StepGoals = ({ config, setConfig }) => {
    const goals = [
        { id: 'short_term', label: 'Short-term Gains', desc: 'Aggressive trading for quick profits', icon: '⚡' },
        { id: 'long_term', label: 'Long-term Wealth', desc: 'Steady compounding over years', icon: '🌳' },
        { id: 'passive', label: 'Passive Income', desc: 'Dividend and yield focused', icon: '💸' },
        { id: 'speculative', label: 'Speculative (Degen)', desc: 'High risk bets on moonshots', icon: '🚀' }
    ];

    const toggleGoal = (id) => {
        const current = config.goals || [];
        const updated = current.includes(id)
            ? current.filter(g => g !== id)
            : [...current, id];
        setConfig({ ...config, goals: updated });
    };

    return (
        <div className="animate-fade-in-up">
            <h2 className="text-2xl font-bold text-gray-100 mb-2">What are your investment goals?</h2>
            <p className="text-gray-400 mb-8">Select all that apply to your vision.</p>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {goals.map(goal => (
                    <div
                        key={goal.id}
                        onClick={() => toggleGoal(goal.id)}
                        className={`p-6 rounded-xl border border-gray-700 cursor-pointer transition-all duration-300 group
                            ${config.goals?.includes(goal.id)
                                ? 'bg-blue-900/20 border-blue-500 shadow-blue-500/20 shadow-lg'
                                : 'bg-gray-800 hover:bg-gray-750 hover:border-gray-600'}`}
                    >
                        <div className="flex items-center justify-between mb-2">
                            <span className="text-3xl">{goal.icon}</span>
                            <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center
                                ${config.goals?.includes(goal.id) ? 'border-blue-500 bg-blue-500' : 'border-gray-600'}`}>
                                {config.goals?.includes(goal.id) && <span className="text-white text-xs">✓</span>}
                            </div>
                        </div>
                        <h3 className={`text-lg font-semibold ${config.goals?.includes(goal.id) ? 'text-blue-400' : 'text-gray-200'}`}>
                            {goal.label}
                        </h3>
                        <p className="text-sm text-gray-400 mt-1">{goal.desc}</p>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default StepGoals;
