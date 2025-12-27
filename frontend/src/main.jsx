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

// Global error handlers to make failures visible in UI and console
window.addEventListener('error', (evt) => {
  // eslint-disable-next-line no-console
  console.error('Uncaught error:', evt.error || evt.message || evt)
})
window.addEventListener('unhandledrejection', (evt) => {
  // eslint-disable-next-line no-console
  console.error('Unhandled promise rejection:', evt.reason || evt)
})

import ErrorBoundary from './ErrorBoundary'
import { BASE_URL } from './api/api'

// Expose resolved BASE_URL for runtime debugging
try { window.__YANTRAX_BASE_URL = BASE_URL } catch (e) {}

window.addEventListener('unhandledrejection', (evt) => {
  try {
    const r = evt.reason
    if (r == null) console.error('Unhandled rejection with no reason')
    else if (typeof r === 'object' && typeof r.then === 'function') console.error('Unhandled rejection: Promise/Thenable thrown', r)
    else console.error('Unhandled rejection reason:', r)
  } catch (e) {
    console.error('Unhandled rejection handler failed', e)
  }
})

try {
  ReactDOM.createRoot(document.getElementById('root')).render(
    <React.StrictMode>
      <ErrorBoundary>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </ErrorBoundary>
    </React.StrictMode>,
  )
} catch (err) {
  // If React fails to bootstrap (module evaluation, runtime syntax error, etc.)
  // render a minimal error message directly into the document so it's visible
  // even if React cannot mount.
  try {
    console.error('Fatal render error:', err)
    document.body.innerHTML = `
      <div style="padding:24px;background:#0b1220;color:#fff;min-height:100vh;">
        <h1 style="color:#ff6b6b;">Fatal startup error</h1>
        <pre style="white-space:pre-wrap;color:#ddd;">${String(err && (err.stack || err.message || err))}</pre>
      </div>
    `
  } catch (e) {
    // ignore
  }
}
