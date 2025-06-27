import React, { useEffect, useState } from 'react'
import JournalCard from './components/JournalCard'

interface Entry {
  timestamp: string
  signal: string
  audit: string
  reward: number
}

export default function App() {
  const [entries, setEntries] = useState<Entry[]>([])

  useEffect(() => {
    fetch('http://127.0.0.1:5000/replay')
      .then(res => res.json())
      .then(data => setEntries(data.replay.reverse()))
      .catch(err => console.error('Failed to fetch:', err))
  }, [])

  return (
    <div className="min-h-screen p-6 bg-gray-100">
      <h1 className="text-3xl font-bold mb-6">Yantra X Trading Journal</h1>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {entries.map((entry, idx) => (
          <JournalCard key={idx} {...entry} />
        ))}
      </div>
    </div>
  )
}
