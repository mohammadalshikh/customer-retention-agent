import type { CustomerState } from "../types";

interface Props {
  id: string;
  customer: CustomerState;
  isThinking: boolean;
  isRetentionThinking: boolean;
}

export function CustomerCard({ id, customer, isThinking, isRetentionThinking }: Props) {
  const lastMessage = customer.inbox[customer.inbox.length - 1];
  const cardClass = [
    "customer-card",
    isThinking ? "thinking" : "",
    isRetentionThinking ? "retention-thinking" : "",
  ].join(" ").trim();

  return (
    <div className={cardClass}>
      <div className="customer-header">
        <div>
          <div className="customer-name">{customer.persona.name}</div>
          <div className="customer-archetype">{customer.persona.archetype}</div>
        </div>
        <span className={`status-badge ${customer.status}`}>{customer.status.replace("_", " ")}</span>
      </div>

      <div className="satisfaction-bar">
        <div className="satisfaction-fill" style={{ width: `${customer.satisfaction * 100}%` }} />
      </div>

      <div>
        {customer.cart.length === 0 ? (
          <span className="chip">cart empty</span>
        ) : (
          customer.cart.map((item, i) => <span className="chip" key={i}>{item}</span>)
        )}
      </div>

      {lastMessage && (
        <div className="inbox-msg">
          <strong style={{ fontSize: 11, color: "var(--text-dim)" }}>{lastMessage.sender}</strong>
          <div>{lastMessage.text}</div>
        </div>
      )}

      {isRetentionThinking && (
        <div className="thinking-indicator" style={{ marginTop: 8 }}>
          <span className="dot" /> retention agent investigating...
        </div>
      )}
    </div>
  );
}
