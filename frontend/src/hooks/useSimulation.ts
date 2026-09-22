import { useCallback, useRef, useState } from "react";
import { startSimulation, nextTurn } from "../api";
import type { SimulationState, TurnEvent } from "../types";

const TURN_DELAY_MS = 1500;

export function useSimulation() {
  const [state, setState] = useState<SimulationState | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [thinkingActor, setThinkingActor] = useState<string | null>(null);
  const [lastEvent, setLastEvent] = useState<TurnEvent | null>(null);

  // Refs mirror the state above so the play loop always reads the latest
  // value instead of a stale closure from when play() was first called.
  const stateRef = useRef<SimulationState | null>(null);
  const playingRef = useRef(false);

  const applyState = (s: SimulationState) => {
    stateRef.current = s;
    setState(s);
  };

  const init = useCallback(async () => {
    const s = await startSimulation();
    applyState(s);
  }, []);

  // Advances exactly one actor's turn. Returns false when the simulation
  // has nothing left to do.
  const stepOnce = useCallback(async (): Promise<boolean> => {
    const current = stateRef.current;
    if (!current || current.is_complete) return false;

    const actor = current.turn_queue[current.turn_index] ?? "starting next tick";
    setThinkingActor(actor);
    try {
      const { event, state: newState } = await nextTurn();
      setLastEvent(event);
      applyState(newState);
    } finally {
      setThinkingActor(null);
    }
    return true;
  }, []);

  const play = useCallback(async () => {
    if (playingRef.current) return;
    playingRef.current = true;
    setIsPlaying(true);

    while (playingRef.current) {
      const shouldContinue = await stepOnce();
      if (!shouldContinue || stateRef.current?.is_complete) break;
      await new Promise((r) => setTimeout(r, TURN_DELAY_MS));
    }

    playingRef.current = false;
    setIsPlaying(false);
  }, [stepOnce]);

  const pause = useCallback(() => {
    playingRef.current = false;
    setIsPlaying(false);
  }, []);

  return { state, isPlaying, thinkingActor, lastEvent, init, play, pause, stepOnce };
}
