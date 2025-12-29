import React, { useState, useEffect } from 'react';
import MarketMoodDial from '../components/MarketMoodDial';
import HypeHeatMap from '../components/mood/HypeHeatMap';
import MoodCompass from '../components/mood/MoodCompass';
import TopSignals from '../components/mood/TopSignals';
import { BASE_URL } from '../api/api';

export default function Moodboard() {
  const [moodData, setMoodData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMood = async () => {
      try {
        const resp = await fetch(`${BASE_URL}/api/ai-firm/status`);
        if (resp.ok) {
          const data = await resp.json();
          setMoodData(data.system_performance);
        }
      } catch (e) {
        console.error('Mood fetch failed', e);
      } finally {
        setLoading(false);
      }
    };
    fetchMood();
  }, []);

  return (
    <div className="min-h-screen bg-black text-white p-6 md:p-8 bg-grid-pattern overflow-x-hidden">
      <div className="absolute inset-0 bg-gradient-to-br from-indigo-900/10 to-purple-900/10 pointer-events-none" />

      <div className="relative z-10 max-w-7xl mx-auto space-y-8">
        <header className="mb-8">
          <h1 className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-pink-500 to-purple-500">
            Market Sentiment Engine
          </h1>
          <p className="text-gray-400 mt-2">Real-time quantification of institutional vs retail psychology.</p>
        </header>

        {/* Top Row: Dial and Compass */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1">
            <MarketMoodDial mood={moodData?.market_mood || 'neutral'} />
          </div>
          <div className="lg:col-span-2">
            <HypeHeatMap />
          </div>
        </div>

        {/* Bottom Row: Compass and Signals */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1">
            <MoodCompass />
          </div>
          <div className="lg:col-span-2">
            <TopSignals />
          </div>
        </div>
      </div>
    </div>
  );
}
