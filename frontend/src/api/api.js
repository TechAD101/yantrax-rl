// YantraX API Client v4.2.0 (Consolidated)
const BASE_URL = import.meta.env.VITE_API_URL || 'https://yantrax-backend.onrender.com';
const UPDATE_INTERVAL = 15000; // 15 seconds

// Export BASE_URL so UI components can reuse the same resolved backend URL
export { BASE_URL };

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

export const getStatus = () => fetchWithRetry(`${BASE_URL}/`);

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
