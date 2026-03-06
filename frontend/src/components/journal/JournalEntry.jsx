import React, { useState, useEffect } from 'react';
import MoodSelector from './MoodSelector';
import JournalInsights from './JournalInsights';
import { getJournalEntries } from '../../api/api';

const JournalEntry = () => {
    const [mood, setMood] = useState('neutral');
    const [entry, setEntry] = useState('');
    const [prompt, setPrompt] = useState('');
    const [saved, setSaved] = useState(false);
    const [recentEntries, setRecentEntries] = useState([]);
    const [stats, setStats] = useState({ total: 0, winRate: 0, avgConfidence: 0 });

    const prompts = [
        "What was your emotional state before your last trade?",
        "Did you follow your trading plan today? Why or why not?",
        "What is one thing you learned from the market today?",
        "How did you handle the volatility in the opening hour?"
    ];

    useEffect(() => {
        // Rotate prompt daily (mock random for now)
        setPrompt(prompts[Math.floor(Math.random() * prompts.length)]);

        const fetchEntries = async () => {
            try {
                const data = await getJournalEntries(20); // Fetch recent entries for stats
                const entries = Array.isArray(data) ? data : (data.entries || []);

                if (entries.length > 0) {
                    setRecentEntries(entries.slice(0, 5));

                    const total = entries.length;
                    const wins = entries.filter(e => (e.reward || 0) > 0).length;
                    const winRate = total > 0 ? Math.round((wins / total) * 100) : 0;

                    const totalConfidence = entries.reduce((acc, e) => acc + (e.confidence || 0), 0);
                    let avgConf = total > 0 ? (totalConfidence / total) : 0;
                    if (avgConf <= 1 && avgConf > 0) avgConf *= 100;

                    setStats({
                        total,
                        winRate,
                        avgConfidence: Math.round(avgConf)
                    });
                }
            } catch (error) {
                console.error("Failed to fetch journal entries:", error);
            }
        };
        fetchEntries();
    }, []);

    const handleSubmit = () => {
        if (!entry.trim()) return;

        console.log('Submitting Journal Entry:', {
            date: new Date().toISOString(),
            mood,
            entry,
            prompt
        });

        // TODO: Implement backend persistence for journal entries

        setSaved(true);
        setTimeout(() => setSaved(false), 3000);
        // Reset entry if needed, or keep for edit
        setEntry(''); // clear for next
    };

    // Helper to format date
    const formatDate = (dateString) => {
        if (!dateString) return '';
        const date = new Date(dateString);
        const now = new Date();
        const diffTime = Math.abs(now - date);
        const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));

        if (diffDays === 0) return 'Today';
        if (diffDays === 1) return 'Yesterday';
        if (diffDays < 7) return `${diffDays} day(s) ago`;
        return date.toLocaleDateString();
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

                    {/* Quick Stats & Previous Entries Preview */}
                    <div className="bg-gray-900 rounded-xl p-6 border border-gray-800">
                        {/* Quick Stats Header */}
                        <div className="flex justify-between items-center mb-6 pb-4 border-b border-gray-800">
                           <div className="text-center">
                                <p className="text-xs text-gray-500 uppercase">Entries</p>
                                <p className="text-xl font-bold text-white">{stats.total}</p>
                           </div>
                           <div className="text-center">
                                <p className="text-xs text-gray-500 uppercase">Win Rate</p>
                                <p className="text-xl font-bold text-green-400">{stats.winRate}%</p>
                           </div>
                           <div className="text-center">
                                <p className="text-xs text-gray-500 uppercase">Conf.</p>
                                <p className="text-xl font-bold text-blue-400">{stats.avgConfidence}%</p>
                           </div>
                        </div>

                        <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wider mb-4">Recent Entries</h3>

                        {recentEntries.length === 0 ? (
                            <div className="text-center py-4 text-gray-500 text-sm">
                                No entries yet. Start writing!
                            </div>
                        ) : (
                            <div className="space-y-4">
                                {recentEntries.map((e, i) => (
                                    <div key={e.id || i} className="border-b border-gray-800 pb-3 last:border-0 last:pb-0">
                                        <div className="flex justify-between text-xs text-gray-500 mb-1">
                                            <span>{formatDate(e.timestamp)}</span>
                                            {/* Action or Confidence as proxy for mood */}
                                            <span className={e.action === 'BUY' ? 'text-green-400' : (e.action === 'SELL' ? 'text-red-400' : 'text-gray-400')}>
                                                {e.action || 'ENTRY'} {(e.confidence || 0) > 0.8 ? '🔥' : ''}
                                            </span>
                                        </div>
                                        <p className="text-gray-300 text-sm truncate">
                                            {e.notes || (e.symbol ? `${e.symbol} Trade` : 'Journal Entry')}
                                        </p>
                                    </div>
                                ))}
                            </div>
                        )}

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
