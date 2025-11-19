import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import YantraDashboard from './pages/YantraDashboard'
import Journal from './pages/Journal'
import Onboarding from './pages/Onboarding'
import Moodboard from './pages/Moodboard'
import Settings from './pages/Settings'
import './App.css'

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<YantraDashboard />} />
          <Route path="/dashboard" element={<YantraDashboard />} />
          <Route path="/journal" element={<Journal />} />
          <Route path="/onboarding" element={<Onboarding />} />
          <Route path="/moodboard" element={<Moodboard />} />
          <Route path="/settings" element={<Settings />} />
          {/* Fallback route: render dashboard for unknown paths to support SPA deep links */}
          <Route path="*" element={<YantraDashboard />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App