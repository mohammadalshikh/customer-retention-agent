export function HomeTab({ onStart }: { onStart: () => void }) {
  return (
    <div className="panel">
      <h2>Retention Agents</h2>
      <p>
        Three customer agents live in a small marketplace, each with a distinct persona.
        Every turn, one agent at a time decides how to act — browse, message support, go
        quiet, renew, or leave — based on its own evolving state, not a script.
      </p>
      <p>
        When a customer's behavior signals risk, a retention specialist agent steps in: it
        investigates using real tool calls (usage trend, support tickets, contract terms,
        similar past accounts), reasons about what it finds, and decides whether to offer a
        discount, send a retention email, escalate to a human, or do nothing.
      </p>
      <p>
        Head to <strong>Playground</strong> and press Play to watch it happen turn by turn, or
        <strong> Agent</strong> to see the retention specialist's full reasoning trail.
      </p>
      <button className="btn primary" onClick={onStart}>Start a new simulation</button>
    </div>
  );
}
