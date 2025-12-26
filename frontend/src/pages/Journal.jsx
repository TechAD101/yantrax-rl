// src/pages/Journal.jsx
import React from 'react';
import JournalEntry from '../components/journal/JournalEntry';

export default function Journal() {
  return (
    <div className="min-h-screen bg-black text-white p-6 md:p-12 bg-grid-pattern">
      <div className="absolute inset-0 bg-gradient-to-b from-gray-900/50 to-black pointer-events-none" />
      <div className="relative z-10">
        <JournalEntry />
      </div>
    </div>
  );
}
