// src/components/journal/JournalInsights.jsx
import React from 'react';

const JournalInsights = () => {
    // Placeholder data
    const insights = [
        { title: 'Best Mood', value: '😎 Confident', desc: '+12% Win Rate', color: 'text-green-400' },
        { title: 'Worst Mood', value: '😤 Frustrated', desc: '-8% Win Rate', color: 'text-red-400' },
        { title: 'Top Prompt', value: 'Pre-Trade Analysis', desc: 'Most filled', color: 'text-blue-400' }
    ];

    return (
        <div className="w-full bg-gray-900 rounded-xl border border-gray-800 p-6">
            <h3 className="text-xl font-bold text-gray-100 mb-4 flex items-center">
                <span className="mr-2">📊</span> AI Emotional Insights
            </h3>

            <div className="grid grid-cols-3 gap-4 mb-6">
                {insights.map((item, idx) => (
                    <div key={idx} className="bg-gray-800/50 p-4 rounded-lg border border-gray-700">
                        <p className="text-xs text-gray-500 uppercase tracking-wide">{item.title}</p>
                        <p className={`text-lg font-bold mt-1 ${item.color}`}>{item.value}</p>
                        <p className="text-xs text-gray-400 mt-1">{item.desc}</p>
                    </div>
                ))}
            </div>

            <div className="h-32 bg-gray-800/30 rounded-lg flex items-center justify-center border border-gray-700/50 border-dashed">
                <p className="text-gray-500 text-sm">
                    Graph: Mood vs ROI Correlation (Coming Soon)
                </p>
            </div>
        </div>
    );
};

export default JournalInsights;
