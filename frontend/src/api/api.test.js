import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import {
  testConnection,
  BASE_URL,
  getRiskMetrics,
  getPerformance,
  getWarrenAnalysis,
  getCathieAnalysis,
  api,
} from './api';

describe('api.js - testConnection', () => {
  const originalFetch = global.fetch;

  beforeEach(() => {
    global.fetch = vi.fn();
    vi.spyOn(console, 'log').mockImplementation(() => {});
    vi.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    global.fetch = originalFetch;
    vi.restoreAllMocks();
  });

  it('should return connected: true and data on successful fetch', async () => {
    const mockData = { status: 'ok', uptime: 123 };
    global.fetch.mockResolvedValueOnce({
      json: vi.fn().mockResolvedValueOnce(mockData)
    });

    const result = await testConnection();

    expect(global.fetch).toHaveBeenCalledWith(`${BASE_URL}/health`);
    expect(result).toEqual({ connected: true, ...mockData });
  });

  it('should return connected: false and error message on failed fetch', async () => {
    const mockError = new Error('Network error');
    global.fetch.mockRejectedValueOnce(mockError);

    const result = await testConnection();

    expect(global.fetch).toHaveBeenCalledWith(`${BASE_URL}/health`);
    expect(result).toEqual({ connected: false, error: 'Network error' });
  });

  it('uses backend API paths for risk and performance widgets', async () => {
    global.fetch.mockResolvedValue({ ok: true, json: vi.fn().mockResolvedValue({}) });

    await getRiskMetrics();
    await getPerformance();

    expect(global.fetch).toHaveBeenNthCalledWith(1, `${BASE_URL}/api/risk-metrics`, expect.any(Object));
    expect(global.fetch).toHaveBeenNthCalledWith(2, `${BASE_URL}/api/performance`, expect.any(Object));
  });

  it('uses POST for legacy persona analysis endpoints', async () => {
    global.fetch.mockResolvedValue({ ok: true, json: vi.fn().mockResolvedValue({}) });

    await getWarrenAnalysis('AAPL');
    await getCathieAnalysis('NVDA');

    expect(global.fetch).toHaveBeenNthCalledWith(1, `${BASE_URL}/api/ai-firm/personas/warren`, expect.objectContaining({
      method: 'POST',
      body: JSON.stringify({ symbol: 'AAPL' }),
    }));
    expect(global.fetch).toHaveBeenNthCalledWith(2, `${BASE_URL}/api/ai-firm/personas/cathie`, expect.objectContaining({
      method: 'POST',
      body: JSON.stringify({ symbol: 'NVDA' }),
    }));
  });

  it('keeps a performance metrics alias for existing subscribers', () => {
    expect(api.getPerformanceMetrics).toBe(api.getPerformance);
  });
});
