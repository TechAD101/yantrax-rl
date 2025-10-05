// YantraX API Client v4.1.0
const API_BASE_URL = 'https://yantrax-backend.onrender.com';
const UPDATE_INTERVAL = 15000; // 15 seconds

// Retry configuration
const MAX_RETRIES = 3;
const RETRY_DELAY = 1000;

// Error types
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

// API Endpoints
export const api = {
  // System Status
  getStatus: () => fetchWithRetry(`${API_BASE_URL}/`),
  
  // AI Firm
  getAiFirmStatus: () => fetchWithRetry(`${API_BASE_URL}/api/ai-firm/status`),
  getGodCycle: () => fetchWithRetry(`${API_BASE_URL}/god-cycle`),
  
  // Trading & Analysis
  getMarketPrice: (symbol) => 
    fetchWithRetry(`${API_BASE_URL}/market-price?symbol=${symbol}`),
  getPortfolio: () => fetchWithRetry(`${API_BASE_URL}/portfolio`),
  getTradingJournal: () => fetchWithRetry(`${API_BASE_URL}/journal`),
  
  // Personas
  getWarrenAnalysis: () => 
    fetchWithRetry(`${API_BASE_URL}/api/ai-firm/personas/warren`),
  getCathieAnalysis: () => 
    fetchWithRetry(`${API_BASE_URL}/api/ai-firm/personas/cathie`),
  
  // Performance & Risk
  getRiskMetrics: () => fetchWithRetry(`${API_BASE_URL}/risk-metrics`),
  getPerformance: () => fetchWithRetry(`${API_BASE_URL}/performance`),
  
  // Utilities
  getCommentary: () => fetchWithRetry(`${API_BASE_URL}/commentary`),
  runTradingCycle: () => 
    fetchWithRetry(`${API_BASE_URL}/run-cycle`, { method: 'POST' })
};

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
const BASE_URL = process.env.REACT_APP_API_URL || "https://yantrax-backend.onrender.com";

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
      // Return mock optimization for now
      return {
        allocation: assets.reduce((acc, asset, i) => {
          acc[asset] = 1.0 / assets.length;
          return acc;
        }, {}),
        expected_return: 0.12,
        volatility: 0.18,
        sharpe_ratio: 1.25
      };
    }
  } catch (error) {
    console.error("Portfolio optimization failed:", error);
    return null;
  }
};

// Existing API functions (enhanced)
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

export const runRLCycle = async () => {
  return await runAdvancedRLCycle();
};

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

