import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App.jsx'
import './index.css'

// Override console methods to prevent crashes from complex objects
const originalConsoleError = console.error
const originalConsoleWarn = console.warn

const safeLog = (fn, ...args) => {
  try {
    const safeArgs = args.map(arg => {
      if (arg === null) return 'null'
      if (arg === undefined) return 'undefined'
      if (typeof arg === 'string') return arg
      if (typeof arg === 'number' || typeof arg === 'boolean') return String(arg)
      if (typeof arg === 'object') {
        try {
          return JSON.stringify(arg)
        } catch (e) {
          return '[Circular or Complex Object]'
        }
      }
      return String(arg)
    })
    fn(...safeArgs)
  } catch (e) {
    // Silently fail - don't let logging break the app
  }
}

console.error = (...args) => safeLog(originalConsoleError, ...args)
console.warn = (...args) => safeLog(originalConsoleWarn, ...args)

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>,
)