import React, { useState, useEffect } from 'react'
import { getMultiAssetData, getGodCycle } from '../api/api'
import AIAgentDashboard from '../components/AIAgentDashboard'
import LiveMarketData from '../components/LiveMarketData'
import TradingPerformanceChart from '../components/TradingPerformanceChart'
import JournalViewer from '../components/JournalViewer'
import CommentaryPanel from '../components/CommentaryPanel'

// Clean, minimal YantraDashboard component
export default function YantraDashboard () {
  const [marketData, setMarketData] = useState(null)
  const [aiData, setAiData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    let mounted = true
    const load = async () => {
      try {
        const m = await getMultiAssetData(['AAPL'])
        const g = await getGodCycle()
        if (!mounted) return
        setMarketData(m?.AAPL || { symbol: 'AAPL', price: 0 })
        setAiData(g || { signal: 'HOLD' })
        setLoading(false)
      } catch (e) {
        console.error(e)
        if (!mounted) return
        setError(e.message || 'load failed')
        setLoading(false)
      }
    }
    load()
    return () => { mounted = false }
  }, [])

  if (loading) return <div className="p-8 text-white">Loading YantraX dashboard...</div>
  if (error) return <div className="p-8 text-red-400">Error: {error}</div>

  return (
    <div className="p-6 text-white">
      <h1 className="text-2xl font-bold mb-4">YantraX Dashboard</h1>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <LiveMarketData marketData={marketData} loading={loading} />
        <AIAgentDashboard aiData={aiData} />
        <TradingPerformanceChart portfolioData={{}} aiData={aiData} loading={loading} />
      </div>

      <div className="mt-6 grid grid-cols-1 lg:grid-cols-2 gap-4">
        <JournalViewer />
        <CommentaryPanel />
      </div>
    </div>
  )
}