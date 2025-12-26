// src/components/journal/MoodSelector.jsx
import React from 'react';

const MoodSelector = ({ selectedMood, onSelect }) => {
    const moods = [
        { id: 'confident', label: 'Confident', emoji: '😎', color: 'text-green-400 group-hover:text-green-300' },
        { id: 'neutral', label: 'Neutral', emoji: '😐', color: 'text-blue-400 group-hover:text-blue-300' },
        { id: 'anxious', label: 'Anxious', emoji: '😰', color: 'text-yellow-400 group-hover:text-yellow-300' },
        { id: 'frustrated', label: 'Frustrated', emoji: '😤', color: 'text-red-400 group-hover:text-red-300' },
        { id: 'analytical', label: 'Analytical', emoji: '🧠', color: 'text-purple-400 group-hover:text-purple-300' }
    ];

    return (
        <div className="flex justify-between items-center bg-gray-900/50 p-4 rounded-xl border border-gray-700">
            {moods.map((mood) => (
                <button
                    key={mood.id}
                    onClick={() => onSelect(mood.id)}
                    className={`flex flex-col items-center p-3 rounded-lg transition-all duration-300 group hover:bg-gray-800
                        ${selectedMood === mood.id ? 'bg-gray-800 scale-110 shadow-lg ring-1 ring-gray-600' : 'opacity-70 hover:opacity-100'}`}
                >
                    <span className={`text-4xl mb-2 transition-transform duration-300 ${selectedMood === mood.id ? 'scale-125' : 'group-hover:scale-110'}`}>
                        {mood.emoji}
                    </span>
                    <span className={`text-xs font-semibold ${selectedMood === mood.id ? 'text-white' : 'text-gray-500'}`}>
                        {mood.label}
                    </span>
                </button>
            ))}
        </div>
    );
};

export default MoodSelector;
