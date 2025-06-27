// src/pages/YantraDashboard.tsx
import React, { useEffect, useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

interface JournalEntry {
  timestamp: string;
  signal: string;
  audit: string;
  reward: number;
}

const YantraDashboard = () => {
  const [entries, setEntries] = useState<JournalEntry[]>([]);

  useEffect(() => {
    fetch('http://127.0.0.1:5000/replay')
      .then((res) => res.json())
      .then((data) => {
        setEntries(data.replay.reverse()); // show latest first
      })
      .catch((err) => console.error('Replay fetch error:', err));
  }, []);

  return (
    <div className="min-h-screen bg-gray-950 text-white p-6">
      <h1 className="text-3xl font-bold mb-4">🧠 Yantra X AI Journal</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {entries.map((entry, index) => (
          <Card key={index} className="bg-gray-900 border border-gray-700 rounded-2xl shadow-md">
            <CardContent className="p-4">
              <div className="flex justify-between items-center mb-2">
                <Badge className="text-xs" variant="secondary">
                  {new Date(entry.timestamp).toLocaleString()}
                </Badge>
                <span
                  className={`text-sm font-bold ${
                    entry.reward > 0 ? 'text-green-400' : entry.reward < 0 ? 'text-red-400' : 'text-yellow-400'
                  }`}
                >
                  {entry.reward > 0 ? '📈 Profit' : entry.reward < 0 ? '📉 Loss' : '⏸ Neutral'}
                </span>
              </div>
              <p className="text-lg mb-1">
                Signal: <span className="font-semibold">{entry.signal}</span>
              </p>
              <p className="text-sm text-gray-400">Audit: {entry.audit}</p>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default YantraDashboard;
