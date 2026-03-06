import { useEffect, useState } from "react";
import { BASE_URL } from "../api/api";

/**
 * StreamManager
 * Singleton that manages EventSource connections.
 * It multiplexes subscriptions to the same URL.
 */
class StreamManager {
  constructor() {
    this.subscriptions = new Map(); // Key: URL -> Subscription Object
  }

  getKey(symbol, interval, count) {
    const normalizedBase = (BASE_URL || '').replace(/\/$/, '');
    return `${normalizedBase}/market-price-stream?symbol=${encodeURIComponent(symbol)}&interval=${encodeURIComponent(interval)}&count=${encodeURIComponent(count)}`;
  }

  subscribe(symbol, interval, count, callback) {
    const url = this.getKey(symbol, interval, count);

    if (!this.subscriptions.has(url)) {
      this.subscriptions.set(url, this.createSubscription(url));
    }

    const sub = this.subscriptions.get(url);
    sub.listeners.add(callback);

    // Initial state push
    callback(sub.state);

    return () => {
      sub.listeners.delete(callback);
      if (sub.listeners.size === 0) {
        // Add a small delay or cleanup immediately?
        // Immediate cleanup is fine for now as per requirement to close when last leaves.
        this.cleanupSubscription(url, sub);
      }
    };
  }

  createSubscription(url) {
    const sub = {
      url,
      listeners: new Set(),
      es: null,
      reconnectTimer: null,
      backoff: { attempts: 0, base: 1000, max: 60000 },
      state: {
        price: null,
        isLoading: true,
        error: null,
        lastUpdate: null,
      },
    };

    this.connect(sub);
    return sub;
  }

  updateState(sub, updates) {
    sub.state = { ...sub.state, ...updates };
    this.notify(sub);
  }

  connect(sub) {
    if (sub.es) {
      try { sub.es.close(); } catch { /* ignore */ }
      sub.es = null;
    }

    this.updateState(sub, { isLoading: true, error: null });

    if (typeof window === 'undefined' || typeof EventSource === 'undefined') {
      this.updateState(sub, { error: 'eventsource_unavailable', isLoading: false });
      return;
    }

    let es;
    try {
      es = new EventSource(sub.url);
    } catch {
      this.updateState(sub, { error: 'eventsource_init_failed', isLoading: false });
      this.scheduleReconnect(sub);
      return;
    }

    sub.es = es;

    es.onopen = () => {
      sub.backoff.attempts = 0;
      this.updateState(sub, { isLoading: false, error: null });
    };

    es.onmessage = (evt) => {
      if (!evt.data) return;
      try {
        const payload = JSON.parse(evt.data);

        // Server now emits structured events with `type` such as 'error' or 'fallback'
        if (payload?.type === 'error') {
            const message = payload?.error?.message || 'provider_error';
            const code = payload?.error?.code || null;
            this.updateState(sub, {
                error: `provider_error:${message}${code ? ` (code:${code})` : ''}`,
                isLoading: false
            });
            return;
        }

        if (payload?.type === 'fallback') {
            const data = payload?.data ?? {};
            const maybePrice = data?.price ?? data?.close ?? data?.last ?? null;
            if (maybePrice === null || maybePrice === undefined) {
              this.updateState(sub, { error: 'fallback_no_price', isLoading: false });
              return;
            }
            const numeric = Number(maybePrice);
            if (!Number.isFinite(numeric)) {
                this.updateState(sub, { error: 'non_numeric_price', isLoading: false });
                return;
            }
            this.updateState(sub, {
                price: numeric,
                lastUpdate: payload.timestamp ? new Date(payload.timestamp) : new Date(),
                error: 'fallback',
                isLoading: false
            });
            return;
        }

        // Default: older-style payloads where the price may be inside payload.data or top-level
        const data = payload?.data ?? payload;
        const maybePrice = data?.price ?? data?.close ?? data?.last ?? null;
        if (maybePrice === null || maybePrice === undefined) {
          this.updateState(sub, { error: 'invalid_payload' });
          return;
        }
        const numeric = Number(maybePrice);
        if (!Number.isFinite(numeric)) {
            this.updateState(sub, { error: 'non_numeric_price' });
            return;
        }

        this.updateState(sub, {
            price: numeric,
            lastUpdate: payload.timestamp ? new Date(payload.timestamp) : new Date(),
            error: null,
            isLoading: false
        });

      } catch {
        this.updateState(sub, { error: 'json_parse_error' });
      }
    };

    es.onerror = () => {
      this.updateState(sub, { error: 'connection_error', isLoading: false });
      try { es.close(); } catch { /* ignore */ }
      sub.es = null;
      this.scheduleReconnect(sub);
    };
  }

  scheduleReconnect(sub) {
    if (sub.reconnectTimer) clearTimeout(sub.reconnectTimer);

    // If we are destroying this subscription, don't reconnect
    if (!this.subscriptions.has(sub.url)) return;

    sub.backoff.attempts += 1;
    const delay = Math.min(
      Math.round(sub.backoff.base * Math.pow(1.5, sub.backoff.attempts - 1)),
      sub.backoff.max
    );
    sub.reconnectTimer = setTimeout(() => {
        // Double check existence before connecting
        if (this.subscriptions.has(sub.url)) {
            this.connect(sub);
        }
    }, delay);
  }

  notify(sub) {
    sub.listeners.forEach(cb => cb(sub.state));
  }

  cleanupSubscription(url, sub) {
    if (sub.reconnectTimer) clearTimeout(sub.reconnectTimer);
    if (sub.es) {
      try { sub.es.close(); } catch { /* ignore */ }
    }
    this.subscriptions.delete(url);
  }
}

const streamManager = new StreamManager();

/**
 * useMarketStream
 * Subscribes to the backend SSE `/market-price-stream` endpoint for a symbol.
 * Returns { price, isLoading, error, lastUpdate }
 */
export default function useMarketStream(symbol, { interval = 5, count = 0 } = {}) {
  const [state, setState] = useState({
    price: null,
    isLoading: true,
    error: null,
    lastUpdate: null,
  });

  useEffect(() => {
    if (!symbol) {
      setState(s => ({ ...s, error: 'missing_symbol', isLoading: false }));
      return;
    }

    const unsubscribe = streamManager.subscribe(symbol, interval, count, (newState) => {
      setState(newState);
    });

    return () => {
      unsubscribe();
    };
  }, [symbol, interval, count]);

  return state;
}
