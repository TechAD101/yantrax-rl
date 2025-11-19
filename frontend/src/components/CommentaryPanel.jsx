import React, { useEffect, useState } from 'react'
import { getCommentary } from '../api/api'
import CommentaryCard from './CommentaryCard'

export default function CommentaryPanel () {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    let mounted = true
    const load = async () => {
      try {
        const data = await getCommentary()
        if (!mounted) return
        setItems(Array.isArray(data) ? data : [])
      } catch (e) {
        if (!mounted) return
        setError(e.message || 'Failed to fetch commentary')
      } finally {
        if (!mounted) return
        setLoading(false)
      }
    }
    load()
    return () => { mounted = false }
  }, [])

  if (loading) return <div className="p-4 text-gray-300">Loading commentary...</div>
  if (error) return <div className="p-4 text-red-400">Error: {error}</div>

  return (
    <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
      <h2 className="text-lg font-semibold text-white mb-2">AI Commentary</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {items.map((c) => (
          <CommentaryCard key={c.id || c.timestamp} agent={c.agent} comment={c.comment} timestamp={c.timestamp} />
        ))}
      </div>
    </div>
  )
}
