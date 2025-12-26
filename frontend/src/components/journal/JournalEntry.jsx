// src/components/journal/JournalEntry.jsx
import React, { useState, useEffect } from 'react';
import MoodSelector from './MoodSelector';
import JournalInsights from './JournalInsights';

const JournalEntry = () => {
    const [mood, setMood] = useState('neutral');
    const [entry, setEntry] = useState('');
    const [prompt, setPrompt] = useState('');
    const [saved, setSaved] = useState(false);

    const prompts = [
        "What was your emotional state before your last trade?",
        "Did you follow your trading plan today? Why or why not?",
        "What is one thing you learned from the market today?",
        "How did you handle the volatility in the opening hour?"
    ];

    useEffect(() => {
        // Rotate prompt daily (mock random for now)
        setPrompt(prompts[Math.floor(Math.random() * prompts.length)]);
    }, []);

    const handleSubmit = () => {
        if (!entry.trim()) return;

        console.log('Submitting Journal Entry:', {
            date: new Date().toISOString(),
            mood,
            entry,
            prompt
        });

        setSaved(true);
        setTimeout(() => setSaved(false), 3000);
        // Reset entry if needed, or keep for edit
        setEntry(''); // clear for next
    };

    return (
        <div className="max-w-4xl mx-auto space-y-6">
            {/* Header Section */}
            <div className="flex justify-between items-end">
                <div>
                    <h1 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-green-400">
                        Trader's Journal
                    </h1>
                    <p className="text-gray-400 text-sm mt-1">
                        Track your psychology, master your execution.
                    </p>
                </div>
                <div className="text-right">
                    <p className="text-gray-500 text-xs uppercase font-mono tracking-widest">Today</p>
                    <p className="text-white font-mono text-lg">
                        {new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' })}
                    </p>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* Main Entry Column */}
                <div className="md:col-span-2 space-y-6">
                    {/* Mood Section */}
                    <div className="bg-gray-900 rounded-xl p-6 border border-gray-800 shadow-lg">
                        <h2 className="text-lg font-semibold text-gray-200 mb-4">How are you feeling right now?</h2>
                        <MoodSelector selectedMood={mood} onSelect={setMood} />
                    </div>

                    {/* Writing Section */}
                    <div className="bg-gray-900 rounded-xl p-6 border border-gray-800 shadow-lg relative">
                        <div className="mb-4 bg-blue-900/20 border-l-4 border-blue-500 p-4 rounded-r-lg">
                            <p className="text-xs text-blue-400 uppercase font-bold mb-1">Daily Prompt</p>
                            <p className="text-gray-200 italic">"{prompt}"</p>
                        </div>

                        <textarea
                            className="w-full h-64 bg-gray-800 text-white p-4 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none resize-none placeholder-gray-600 font-sans leading-relaxed"
                            placeholder="Start writing here... (e.g. 'I felt FOMO when Nifty broke resistance...')"
                            value={entry}
                            onChange={(e) => setEntry(e.target.value)}
                        />

                        <div className="flex justify-end mt-4">
                            <button
                                onClick={handleSubmit}
                                disabled={!entry.trim()}
                                className={`px-6 py-2 rounded-lg font-semibold shadow-lg transition-all
                                    ${saved
                                        ? 'bg-green-600 text-white cursor-default'
                                        : 'bg-blue-600 hover:bg-blue-500 text-white hover:scale-105 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed'}`}
                            >
                                {saved ? 'Saved ✓' : 'Save Entry'}
                            </button>
                        </div>
                    </div>
                </div>

                {/* Sidebar Column */}
                <div className="space-y-6">
                    <JournalInsights />

                    {/* Quick Stats or Previous Entries Preview could go here */}
                    <div className="bg-gray-900 rounded-xl p-6 border border-gray-800">
                        <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wider mb-4">Recent Entries</h3>
                        <div className="space-y-4">
                            {[1, 2, 3].map((d) => (
                                <div key={d} className="border-b border-gray-800 pb-3 last:border-0 last:pb-0">
                                    <div className="flex justify-between text-xs text-gray-500 mb-1">
                                        <span>{d} day(s) ago</span>
                                        <span>😐 Neutral</span>
                                    </div>
                                    <p className="text-gray-300 text-sm truncate">
                                        Market was choppy, stayed cash mostly...
                                    </p>
                                </div>
                            ))}
                        </div>
                        <button className="w-full mt-4 py-2 text-sm text-blue-400 hover:text-blue-300 border border-blue-900 hover:bg-blue-900/20 rounded-lg transition-colors">
                            View Archive
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default JournalEntry;
