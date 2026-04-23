import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { testConnection } from './api';

describe('api.js - testConnection', () => {
  const originalFetch = global.fetch;
  const originalConsoleLog = console.log;
  const originalConsoleError = console.error;

  beforeEach(() => {
    global.fetch = vi.fn();
    console.log = vi.fn();
    console.error = vi.fn();
  });

  afterEach(() => {
    global.fetch = originalFetch;
    console.log = originalConsoleLog;
    console.error = originalConsoleError;
    vi.restoreAllMocks();
  });

  it('should return connected: true and data on successful fetch', async () => {
    const mockData = { status: 'healthy', version: '1.0.0' };
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockData,
    });

    const result = await testConnection();

    expect(global.fetch).toHaveBeenCalledTimes(1);
    // Since BASE_URL might be defined differently depending on env, we just check fetch was called
    expect(result).toEqual({ connected: true, ...mockData });
    expect(console.log).toHaveBeenCalledWith('Testing connection to:', expect.anything());
    expect(console.log).toHaveBeenCalledWith('Backend health check:', mockData);
  });

  it('should return connected: false and error message on failed fetch', async () => {
    const errorMessage = 'Network error';
    global.fetch.mockRejectedValueOnce(new Error(errorMessage));

    const result = await testConnection();

    expect(global.fetch).toHaveBeenCalledTimes(1);
    expect(result).toEqual({ connected: false, error: errorMessage });
    expect(console.error).toHaveBeenCalledWith('Connection test failed:', expect.any(Error));
  });
});
