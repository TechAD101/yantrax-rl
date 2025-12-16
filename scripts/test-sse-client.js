let EventSource;
try {
  EventSource = require('eventsource');
  EventSource = EventSource && (EventSource.default || EventSource);
} catch (e) {
  // Fallback to frontend-local installed package
  const mod = require('/workspaces/yantrax-rl/frontend/node_modules/eventsource/dist/index.cjs');
  EventSource = mod && (mod.default || mod);
}

const url = process.argv[2] || 'http://127.0.0.1:5000/market-price-stream?symbol=AAPL&count=5';

console.log('Connecting to', url);
const es = new EventSource(url);

es.onopen = () => console.log('OPEN');
es.onerror = (err) => { console.error('ERROR', err); es.close(); };
es.onmessage = (evt) => {
  try {
    const payload = JSON.parse(evt.data);
    console.log('MSG', JSON.stringify(payload).slice(0, 300));
    if (payload?.data?.price) {
      console.log('PRICE', payload.data.price);
    } else if (payload?.error) {
      console.error('STREAM ERROR PAYLOAD', payload);
    }
  } catch (e) {
    console.error('JSON ERROR', e);
  }
};

process.on('SIGINT', () => { es.close(); process.exit(0); });
