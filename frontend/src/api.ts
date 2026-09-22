import type { SimulationState, TurnEvent } from "./types";

const BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export async function startSimulation(): Promise<SimulationState> {
  const res = await fetch(`${BASE_URL}/simulation/start`, { method: "POST" });
  if (!res.ok) throw new Error("Failed to start simulation");
  return res.json();
}

export async function getState(): Promise<SimulationState> {
  const res = await fetch(`${BASE_URL}/simulation/state`);
  if (!res.ok) throw new Error("Failed to fetch state");
  return res.json();
}

export async function nextTurn(): Promise<{ event: TurnEvent; state: SimulationState }> {
  const res = await fetch(`${BASE_URL}/simulation/next-turn`, { method: "POST" });
  if (!res.ok) throw new Error("Failed to advance turn");
  return res.json();
}
