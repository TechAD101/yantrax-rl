import { useEffect, useRef, useState } from "react";
import { BASE_URL } from "../api/api";

/**
 * useMarketStream
 * Subscribes to the backend SSE `/market-price-stream` endpoint for a symbol.
 * Returns { price, isLoading, error, lastUpdate }
 */
export default function useMarketStream(symbol, { interval = 5, count = 0 } = {}) {
  const [price, setPrice] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);

  const esRef = useRef(null);
  const backoffRef = useRef({ attempts: 0, base: 1000, max: 60000 });
  const reconnectTimer = useRef(null);
  const mounted = useRef(true);

  useEffect(() => {
    mounted.current = true;

    if (!symbol) {
      setError('missing_symbol');
      setIsLoading(false);
      return () => { mounted.current = false; };
    }

    const normalizedBase = (BASE_URL || '').replace(/\/$/, '');
    const url = `${normalizedBase}/market-price-stream?symbol=${encodeURIComponent(symbol)}&interval=${encodeURIComponent(interval)}&count=${encodeURIComponent(count)}`;

    const clearReconnect = () => {
      if (reconnectTimer.current) {
        clearTimeout(reconnectTimer.current);
        reconnectTimer.current = null;
      }
    };

    const scheduleReconnect = () => {
      clearReconnect();
      backoffRef.current.attempts += 1;
      const delay = Math.min(Math.round(backoffRef.current.base * Math.pow(1.5, backoffRef.current.attempts - 1)), backoffRef.current.max);
      reconnectTimer.current = setTimeout(() => connect(), delay);
    };

    const connect = () => {
      try { if (esRef.current) { esRef.current.close(); esRef.current = null; } } catch (e) {}
      setIsLoading(true);
      setError(null);

      if (typeof window === 'undefined' || typeof EventSource === 'undefined') {
        setError('eventsource_unavailable');
        setIsLoading(false);
        return;
      }

      let es;
      try {
        es = new EventSource(url);
      } catch (e) {
        setError('eventsource_init_failed');
        setIsLoading(false);
        scheduleReconnect();
        return;
      }

      esRef.current = es;

      es.onopen = () => {
        backoffRef.current.attempts = 0;
        setIsLoading(false);
        setError(null);
      };

      es.onmessage = (evt) => {
        if (!mounted.current) return;
        if (!evt.data) return;
        try {
          const payload = JSON.parse(evt.data);
          const data = payload?.data ?? payload;
          const maybePrice = data?.price ?? data?.close ?? data?.last ?? null;
          if (maybePrice === null || maybePrice === undefined) {
            setError('invalid_payload');
            return;
          }
          const numeric = Number(maybePrice);
          if (!Number.isFinite(numeric)) { setError('non_numeric_price'); return; }
          setPrice(numeric);
          setLastUpdate(payload.timestamp ? new Date(payload.timestamp) : new Date());
          setError(null);
          setIsLoading(false);
        } catch (err) {
          setError('json_parse_error');
        }
      };

      es.onerror = () => {
        if (!mounted.current) return;
        setError('connection_error');
        setIsLoading(false);
        try { es.close(); } catch (e) {}
        scheduleReconnect();
      };
    };

    connect();

    return () => {
      mounted.current = false;
      clearReconnect();
      try { if (esRef.current) { esRef.current.close(); esRef.current = null; } } catch (e) {}
    };
  }, [symbol, interval, count]);

  return { price, isLoading, error, lastUpdate };
}
