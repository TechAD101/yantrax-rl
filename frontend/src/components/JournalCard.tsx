import React from 'react'

interface Props {
  timestamp: string
  signal: string
  audit: string
  reward: number
}

export default function JournalCard({ timestamp, signal, audit, reward }: Props) {
  return (
    <div className="bg-white rounded-xl shadow p-4 hover:shadow-lg transition-all">
      <p className="text-sm text-gray-500">{new Date(timestamp).toLocaleString()}</p>
      <p className="text-xl font-semibold mt-2">{signal}</p>
      <p className="text-md text-blue-600">{audit}</p>
      <p className={`text-md font-bold ${reward >= 0 ? 'text-green-600' : 'text-red-500'}`}>
        Reward: {reward}
      </p>
    </div>
  )
}
