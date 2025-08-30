import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import YantraDashboard from './pages/YantraDashboard'
import './App.css'

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<YantraDashboard />} />
          <Route path="/dashboard" element={<YantraDashboard />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App