// src/api/api.js

console.log("VITE_API_URL is:", import.meta.env.VITE_API_URL);

const API_URL = import.meta.env.VITE_API_URL;

// GET /god-cycle
export async function getGodCycle() {
  const res = await fetch(`${API_URL}/god-cycle`);
  if (!res.ok) throw new Error("Backend error");
  return res.json();
}

// GET /journal
export async function getJournal() {
  const res = await fetch(`${API_URL}/journal`);
  if (!res.ok) throw new Error("Backend error");
  return res.json();
}

// GET /commentary
export async function getCommentary() {
  const res = await fetch(`${API_URL}/commentary`);
  if (!res.ok) throw new Error("Backend error");
  return res.json();
}

// POST /run-cycle
export async function runRLCycle() {
  const res = await fetch(`${API_URL}/run-cycle`, { method: "POST" });
  if (!res.ok) throw new Error("Backend error");
  return res.json();
}

// GET /market-price?symbol=...
export async function getMarketPrice(symbol = "AAPL") {
  const res = await fetch(`${API_URL}/market-price?symbol=${symbol}`);
  if (!res.ok) throw new Error("Market data error");
  return res.json();
}
