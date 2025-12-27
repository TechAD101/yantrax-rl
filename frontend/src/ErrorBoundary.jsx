import React from 'react'

function serializeError(err) {
  try {
    if (err == null) return String(err)
    if (typeof err === 'string') return err
    if (typeof err === 'object') {
      // If it's a Promise or thenable, indicate that
      if (typeof err.then === 'function') return '[Thrown a Promise/Thenable]'
      // Attempt to stringify useful properties
      const obj = {}
      Object.getOwnPropertyNames(err).forEach((k) => {
        try { obj[k] = err[k] } catch (e) { obj[k] = `unserializable (${e.message})` }
      })
      if (obj.message || obj.stack) {
        return `${obj.message || ''}\n${obj.stack || ''}`.trim()
      }
      return JSON.stringify(obj, null, 2)
    }
    return String(err)
  } catch (e) {
    return `Could not serialize error: ${e.message}`
  }
}

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = { error: null, info: null }
  }

  componentDidCatch(error, info) {
    // Preserve original behavior but make it visible in UI
    this.setState({ error, info })
    try {
      // Keep normal logging as well
      // eslint-disable-next-line no-console
      console.error('Captured error:', error, info)
    } catch (e) {}
  }

  render() {
    if (this.state.error) {
      const { error, info } = this.state
      const serialized = serializeError(error)
      const componentStack = info?.componentStack || '(no component stack available)'

      return (
        <div style={{ padding: 20, background: '#071021', color: '#fff', minHeight: '100vh', fontFamily: 'system-ui, sans-serif' }}>
          <div style={{ display: 'flex', gap: 12 }}>
            <div style={{ flex: 1 }}>
              <h1 style={{ color: '#ff6b6b', margin: 0 }}>An error occurred</h1>
              <p style={{ color: '#ddd', marginTop: 6, marginBottom: 12 }}>The application has encountered an error. Details are shown below for debugging.</p>

              <div style={{ background: '#001029', padding: 12, borderRadius: 6, color: '#fff' }}>
                <div style={{ fontSize: 13, marginBottom: 8, color: '#9bb7d7' }}>Error</div>
                <pre style={{ whiteSpace: 'pre-wrap', fontSize: 12, color: '#ffdede' }}>{serialized}</pre>
              </div>

              <div style={{ marginTop: 12, background: '#001029', padding: 12, borderRadius: 6 }}>
                <div style={{ fontSize: 13, marginBottom: 8, color: '#9bb7d7' }}>Component stack</div>
                <pre style={{ whiteSpace: 'pre-wrap', fontSize: 12, color: '#cfe8ff' }}>{componentStack}</pre>
              </div>

              <div style={{ marginTop: 12 }}>
                <button onClick={() => { window.location.reload() }} style={{ padding: '8px 12px', borderRadius: 6, background: '#0ea5a3', border: 'none', color: '#00363a' }}>Reload</button>
                <button onClick={() => { navigator.clipboard?.writeText(serialized + '\n\n' + componentStack) }} style={{ marginLeft: 8, padding: '8px 12px', borderRadius: 6, background: '#334155', border: 'none', color: '#fff' }}>Copy Debug Info</button>
              </div>
            </div>

            <aside style={{ width: 320 }}>
              <div style={{ background: '#001029', padding: 12, borderRadius: 6 }}>
                <div style={{ fontSize: 13, marginBottom: 8, color: '#9bb7d7' }}>Env</div>
                <div style={{ fontSize: 12, color: '#cfe8ff' }}>BASE_URL: {typeof window !== 'undefined' && window.__YANTRAX_BASE_URL ? window.__YANTRAX_BASE_URL : '(unknown)'}</div>
                <div style={{ fontSize: 12, color: '#cfe8ff', marginTop: 8 }}>User Agent: {typeof navigator !== 'undefined' ? navigator.userAgent : ''}</div>
              </div>
            </aside>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}
