export async function runRLCycle() {
  const res = await fetch("https://yantrax-backend.onrender.com/run_rl_cycle");
  if (!res.ok) throw new Error("Backend returned an error");
  return await res.json();
}
