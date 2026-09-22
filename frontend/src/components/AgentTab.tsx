import type { CustomerTurnResult, RetentionTurnResult, SimulationState } from "../types";

function isRetentionResult(r: CustomerTurnResult | RetentionTurnResult): r is RetentionTurnResult {
  return "investigation" in r;
}

export function AgentTab({ state }: { state: SimulationState | null }) {
  if (!state) return <p>Loading...</p>;
  const entries = [...state.log].reverse(); // most recent first

  return (
    <div className="panel">
      <h3>Retention agent activity</h3>
      <p>Every decision the retention specialist has made, in order, with its reasoning and the tools it called to get there.</p>

      {entries.length === 0 && <p>No activity yet — press Play or Next Turn in the Playground tab.</p>}

      {entries.map((entry, i) => {
        const retention = isRetentionResult(entry.result);
        return (
          <div className={`log-entry ${retention ? "retention" : ""}`} key={i}>
            <div className="log-meta">
              tick {entry.tick} · {retention ? `retention agent → ${entry.result.customer_id}` : entry.actor}
              {!retention && ` · ${(entry.result as CustomerTurnResult).action.replace("_", " ")}`}
              {retention && ` · decided: ${(entry.result as RetentionTurnResult).action.replace("_", " ")}`}
            </div>

            {retention && (entry.result as RetentionTurnResult).investigation.length > 0 && (
              <div style={{ marginBottom: 4 }}>
                {(entry.result as RetentionTurnResult).investigation.map((step, j) => (
                  <span className="investigation-step" key={j}>{step.tool}</span>
                ))}
              </div>
            )}

            <div className="log-reasoning">{entry.result.reasoning}</div>
          </div>
        );
      })}
    </div>
  );
}
