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
