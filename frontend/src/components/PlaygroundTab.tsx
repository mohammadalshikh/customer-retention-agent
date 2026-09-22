import type { SimulationState } from "../types";
import { CustomerCard } from "./CustomerCard";
import { TurnControls } from "./TurnControls";

interface Props {
  state: SimulationState | null;
  isPlaying: boolean;
  thinkingActor: string | null;
  onPlay: () => void;
  onPause: () => void;
  onStep: () => void;
}

export function PlaygroundTab({ state, isPlaying, thinkingActor, onPlay, onPause, onStep }: Props) {
  if (!state) return <p>Loading simulation...</p>;

  return (
    <div>
      <TurnControls
        tick={state.tick}
        isPlaying={isPlaying}
        thinkingActor={thinkingActor}
        isComplete={state.is_complete}
        onPlay={onPlay}
        onPause={onPause}
        onStep={onStep}
      />

      <div className="panel" style={{ marginBottom: 16 }}>
        <h3>Marketplace</h3>
        <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
          {state.products.map((p) => (
            <span className="chip" key={p.id} style={{ fontSize: 13, padding: "6px 12px" }}>
              {p.name} · ${p.price}
            </span>
          ))}
        </div>
      </div>

      <div className="card-grid">
        {Object.entries(state.customers).map(([id, customer]) => (
          <CustomerCard
            key={id}
            id={id}
            customer={customer}
            isThinking={thinkingActor === id}
            isRetentionThinking={thinkingActor === `retention:${id}`}
          />
        ))}
      </div>
    </div>
  );
}
