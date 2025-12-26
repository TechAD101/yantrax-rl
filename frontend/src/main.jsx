import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App.jsx'
import './index.css'

// Prevent console.error from breaking the app
const originalError = console.error
console.error = function(...args) {
  try {
    // Try to stringify complex objects safely
    const safeArgs = args.map(arg => {
      if (typeof arg === 'object' && arg !== null) {
        try {
          return JSON.stringify(arg)
        } catch (e) {
          return String(arg)
        }
      }
      return arg
    })
    originalError.apply(console, safeArgs)
  } catch (e) {
    // Silently fail if we can't log
    try {
      originalError('Error logging failed:', e.message)
    } catch (e2) {
      // Give up
    }
  }
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>,
)