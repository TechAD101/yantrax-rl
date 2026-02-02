import React, { useState, useEffect } from 'react';
import { createOrder as apiCreateOrder, listOrders as apiListOrders } from '../api/api';

export default function OrderManager() {
  const [symbol, setSymbol] = useState('');
  const [usd, setUsd] = useState(100);
  const [orders, setOrders] = useState([]);
  const [message, setMessage] = useState(null);

  const fetchOrders = async () => {
    try {
      const res = await apiListOrders(50);
      setOrders(res.orders || []);
    } catch (e) {
      setMessage({ type: 'error', text: `Failed to load orders: ${e.message}` });
    }
  };

  useEffect(() => {
    fetchOrders();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage(null);
    try {
      const resp = await apiCreateOrder(symbol, Number(usd));
      if (resp.order) {
        setMessage({ type: 'success', text: `Created order ${resp.order.symbol} $${resp.order.usd}` });
        setSymbol('');
        setUsd(100);
        fetchOrders();
      } else {
        setMessage({ type: 'error', text: 'Unexpected response' });
      }
    } catch (err) {
      setMessage({ type: 'error', text: err.message });
    }
  };

  return (
    <div className="p-6 bg-gray-900/80 rounded-xl border border-gray-700/40">
      <h2 className="text-xl font-bold text-white mb-4">Order Manager (Paper)</h2>
      <form onSubmit={handleSubmit} className="mb-4 flex items-center space-x-2">
        <input placeholder="Symbol" value={symbol} onChange={e => setSymbol(e.target.value)} className="px-2 py-1 rounded bg-gray-900/50" />
        <input type="number" value={usd} onChange={e => setUsd(e.target.value)} className="px-2 py-1 rounded bg-gray-900/50 w-24" />
        <button className="px-3 py-1 bg-green-600 rounded text-white">Create Order</button>
      </form>

      {message && (
        <div className={`mb-4 ${message.type === 'error' ? 'text-red-400' : 'text-green-400'}`}>{message.text}</div>
      )}

      <h4 className="text-sm text-gray-300 mb-2">Recent Orders</h4>
      <div className="grid grid-cols-1 gap-2">
        {orders.length === 0 && <div className="text-gray-400">No orders yet</div>}
        {orders.map(o => (
          <div key={o.id} className="bg-gray-800/40 p-3 rounded">
            <div className="font-bold text-white">{o.symbol}</div>
            <div className="text-xs text-gray-400">Status: {o.status} • USD: {o.usd} • Qty: {o.quantity}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
