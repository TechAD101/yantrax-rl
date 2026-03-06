// @vitest-environment jsdom
import { renderHook, act } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import useMarketStream from '../hooks/useMarketStream';

// Mock EventSource
const mockEventSource = vi.fn();
global.EventSource = mockEventSource;

describe('useMarketStream Performance', () => {
  let eventSourceInstances = [];

  beforeEach(() => {
    eventSourceInstances = [];
    mockEventSource.mockReset();
    mockEventSource.mockImplementation((url) => {
      const instance = {
        url,
        close: vi.fn(),
        onopen: null,
        onmessage: null,
        onerror: null,
      };
      eventSourceInstances.push(instance);
      return instance;
    });
  });

  it('creates only ONE connection for multiple subscribers to the same symbol', () => {
    const symbol = 'BTC-USD';
    const options = { interval: 5 };

    // Render hook 1
    const { unmount: unmount1 } = renderHook(() => useMarketStream(symbol, options));

    // Render hook 2
    const { unmount: unmount2 } = renderHook(() => useMarketStream(symbol, options));

    // Expect ONLY 1 connection
    expect(mockEventSource).toHaveBeenCalledTimes(1);
    expect(eventSourceInstances.length).toBe(1);

    // Verify cleanup
    unmount1();
    // Connection should still be open
    expect(eventSourceInstances[0].close).not.toHaveBeenCalled();

    unmount2();
    // Connection should be closed now
    expect(eventSourceInstances[0].close).toHaveBeenCalled();
  });

  it('broadcasts messages to all subscribers', () => {
    const symbol = 'ETH-USD';
    const options = { interval: 5 };

    const { result: result1, unmount: unmount1 } = renderHook(() => useMarketStream(symbol, options));
    const { result: result2, unmount: unmount2 } = renderHook(() => useMarketStream(symbol, options));

    const instance = eventSourceInstances[0];

    // Simulate open
    act(() => {
        if (instance.onopen) instance.onopen();
    });

    // Simulate message
    const payload = JSON.stringify({ data: { price: 3000, last: 3000 } });
    act(() => {
        if (instance.onmessage) instance.onmessage({ data: payload });
    });

    expect(result1.current.price).toBe(3000);
    expect(result2.current.price).toBe(3000);
    expect(result1.current.isLoading).toBe(false);

    unmount1();
    unmount2();
  });

  it('handles different symbols with separate connections', () => {
    const { unmount: unmount1 } = renderHook(() => useMarketStream('AAPL', { interval: 5 }));
    const { unmount: unmount2 } = renderHook(() => useMarketStream('GOOGL', { interval: 5 }));

    expect(mockEventSource).toHaveBeenCalledTimes(2);

    unmount1();
    unmount2();
  });
});
