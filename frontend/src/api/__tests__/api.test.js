import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { runAdvancedRLCycle, BASE_URL } from '../api';

describe('api', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn());
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('runAdvancedRLCycle', () => {
    it('should successfully run an advanced RL cycle with default config', async () => {
      const mockResponse = { success: true, result: 'test_result' };
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await runAdvancedRLCycle();

      expect(fetch).toHaveBeenCalledWith(`${BASE_URL}/run-cycle`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ symbol: 'AAPL', strategy_weights: {}, risk_parameters: {} })
      });
      expect(result).toEqual(mockResponse);
    });

    it('should successfully run an advanced RL cycle with custom config', async () => {
      const mockResponse = { success: true, result: 'custom_result' };
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const config = {
        symbol: 'TSLA',
        strategyWeights: { momentum: 0.8 },
        riskParams: { maxDrawdown: 0.2 }
      };

      const result = await runAdvancedRLCycle(config);

      expect(fetch).toHaveBeenCalledWith(`${BASE_URL}/run-cycle`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          symbol: 'TSLA',
          strategy_weights: { momentum: 0.8 },
          risk_parameters: { maxDrawdown: 0.2 }
        })
      });
      expect(result).toEqual(mockResponse);
    });

    it('should throw an error if the response is not ok', async () => {
      fetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error'
      });

      await expect(runAdvancedRLCycle()).rejects.toThrow('HTTP 500');
    });

    it('should throw an error on network failure', async () => {
      const networkError = new Error('Network Error');
      fetch.mockRejectedValueOnce(networkError);

      await expect(runAdvancedRLCycle()).rejects.toThrow('Network Error');
    });
  });
});
