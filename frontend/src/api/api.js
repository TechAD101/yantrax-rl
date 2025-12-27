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

export const getAiFirmStatus = async () => {
  try {
    const r = await fetch(`${BASE_URL}/api/ai-firm/status`);
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    return await r.json();
  } catch (e) {
    console.error('Ai firm status failed:', e);
    throw e;
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


export const getWarrenAnalysis = () => fetchWithRetry(`${BASE_URL}/api/ai-firm/personas/warren`);
export const getCathieAnalysis = () => fetchWithRetry(`${BASE_URL}/api/ai-firm/personas/cathie`);

export const getRiskMetrics = () => fetchWithRetry(`${BASE_URL}/risk-metrics`);
export const getPerformance = () => fetchWithRetry(`${BASE_URL}/performance`);



export const runTradingCycle = () => fetchWithRetry(`${BASE_URL}/run-cycle`, { method: 'POST' });

// Enhanced RL cycle


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
