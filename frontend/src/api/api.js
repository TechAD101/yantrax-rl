// src/api/api.js
const API_URL = import.meta.env.VITE_API_URL || "";

export async function getGodCycle() {
  const res = await fetch(`${API_URL}/god-cycle`);
  if (!res.ok) throw new Error("Backend error");
  return res.json();
}

export async function getJournal() {
  const res = await fetch(`${API_URL}/journal`);
  if (!res.ok) throw new Error("Backend error");
  return res.json();
}

export async function getCommentary() {
  const res = await fetch(`${API_URL}/commentary`);
  if (!res.ok) throw new Error("Backend error");
  return res.json();
}

export async function runRLCycle() {
  const res = await fetch(`${API_URL}/run-cycle`, { method: "POST" });
  if (!res.ok) throw new Error("Backend error");
  return res.json();
}

export async function getMarketPrice(symbol = "AAPL") {
  const res = await fetch(`${API_URL}/market-price?symbol=${symbol}`);
  if (!res.ok) throw new Error("Market data error");
  return res.json();
}
