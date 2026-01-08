import React, { useState, useEffect } from 'react';
import { BASE_URL, listStrategies } from '../api/api';

const StrategyHub = () => {
  const [strategies, setStrategies] = useState([]);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);
  const [perPage, setPerPage] = useState(6);
  const [totalPages, setTotalPages] = useState(1);
  const [q, setQ] = useState('');
  const [archetype, setArchetype] = useState('');
  const [minSharpe, setMinSharpe] = useState('');
  const [sortBy, setSortBy] = useState('created_at');
  const [order, setOrder] = useState('desc');

  useEffect(() => {
    fetchStrategies();
  }, [page, perPage, q, archetype, minSharpe, sortBy, order]);

  const fetchStrategies = async () => {
    setLoading(true);
    try {
      const data = await listStrategies({ page, per_page: perPage, q, archetype, min_sharpe: minSharpe, sort_by: sortBy, order });
      setStrategies(data.strategies || []);
      setTotalPages(data.total_pages || 1);
    } catch (e) {
      console.error('Failed to fetch strategies', e);
    } finally {
      setLoading(false);
    }
  };

  const [formOpen, setFormOpen] = useState(false);
  const [form, setForm] = useState({ name: '', description: '', archetype: '', params: '{}', metrics: '{}' });

  const publish = async () => {
    try {
      const body = {
        name: form.name,
        description: form.description,
        archetype: form.archetype,
        params: JSON.parse(form.params || '{}'),
        metrics: JSON.parse(form.metrics || '{}')
      };
      const r = await fetch(`${BASE_URL}/api/strategy/publish`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
      const data = await r.json();
      if (r.ok) {
        setFormOpen(false);
        fetchStrategies();
      } else {
        alert('Publish failed: ' + (data.error || 'unknown'));
      }
    } catch (e) {
      console.error('Publish error', e);
      alert('Publish error');
    }
  };

  return (
    <div className="p-6 bg-gray-900/80 rounded-xl border border-gray-700/40">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-white">Strategy Hub (Internal)</h2>
        <div className="flex items-center space-x-3">
          <div className="flex items-center bg-gray-800/30 rounded p-2 space-x-2">
            <input placeholder="Search" value={q} onChange={e => { setQ(e.target.value); setPage(1); }} className="px-2 py-1 rounded bg-gray-900/50 text-sm" />
            <input placeholder="Archetype" value={archetype} onChange={e => { setArchetype(e.target.value); setPage(1); }} className="px-2 py-1 rounded bg-gray-900/50 text-sm w-28" />
            <input placeholder="Min Sharpe" value={minSharpe} onChange={e => { setMinSharpe(e.target.value); setPage(1); }} className="px-2 py-1 rounded bg-gray-900/50 text-sm w-20" />
            <select value={sortBy} onChange={e => { setSortBy(e.target.value); setPage(1); }} className="px-2 py-1 rounded bg-gray-900/50 text-sm">
              <option value="created_at">Newest</option>
              <option value="sharpe">Sharpe</option>
              <option value="win_rate">Win Rate</option>
            </select>
            <button onClick={() => setOrder(order === 'asc' ? 'desc' : 'asc')} className="px-2 py-1 rounded bg-gray-900/50 text-sm">{order === 'asc' ? '↑' : '↓'}</button>
          </div>
          <button onClick={() => setFormOpen(!formOpen)} className="px-3 py-2 bg-indigo-600 rounded-md text-white text-sm">{formOpen ? 'Close' : 'Publish Strategy'}</button>
        </div>
      </div>

      {formOpen && (
        <div className="bg-gray-800/30 rounded p-4 mb-4 border border-white/5">
          <div className="grid grid-cols-1 gap-2">
            <input placeholder="Name" value={form.name} onChange={e => setForm({...form, name: e.target.value})} className="p-2 rounded bg-gray-900/50" />
            <input placeholder="Archetype" value={form.archetype} onChange={e => setForm({...form, archetype: e.target.value})} className="p-2 rounded bg-gray-900/50" />
            <textarea placeholder="Description" value={form.description} onChange={e => setForm({...form, description: e.target.value})} className="p-2 rounded bg-gray-900/50" />
            <input placeholder='Params (JSON)' value={form.params} onChange={e => setForm({...form, params: e.target.value})} className="p-2 rounded bg-gray-900/50" />
            <input placeholder='Metrics (JSON)' value={form.metrics} onChange={e => setForm({...form, metrics: e.target.value})} className="p-2 rounded bg-gray-900/50" />
            <div className="flex justify-end">
              <button onClick={publish} className="px-3 py-2 bg-green-600 rounded-md text-white">Publish (internal)</button>
            </div>
          </div>
        </div>
      )}

      {loading ? (
        <div className="text-gray-400">Loading...</div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {strategies.map((s) => (
              <div key={s.id} className="bg-gray-800/40 rounded-lg p-4 border border-white/5">
                <div className="flex items-center justify-between mb-2">
                  <div className="text-lg font-semibold text-white">{s.name}</div>
                  <div className="text-xs text-gray-400">{s.archetype}</div>
                </div>
                <div className="text-sm text-gray-300 mb-2">{s.description}</div>
                <div className="text-xs text-gray-500">Metrics: {JSON.stringify(s.metrics || {})}</div>
              </div>
            ))}
          </div>

          {/* Pagination Controls */}
          <div className="flex items-center justify-between mt-4">
            <div className="flex items-center space-x-2">
              <button onClick={() => setPage(Math.max(1, page - 1))} className="px-2 py-1 rounded bg-gray-900/20 text-sm" disabled={page === 1}>Prev</button>
              <span className="text-sm text-gray-300">Page {page} of {totalPages}</span>
              <button onClick={() => setPage(Math.min(totalPages, page + 1))} className="px-2 py-1 rounded bg-gray-900/20 text-sm" disabled={page >= totalPages}>Next</button>
            </div>

            <div className="flex items-center space-x-2">
              <label className="text-xs text-gray-400">Per page</label>
              <select value={perPage} onChange={e => { setPerPage(parseInt(e.target.value, 10)); setPage(1); }} className="px-2 py-1 rounded bg-gray-900/20 text-sm">
                <option value={6}>6</option>
                <option value={12}>12</option>
                <option value={24}>24</option>
              </select>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default StrategyHub;
