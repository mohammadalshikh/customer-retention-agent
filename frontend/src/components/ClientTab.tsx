import type { SimulationState } from "../types";

function TraitBar({ label, value }: { label: string; value: number }) {
  return (
    <div className="trait-row">
      <span className="trait-label">{label}</span>
      <div className="trait-track">
        <div className="trait-fill" style={{ width: `${value * 100}%` }} />
      </div>
    </div>
  );
}

export function ClientTab({ state }: { state: SimulationState | null }) {
  if (!state) return <p>Loading...</p>;

  return (
    <div>
      <p>
        These are the customer agent personas active in the current simulation. Traits bias each
        agent's tendencies but never dictate a fixed script — behavior still depends on how their
        situation evolves turn to turn.
      </p>
      <div className="card-grid">
        {Object.values(state.customers).map((c) => (
          <div className="panel" key={c.persona.id}>
            <h3>{c.persona.name}</h3>
            <div className="customer-archetype" style={{ marginBottom: 10 }}>{c.persona.archetype}</div>
            <p>{c.persona.description}</p>
            <TraitBar label="Patience" value={c.persona.patience} />
            <TraitBar label="Price sensitivity" value={c.persona.price_sensitivity} />
            <TraitBar label="Loyalty" value={c.persona.loyalty} />
            <TraitBar label="Chattiness" value={c.persona.chattiness} />
          </div>
        ))}
      </div>
      <p style={{ marginTop: 16, fontSize: 13 }}>
        Editing traits or adding a new persona on the fly is the natural next extension here —
        the backend already accepts arbitrary Persona objects, this tab just needs a form wired
        to a future <code>POST /personas</code> endpoint.
      </p>
    </div>
  );
}
