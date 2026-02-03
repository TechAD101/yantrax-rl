// YantraX API Client - consolidated and robust
// Resolve backend BASE URL from Vite env var or process env fallbacks
const API_BASE_URL = (typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.VITE_API_URL)
  ? import.meta.env.VITE_API_URL
  : 'https://yantrax-backend.onrender.com';

const BASE_URL = API_BASE_URL;
export { BASE_URL };

const UPDATE_INTERVAL = 60000; // 60 seconds (1 minute updates)
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


// Backwards-compatible status endpoint used by Header.subscribeToUpdates('getStatus')
export const getStatus = () => fetchWithRetry(`${BASE_URL}/`);

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

// Portfolio endpoint used by the dashboard and real-time subscriptions
export const getPortfolio = async () => {
  try {
    const r = await fetch(`${BASE_URL}/portfolio`);
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    return await r.json();
  } catch (e) {
    console.error('Portfolio fetch failed:', e);
    // Return a safe minimal shape expected by the UI
    return { total_value: 0, daily_pnl: 0, total_return: 0, total_positions: 0, positions: [], recent_trades: [] };
  }
};

// Backwards-compatible alias for earlier naming
export const getTradingJournal = getJournal;

export const streamMarketPrice = ({ symbol = 'AAPL', interval = 60, count = 0, onMessage = null, onOpen = null, onError = null } = {}) => {
  if (!symbol) throw new Error('streamMarketPrice requires a symbol');
  const normalizedBase = (BASE_URL || '').replace(/\/$/, '');
  const url = `${normalizedBase}/market-price-stream?symbol=${encodeURIComponent(symbol)}&interval=${encodeURIComponent(interval)}&count=${encodeURIComponent(count)}`;
  let es;
  try { es = new EventSource(url) } catch (err) { if (typeof onError === 'function') onError(err); throw err }
  es.onopen = (evt) => { if (typeof onOpen === 'function') onOpen(evt) }
  es.onmessage = (evt) => { try { const payload = JSON.parse(evt.data); if (typeof onMessage === 'function') onMessage(payload) } catch (err) { if (typeof onError === 'function') onError(err); console.error('streamMarketPrice JSON parse error', err) } }
  es.onerror = (evt) => { if (typeof onError === 'function') onError(evt) }
  return { close: () => { try { es.close() } catch (e) { } } }
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


export const createPortfolio = async (config) => {
  // Map frontend wizard config to backend API format
  const portfolioData = {
    name: config.name || 'My Portfolio',
    risk_profile: config.risk || 'moderate',
    initial_capital: config.capital || 50000,
    strategy_preference: config.strategy || 'balanced'
  };

  return fetchWithRetry(`${BASE_URL}/api/portfolio/create`, {
    method: 'POST',
    body: JSON.stringify(portfolioData)
  });
};

export const listStrategies = async (opts = {}) => {
  const qs = new URLSearchParams();
  if (opts.page) qs.set('page', opts.page);
  if (opts.per_page) qs.set('per_page', opts.per_page);
  if (opts.archetype) qs.set('archetype', opts.archetype);
  if (opts.q) qs.set('q', opts.q);
  if (opts.min_sharpe) qs.set('min_sharpe', opts.min_sharpe);
  if (opts.min_win_rate) qs.set('min_win_rate', opts.min_win_rate);
  if (opts.sort_by) qs.set('sort_by', opts.sort_by);
  if (opts.order) qs.set('order', opts.order);

  return fetchWithRetry(`${BASE_URL}/api/strategy/list?${qs.toString()}`);
};

export const getTopStrategies = async (opts = {}) => {
  const qs = new URLSearchParams();
  qs.set('limit', opts.limit || 3);
  qs.set('metric', opts.metric || 'sharpe');
  qs.set('order', opts.order || 'desc');
  return fetchWithRetry(`${BASE_URL}/api/strategy/top?${qs.toString()}`);
};

export const scanMemecoins = async (symbols = []) => {
  return fetchWithRetry(`${BASE_URL}/api/memecoin/scan`, { method: 'POST', body: JSON.stringify({ symbols }) });
};

export const getTopMemecoins = async (limit = 10) => {
  return fetchWithRetry(`${BASE_URL}/api/memecoin/top?limit=${limit}`);
};

export const simulateMemecoin = async (symbol, usd = 100) => {
  return fetchWithRetry(`${BASE_URL}/api/memecoin/simulate`, { method: 'POST', body: JSON.stringify({ symbol, usd }) });
};

// Order Manager (paper)
export const createOrder = async (symbol, usd = 100) => {
  return fetchWithRetry(`${BASE_URL}/api/orders`, { method: 'POST', body: JSON.stringify({ symbol, usd }) });
};

export const listOrders = async (limit = 100) => {
  return fetchWithRetry(`${BASE_URL}/api/orders?limit=${limit}`);
};

export const getOrder = async (orderId) => {
  return fetchWithRetry(`${BASE_URL}/api/orders/${orderId}`);
};

export const runTradingCycle = () => fetchWithRetry(`${BASE_URL}/run-cycle`, { method: 'POST' });

// ==================== INSTITUTIONAL ENDPOINTS ====================

// Knowledge Base
export const queryKnowledge = (topic, archetype = null) =>
  fetchWithRetry(`${BASE_URL}/api/knowledge/query`, {
    method: 'POST',
    body: JSON.stringify({ topic, archetype })
  });

export const getKnowledgeStats = () => fetchWithRetry(`${BASE_URL}/api/knowledge/stats`);

// Personas
export const getPersonas = () => fetchWithRetry(`${BASE_URL}/api/personas`);

export const getVotingHistory = (limit = 10) => fetchWithRetry(`${BASE_URL}/api/ai-firm/voting-history?limit=${limit}`);

export const getPersonaDetails = (name) => fetchWithRetry(`${BASE_URL}/api/personas/${name}`);

export const conductPersonaVote = (proposal, context = {}) =>
  fetchWithRetry(`${BASE_URL}/api/personas/vote`, {
    method: 'POST',
    body: JSON.stringify({ proposal, ...context })
  });

// Trade Validation
export const validateTrade = (trade, marketContext = {}) =>
  fetchWithRetry(`${BASE_URL}/api/trade/validate`, {
    method: 'POST',
    body: JSON.stringify({ trade, market_context: marketContext })
  });

export const getValidationStats = () => fetchWithRetry(`${BASE_URL}/api/trade/validation-stats`);

// Data Verification
export const getVerifiedPrice = (symbol) => fetchWithRetry(`${BASE_URL}/api/data/price-verified?symbol=${symbol}`);

export const getVerificationStats = () => fetchWithRetry(`${BASE_URL}/api/data/verification-stats`);

// ================================================================

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
  testConnection,
  // New Institutional
  queryKnowledge,
  getKnowledgeStats,
  getVotingHistory,
  getPersonas,
  getPersonaDetails,
  conductPersonaVote,
  validateTrade,
  getValidationStats,
  getVerifiedPrice,
  getVerificationStats,

  // Manual trigger for Knowledge Ingestion
  triggerKnowledgeIngest: async () => {
    try {
      const resp = await fetch(`${BASE_URL}/api/knowledge/ingest`, { method: 'POST' });
      return await resp.json();
    } catch (e) {
      console.error('Ingestion trigger failed:', e);
      return { success: false, error: e.message };
    }
  },
  // New Institutional Phase Ω
  getInstitutionalReport: (symbol = 'AAPL') => fetchWithRetry(`${BASE_URL}/report/institutional?symbol=${symbol}`),
  getSystemStatus: () => fetchWithRetry(`${BASE_URL}/health`),
  // WORLD CLASS API (Vision Upgrade)
  getVisualMoodBoard: async () => {
    try {
      const resp = await fetchWithRetry(`${BASE_URL}/api/visual_mood_board`);
      return resp;
    } catch (e) {
      console.error('Mood Board fetch failed:', e);
      return { emotion_dial: { current_mood: 'neutral', pain_meter: 0 }, market_weather: 'Cloudy', philosophy_quote: 'Connecting...' };
    }
  },

  getTopStrategies: async (limit = 10) => {
    return fetchWithRetry(`${BASE_URL}/api/strategies/top?limit=${limit}`);
  },

  publishStrategy: async (data) => {
    const response = await fetch(`${BASE_URL}/api/strategies/publish`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Failed to publish strategy');
    return await response.json();
  },

  copyStrategy: async (data) => {
    const response = await fetch(`${BASE_URL}/api/strategies/copy`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Failed to copy strategy');
    return await response.json();
  },

  getActiveContest: async () => {
    return fetchWithRetry(`${BASE_URL}/api/contests/active`);
  },

  // ==================== PERPLEXITY INTELLIGENCE API ====================

  // Get AI-powered sentiment analysis for a ticker
  getMarketSentiment: async (ticker = 'AAPL', includeNews = true) => {
    try {
      const resp = await fetchWithRetry(
        `${BASE_URL}/api/intelligence/sentiment?ticker=${encodeURIComponent(ticker)}&include_news=${includeNews}`
      );
      return resp;
    } catch (e) {
      console.error('Sentiment fetch failed:', e);
      return { ticker, mood: 'neutral', confidence: 0, error: e.message };
    }
  },

  // Get trending sector analysis
  getTrendingAnalysis: async (sector = 'technology', focus = 'opportunities') => {
    try {
      return await fetchWithRetry(
        `${BASE_URL}/api/intelligence/trending?sector=${encodeURIComponent(sector)}&focus=${encodeURIComponent(focus)}`
      );
    } catch (e) {
      console.error('Trending fetch failed:', e);
      return { sector, opportunities: [], risks: [], error: e.message };
    }
  },

  // Get AI market commentary from different personas
  getAICommentary: async (tickers = ['AAPL'], persona = null) => {
    try {
      const tickerStr = Array.isArray(tickers) ? tickers.join(',') : tickers;
      let url = `${BASE_URL}/api/intelligence/commentary?tickers=${encodeURIComponent(tickerStr)}`;
      if (persona) url += `&persona=${encodeURIComponent(persona)}`;
      return await fetchWithRetry(url);
    } catch (e) {
      console.error('Commentary fetch failed:', e);
      return { tickers, headline: 'Unavailable', error: e.message };
    }
  },

  // Get real-time market context for debates
  getDebateContext: async (topic, tickers = []) => {
    try {
      const tickerStr = tickers.join(',');
      return await fetchWithRetry(
        `${BASE_URL}/api/intelligence/debate-context?topic=${encodeURIComponent(topic)}&tickers=${encodeURIComponent(tickerStr)}`
      );
    } catch (e) {
      console.error('Debate context fetch failed:', e);
      return { topic, error: e.message };
    }
  },

  // Search financial news from trusted sources
  searchFinancialNews: async (query, maxResults = 5, trustedOnly = true) => {
    try {
      return await fetchWithRetry(
        `${BASE_URL}/api/intelligence/search?query=${encodeURIComponent(query)}&max_results=${maxResults}&trusted_sources=${trustedOnly}`
      );
    } catch (e) {
      console.error('News search failed:', e);
      return { query, results: [], error: e.message };
    }
  },

  // Get ticker-specific news (earnings, analyst, sec filings)
  getTickerNews: async (ticker = 'AAPL', type = 'all') => {
    try {
      return await fetchWithRetry(
        `${BASE_URL}/api/intelligence/ticker-news?ticker=${encodeURIComponent(ticker)}&type=${encodeURIComponent(type)}`
      );
    } catch (e) {
      console.error('Ticker news fetch failed:', e);
      return { ticker, results: [], error: e.message };
    }
  },

  // Check intelligence service status
  getIntelligenceStatus: async () => {
    try {
      return await fetchWithRetry(`${BASE_URL}/api/intelligence/status`);
    } catch (e) {
      return { configured: false, error: e.message };
    }
  }
};

// ==================== NEW MVP ENDPOINTS ====================

// Portfolio Trading
export const getPortfolioById = (id) => fetchWithRetry(`${BASE_URL}/api/portfolio/${id}`);

export const executeTrade = async (portfolioId, tradeData) => {
  return fetchWithRetry(`${BASE_URL}/api/portfolio/${portfolioId}/trade`, {
    method: 'POST',
    body: JSON.stringify(tradeData)
  });
};

// Market Search
export const searchMarket = (query, limit = 5) =>
  fetchWithRetry(`${BASE_URL}/api/market-search?query=${encodeURIComponent(query)}&limit=${limit}`);

// AI Debate Engine
export const triggerAIDebate = async (symbol, context = {}) => {
  return fetchWithRetry(`${BASE_URL}/api/strategy/ai-debate/trigger`, {
    method: 'POST',
    body: JSON.stringify({
      symbol: symbol.toUpperCase(),
      context: context
    })
  });
};

// Ingestion Trigger
export const triggerKnowledgeIngest = () => fetchWithRetry(`${BASE_URL}/api/knowledge/ingest`, { method: 'POST' });


// AI Firm Status
export const getAIFirmStatus = () => fetchWithRetry(`${BASE_URL}/api/ai-firm/status`);

// Trading Journal
export const getJournalEntries = (limit = 50) =>
  fetchWithRetry(`${BASE_URL}/api/journal?limit=${limit}`);

export default api;
