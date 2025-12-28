import React from 'react'

export default function withDebug(name, Component) {
  function Wrapped(props) {
    try {
      return <Component {...props} />
    } catch (e) {
      // Throw a new Error with component context while preserving original stack
      const err = new Error(`[${name}] ${e && e.message ? e.message : String(e)}`)
      // Attempt to preserve stack for easier mapping
      try { err.stack = (e && e.stack) ? `${err.message}\nOriginal stack:\n${e.stack}` : err.stack } catch (ex) {}
      // Log detailed info to console for remote debugging
      try { console.error(`Error in component ${name}:`, { original: e, annotated: err }) } catch (ex) {}
      throw err
    }
  }
  Wrapped.displayName = `WithDebug(${name})`
  return Wrapped
}
