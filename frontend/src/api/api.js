// YantraX API Client - consolidated and robust
// Resolve backend BASE URL from Vite env var or process env fallbacks
const API_BASE_URL = (typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.VITE_API_URL)
  ? import.meta.env.VITE_API_URL
  : (process.env.VITE_API_URL || process.env.REACT_APP_API_URL || 'https://yantrax-backend.onrender.com');

const BASE_URL = API_BASE_URL;
export { BASE_URL };

const UPDATE_INTERVAL = 15000; // 15 seconds
const MAX_RETRIES = 3;
const RETRY_DELAY = 1000;

export const ERROR_TYPES = {
  NETWORK: 'NETWORK_ERROR',
  API: 'API_ERROR',
  TIMEOUT: 'TIMEOUT_ERROR'
};

// Retry logic with exponential backoff
const fetchWithRetry = async (url, options = {}, retries = MAX_RETRIES) => {
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      }
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    if (retries > 0) {
      await new Promise(resolve =>
        setTimeout(resolve, RETRY_DELAY * (MAX_RETRIES - retries + 1))
      );
      return fetchWithRetry(url, options, retries - 1);
    }
    throw error;
  }
};

// Core API object for simple calls
export const api = {
  getStatus: () => fetchWithRetry(`${BASE_URL}/`),
  getAiFirmStatus: () => fetchWithRetry(`${BASE_URL}/api/ai-firm/status`),
  getGodCycle: () => fetchWithRetry(`${BASE_URL}/god-cycle`),
  getMarketPrice: (symbol) => fetchWithRetry(`${BASE_URL}/market-price?symbol=${encodeURIComponent(symbol)}`),
  getPortfolio: () => fetchWithRetry(`${BASE_URL}/portfolio`),
  getTradingJournal: () => fetchWithRetry(`${BASE_URL}/journal`),
  getCommentary: () => fetchWithRetry(`${BASE_URL}/commentary`),
  runTradingCycle: () => fetchWithRetry(`${BASE_URL}/run-cycle`, { method: 'POST' })
};

// Real-time data subscription helper
export const subscribeToUpdates = (endpoint, callback, interval = UPDATE_INTERVAL) => {
  const fn = () => {
    if (typeof api[endpoint] !== 'function') {
      console.error(`subscribeToUpdates: endpoint ${endpoint} not found`);
      return;
    }
    api[endpoint]()
      .then(callback)
      .catch(error => console.error(`Update error (${endpoint}):`, error));
  };

  fn();
  const timer = setInterval(fn, interval);
  return () => clearInterval(timer);
};

// Export default for compatibility
export default api;

// Additional utilities
export const getMultiAssetData = async (symbols = ["AAPL", "MSFT", "GOOGL", "TSLA"]) => {
  try {
    const promises = symbols.map(symbol =>
      fetch(`${BASE_URL}/market-price?symbol=${encodeURIComponent(symbol)}&analysis=true`).then(r => r.json()).catch(e => ({ symbol, error: e.message }))
    );
    const results = await Promise.all(promises);
    return results.reduce((acc, res) => { if (!res.error && res.symbol) acc[res.symbol] = res; return acc }, {});
  } catch (e) {
    console.error('Multi-asset data fetch failed:', e);
    return {};
  }
};

export const runAdvancedRLCycle = async (config = {}) => {
  try {
    const resp = await fetch(`${BASE_URL}/run-cycle`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ symbol: config.symbol || 'AAPL', strategy_weights: config.strategyWeights || {}, risk_parameters: config.riskParams || {} })
    });
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    return await resp.json();
  } catch (e) {
    console.error('Advanced RL cycle failed:', e);
    throw e;
  }
};

export const getJournal = async () => {
  try {
    const r = await fetch(`${BASE_URL}/journal`);
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    const data = await r.json();
    return Array.isArray(data) ? data : data.entries || [];
  } catch (e) {
    console.error('Journal fetch failed:', e);
    return [];
  }
};

export const getCommentary = async () => {
  try {
    const r = await fetch(`${BASE_URL}/commentary`);
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    const data = await r.json();
    return Array.isArray(data) ? data : data.commentary || [];
  } catch (e) {
    console.error('Commentary fetch failed:', e);
    return [];
  }
};

export const runRLCycle = async (config = {}) => {
  try {
    const response = await fetch(`${BASE_URL}/god-cycle`);
    if (!response.ok) return await runAdvancedRLCycle(config);
    return await response.json();
  } catch (e) {
    console.error('RL cycle failed:', e);
    throw new Error(`RL cycle request failed: ${e.message}`);
  }
};

export const getGodCycle = async () => {
  try {
    const r = await fetch(`${BASE_URL}/god-cycle`);
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    return await r.json();
  } catch (e) {
    console.error('God cycle failed:', e);
    throw e;
  }
};

export const getMarketPrice = async (symbol = 'AAPL') => {
  try {
    const r = await fetch(`${BASE_URL}/market-price?symbol=${encodeURIComponent(symbol)}`);
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    return await r.json();
  } catch (e) {
    console.error(`Market price fetch failed for ${symbol}:`, e);
    return { symbol, price: null, error: e.message };
  }
};

export const streamMarketPrice = ({ symbol = 'AAPL', interval = 5, count = 0, onMessage = null, onOpen = null, onError = null } = {}) => {
  if (!symbol) throw new Error('streamMarketPrice requires a symbol');
  const normalizedBase = (BASE_URL || '').replace(/\/$/, '');
  const url = `${normalizedBase}/market-price-stream?symbol=${encodeURIComponent(symbol)}&interval=${encodeURIComponent(interval)}&count=${encodeURIComponent(count)}`;
  let es;
  try { es = new EventSource(url) } catch (err) { if (typeof onError === 'function') onError(err); throw err }
  es.onopen = (evt) => { if (typeof onOpen === 'function') onOpen(evt) }
  es.onmessage = (evt) => { try { const payload = JSON.parse(evt.data); if (typeof onMessage === 'function') onMessage(payload) } catch (err) { if (typeof onError === 'function') onError(err); console.error('streamMarketPrice JSON parse error', err) } }
  es.onerror = (evt) => { if (typeof onError === 'function') onError(evt) }
  return { close: () => { try { es.close() } catch (e) {} } }
};

export const testConnection = async () => {
  try {
    console.log('Testing connection to:', BASE_URL);
    const r = await fetch(`${BASE_URL}/health`);
    const data = await r.json();
    console.log('Backend health check:', data);
    return { connected: true, ...data };
  } catch (e) {
    console.error('Connection test failed:', e);
    return { connected: false, error: e.message };
  }
};
const MAX_RETRIES = 3;
const RETRY_DELAY = 1000;

export const ERROR_TYPES = {
  NETWORK: 'NETWORK_ERROR',
  API: 'API_ERROR',
  TIMEOUT: 'TIMEOUT_ERROR'
};

// Retry logic with exponential backoff
const fetchWithRetry = async (url, options = {}, retries = MAX_RETRIES) => {
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      }
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    if (retries > 0) {
      await new Promise(resolve =>
        setTimeout(resolve, RETRY_DELAY * (MAX_RETRIES - retries + 1))
      );
      return fetchWithRetry(url, options, retries - 1);
    }
    throw error;
  }
};

// --- API Methods ---

<<<<<<< HEAD
export const getStatus = () => fetchWithRetry(`${BASE_URL}/`);
=======
// Real-time data subscription
export const subscribeToUpdates = (endpoint, callback, interval = UPDATE_INTERVAL) => {
  const fetch = () => {
    api[endpoint]()
      .then(callback)
      .catch(error => console.error(`Update error (${endpoint}):`, error));
  };

  fetch(); // Initial fetch
  const timer = setInterval(fetch, interval);
  
  // Return cleanup function
  return () => clearInterval(timer);
};

export default api;
// src/api/api.js - Enhanced API with Multi-Asset Support
// Reuse the already-resolved API_BASE_URL so all code uses the same backend URL.
const BASE_URL = API_BASE_URL;

// Export BASE_URL so UI components can reuse the same resolved backend URL
export { BASE_URL };

// Enhanced market data fetching with multiple assets
export const getMultiAssetData = async (symbols = ["AAPL", "MSFT", "GOOGL", "TSLA"]) => {
  try {
    const promises = symbols.map(symbol => 
      fetch(`${BASE_URL}/market-price?symbol=${symbol}&analysis=true`)
        .then(res => res.json())
        .catch(err => ({ symbol, error: err.message }))
    );

    const results = await Promise.all(promises);
    return results.reduce((acc, result) => {
      if (!result.error) {
        acc[result.symbol] = result;
      }
      return acc;
    }, {});
  } catch (error) {
    console.error("Multi-asset data fetch failed:", error);
    return {};
  }
};

// Enhanced RL cycle with comprehensive data
export const runAdvancedRLCycle = async (config = {}) => {
  try {
    const response = await fetch(`${BASE_URL}/run-cycle`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        symbol: config.symbol || "AAPL",
        strategy_weights: config.strategyWeights || {},
        risk_parameters: config.riskParams || {}
      })
    });

    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error("Advanced RL cycle failed:", error);
    throw error;
  }
};

// Get comprehensive system health
export const getSystemHealth = async () => {
  try {
    const response = await fetch(`${BASE_URL}/health`);
    if (response.ok) {
      return await response.json();
    } else {
      // Fallback to basic health check
      const basicResponse = await fetch(`${BASE_URL}/`);
      return { 
        status: basicResponse.ok ? "healthy" : "degraded",
        services: { basic: "operational" }
      };
    }
  } catch (error) {
    return { status: "error", error: error.message };
  }
};

// Get advanced analytics
export const getAdvancedAnalytics = async () => {
  try {
    const [journal, commentary, marketStats] = await Promise.allSettled([
      getJournal(),
      getCommentary(), 
      fetch(`${BASE_URL}/market-stats?anomalies=true`).then(r => r.json())
    ]);

    return {
      trading: journal.status === 'fulfilled' ? journal.value : [],
      commentary: commentary.status === 'fulfilled' ? commentary.value : [],
      market: marketStats.status === 'fulfilled' ? marketStats.value : {}
    };
  } catch (error) {
    console.error("Advanced analytics fetch failed:", error);
    return { trading: [], commentary: [], market: {} };
  }
};

// Portfolio optimization endpoint
export const optimizePortfolio = async (assets, constraints = {}) => {
  try {
    const response = await fetch(`${BASE_URL}/optimize-portfolio`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ assets, constraints })
    });

    if (response.ok) {
      return await response.json();
    } else {
      // No mock fallback: signal failure to caller
      throw new Error(`Optimization API returned status ${response.status}`);
    }
  } catch (error) {
    console.error("Portfolio optimization failed:", error);
    return null;
  }
};

// Existing API functions (enhanced with better error handling)
export const getJournal = async () => {
  try {
    const response = await fetch(`${BASE_URL}/journal`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    return Array.isArray(data) ? data : data.entries || [];
  } catch (error) {
    console.error("Journal fetch failed:", error);
    return [];
  }
};

export const getCommentary = async () => {
  try {
    const response = await fetch(`${BASE_URL}/commentary`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    return Array.isArray(data) ? data : data.commentary || [];
  } catch (error) {
    console.error("Commentary fetch failed:", error);
    return [];
  }
};

// Enhanced RL cycle that uses god-cycle for better data
export const runRLCycle = async (config = {}) => {
  try {
    // Try god-cycle first for richer data
    const response = await fetch(`${BASE_URL}/god-cycle`);
    if (!response.ok) {
      // Fallback to regular run-cycle
      return await runAdvancedRLCycle(config);
    }
    return await response.json();
  } catch (error) {
    console.error("RL cycle failed:", error);
        throw new Error(`RL cycle request failed: ${error.message}`);
  }
};
>>>>>>> ec0225d (fix(frontend): add improved error boundary, expose BASE_URL, add render safeguards and better rejection logging)

export const getAiFirmStatus = () => fetchWithRetry(`${BASE_URL}/api/ai-firm/status`);
export const getGodCycle = async () => {
  try {
    const response = await fetch(`${BASE_URL}/god-cycle`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error("God cycle failed:", error);
    throw error;
  }
};

export const getMarketPrice = async (symbol = "AAPL") => {
  try {
    const response = await fetch(`${BASE_URL}/market-price?symbol=${symbol}`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error(`Market price fetch failed for ${symbol}:`, error);
    return { symbol, price: null, error: error.message };
  }
};

export const getPortfolio = () => fetchWithRetry(`${BASE_URL}/portfolio`);

export const getTradingJournal = () => fetchWithRetry(`${BASE_URL}/journal`);
export const getJournal = getTradingJournal; // Alias

export const getWarrenAnalysis = () => fetchWithRetry(`${BASE_URL}/api/ai-firm/personas/warren`);
export const getCathieAnalysis = () => fetchWithRetry(`${BASE_URL}/api/ai-firm/personas/cathie`);

export const getRiskMetrics = () => fetchWithRetry(`${BASE_URL}/risk-metrics`);
export const getPerformance = () => fetchWithRetry(`${BASE_URL}/performance`);

export const getCommentary = async () => {
  try {
    const response = await fetch(`${BASE_URL}/commentary`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    return Array.isArray(data) ? data : data.commentary || [];
  } catch (error) {
    console.error("Commentary fetch failed:", error);
    return [];
  }
};

export const runTradingCycle = () => fetchWithRetry(`${BASE_URL}/run-cycle`, { method: 'POST' });

// Enhanced RL cycle
export const runAdvancedRLCycle = async (config = {}) => {
  try {
    const response = await fetch(`${BASE_URL}/run-cycle`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        symbol: config.symbol || "AAPL",
        strategy_weights: config.strategyWeights || {},
        risk_parameters: config.riskParams || {}
      })
    });

    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error("Advanced RL cycle failed:", error);
    throw error;
  }
};

export const runRLCycle = async (config = {}) => {
  try {
    // Try god-cycle first for richer data
    const response = await fetch(`${BASE_URL}/god-cycle`);
    if (!response.ok) {
      return await runAdvancedRLCycle(config);
    }
    return await response.json();
  } catch (error) {
    console.error("RL cycle failed:", error);
    throw new Error(`RL cycle request failed: ${error.message}`);
  }
};

export const getMultiAssetData = async (symbols = ["AAPL", "MSFT", "GOOGL", "TSLA"]) => {
  try {
    const promises = symbols.map(symbol =>
      fetch(`${BASE_URL}/market-price?symbol=${symbol}&analysis=true`)
        .then(res => res.json())
        .catch(err => ({ symbol, error: err.message }))
    );

    const results = await Promise.all(promises);
    return results.reduce((acc, result) => {
      if (!result.error) {
        acc[result.symbol] = result;
      }
      return acc;
    }, {});
  } catch (error) {
    console.error("Multi-asset data fetch failed:", error);
    return {};
  }
};

export const getSystemHealth = async () => {
  try {
    const response = await fetch(`${BASE_URL}/health`);
    if (response.ok) {
      return await response.json();
    } else {
      const basicResponse = await fetch(`${BASE_URL}/`);
      return {
        status: basicResponse.ok ? "healthy" : "degraded",
        services: { basic: "operational" }
      };
    }
  } catch (error) {
    return { status: "error", error: error.message };
  }
};

export const getAdvancedAnalytics = async () => {
  try {
    const [journal, commentary, marketStats] = await Promise.allSettled([
      getJournal(),
      getCommentary(),
      fetch(`${BASE_URL}/market-stats?anomalies=true`).then(r => r.json())
    ]);

    return {
      trading: journal.status === 'fulfilled' ? journal.value : [],
      commentary: commentary.status === 'fulfilled' ? commentary.value : [],
      market: marketStats.status === 'fulfilled' ? marketStats.value : {}
    };
  } catch (error) {
    console.error("Advanced analytics fetch failed:", error);
    return { trading: [], commentary: [], market: {} };
  }
};

export const optimizePortfolio = async (assets, constraints = {}) => {
  try {
    const response = await fetch(`${BASE_URL}/optimize-portfolio`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ assets, constraints })
    });

    if (response.ok) {
      return await response.json();
    } else {
      throw new Error(`Optimization API returned status ${response.status}`);
    }
  } catch (error) {
    console.error("Portfolio optimization failed:", error);
    return null;
  }
};

export const subscribeToUpdates = (endpoint, callback, interval = UPDATE_INTERVAL) => {
  const fetchFn = () => {
    // Direct call to specific endpoint functions if they exist in mapped object, 
    // or manual fetch for custom endpoints. 
    // Simplified: we only support subscribing to known API methods if 'endpoint' matches method name.
    if (api[endpoint]) {
      api[endpoint]()
        .then(callback)
        .catch(error => console.error(`Update error (${endpoint}):`, error));
    } else {
      // Fallback if endpoint is a URL path
      fetch(`${BASE_URL}/${endpoint}`)
        .then(r => r.json())
        .then(callback)
        .catch(e => console.error(`Subscription error ${endpoint}`, e));
    }
  };

  fetchFn();
  const timer = setInterval(fetchFn, interval);
  return () => clearInterval(timer);
};

export const streamMarketPrice = ({ symbol = "AAPL", interval = 5, count = 0, onMessage = null, onOpen = null, onError = null } = {}) => {
  if (!symbol) throw new Error('streamMarketPrice requires a symbol');
  const normalizedBase = (BASE_URL || '').replace(/\/$/, '');
  const url = `${normalizedBase}/market-price-stream?symbol=${encodeURIComponent(symbol)}&interval=${encodeURIComponent(interval)}&count=${encodeURIComponent(count)}`;
  let es;
  try {
    es = new EventSource(url);
  } catch (err) {
    if (typeof onError === 'function') onError(err);
    throw err;
  }

  es.onopen = (evt) => { if (typeof onOpen === 'function') onOpen(evt); };
  es.onmessage = (evt) => {
    try {
      const payload = JSON.parse(evt.data);
      if (typeof onMessage === 'function') onMessage(payload);
    } catch (err) {
      if (typeof onError === 'function') onError(err);
      console.error('streamMarketPrice JSON parse error', err);
    }
  };
  es.onerror = (evt) => { if (typeof onError === 'function') onError(evt); };

  return {
    close: () => { try { es.close(); } catch (e) { } }
  };
};

export const testConnection = async () => {
  try {
    console.log('Testing connection to:', BASE_URL);
    const response = await fetch(`${BASE_URL}/health`);
    const data = await response.json();
    console.log('Backend health check:', data);
    return { connected: true, ...data };
  } catch (error) {
    console.error('Connection test failed:', error);
    return { connected: false, error: error.message };
  }
};

// Default object export for backward compatibility
export const api = {
  getStatus,
  getAiFirmStatus,
  getGodCycle,
  getMarketPrice,
  getPortfolio,
  getTradingJournal,
  getWarrenAnalysis,
  getCathieAnalysis,
  getRiskMetrics,
  getPerformance,
  getCommentary,
  runTradingCycle,
  runRLCycle,
  getMultiAssetData,
  getSystemHealth,
  getAdvancedAnalytics,
  optimizePortfolio,
  subscribeToUpdates,
  streamMarketPrice,
  testConnection
};

export default api;
