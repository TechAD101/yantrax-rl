import React, { useEffect, useState } from 'react'
import { getJournal } from '../api/api'

export default function JournalViewer () {
  const [entries, setEntries] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    let mounted = true
    const load = async () => {
      try {
        const j = await getJournal()
        if (!mounted) return
        setEntries(Array.isArray(j) ? j : [])
      } catch (e) {
        if (!mounted) return
        setError(e.message || 'Failed to fetch journal')
      } finally {
        if (!mounted) return
        setLoading(false)
      }
    }
    load()
    return () => { mounted = false }
  }, [])

  if (loading) return <div className="p-4 text-gray-300">Loading journal...</div>
  if (error) return <div className="p-4 text-red-400">Error: {error}</div>

  return (
    <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
      <h2 className="text-lg font-semibold text-white mb-2">Trade Journal</h2>
      {entries.length === 0 && <div className="text-gray-400">No journal entries available.</div>}
      <ul className="space-y-2">
        {entries.map((entry, i) => (
          <li key={entry.id || i} className="bg-gray-900 p-3 rounded-md border border-gray-800">
            <div className="text-xs text-gray-400">{new Date(entry.timestamp).toLocaleString()}</div>
            <div className="text-sm text-blue-300 font-medium">Action: {entry.action}</div>
            <div className="text-sm">Reward: {entry.reward}</div>
            <div className="text-sm">Balance: {entry.balance}</div>
            <div className="text-sm text-gray-300">Notes: {entry.notes}</div>
          </li>
        ))}
      </ul>
    </div>
  )
}
