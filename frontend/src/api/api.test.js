import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { testConnection, BASE_URL } from './api';

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
});
