import React from 'react'

function serializeError(err) {
  try {
    if (err == null) return String(err)
    if (typeof err === 'string') return err
    if (typeof err === 'object') {
      // If it's a Promise or thenable, indicate that
      if (typeof err.then === 'function') return '[Thrown a Promise/Thenable]'

      // Collect own string/symbol keys
      const names = Object.getOwnPropertyNames(err)
      const syms = Object.getOwnPropertySymbols(err)
      const hasOwn = names.length > 0 || syms.length > 0

      // If there are own properties, try to show them
      if (hasOwn) {
        const obj = {}
        names.forEach((k) => {
          try { obj[k] = err[k] } catch (e) { obj[k] = `unserializable (${e.message})` }
        })
        syms.forEach((s) => {
          try { obj[s.toString()] = err[s] } catch (e) { obj[s.toString()] = `unserializable (${e.message})` }
        })
        if (obj.message || obj.stack) {
          return `${obj.message || ''}\n${obj.stack || ''}`.trim()
        }
        return JSON.stringify(obj, null, 2)
      }

      // No own properties — it's an empty object or something with hidden props
      const proto = Object.getPrototypeOf(err)
      const ctor = err && err.constructor ? err.constructor.name : '(unknown)'
      let toStr = '(toString failed)'
      try { toStr = String(err) } catch (e) { toStr = `toString failed: ${e.message}` }
      let valueOf = '(valueOf failed)'
      try { valueOf = typeof err.valueOf === 'function' ? String(err.valueOf()) : '(no valueOf)' } catch (e) { valueOf = `valueOf threw: ${e.message}` }

      return `Thrown object (no own props)\nconstructor: ${ctor}\nprototype: ${proto && proto.constructor ? proto.constructor.name : String(proto)}\nvalueOf: ${valueOf}\ntoString: ${toStr}\nownKeys: ${JSON.stringify(names.concat(syms.map(s=>s.toString())), null, 2)}`
    }
    return String(err)
  } catch (e) {
    return `Could not serialize error: ${e && e.message ? e.message : String(e)}`
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
      // Provide an expanded debug dump to help with minified/opaque thrown values
      const details = {
        constructor: error && error.constructor ? error.constructor.name : '(unknown)',
        ownKeys: typeof Reflect !== 'undefined' ? Reflect.ownKeys(error || {}) : Object.getOwnPropertyNames(error || {}),
        prototype: Object.getPrototypeOf(error),
        serialized: serializeError(error),
        componentStack: info?.componentStack
      }
      // eslint-disable-next-line no-console
      console.error('Captured error (detailed):', details)
    } catch (e) {
      try { console.error('Captured error, but failed to dump details', e) } catch (er) {}
    }
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
                <button onClick={() => {
                  try {
                    const debugPayload = {
                      serialized,
                      componentStack,
                      constructor: error && error.constructor ? error.constructor.name : '(unknown)',
                      ownKeys: typeof Reflect !== 'undefined' ? Reflect.ownKeys(error || {}) : Object.getOwnPropertyNames(error || {}),
                      prototype: Object.getPrototypeOf(error)
                    }
                    navigator.clipboard?.writeText(serialized + '\n\n' + componentStack + '\n\n' + JSON.stringify(debugPayload, null, 2))
                  } catch (e) {
                    try { navigator.clipboard?.writeText(serialized + '\n\n' + componentStack) } catch (er) {}
                  }
                }} style={{ marginLeft: 8, padding: '8px 12px', borderRadius: 6, background: '#334155', border: 'none', color: '#fff' }}>Copy Debug Info</button>
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
