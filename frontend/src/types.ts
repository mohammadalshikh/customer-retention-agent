export type CustomerAction =
  | "add_to_cart" | "purchase" | "message_support" | "go_quiet" | "renew" | "leave";

export type RetentionAction = "discount" | "retention_email" | "escalate_human" | "ignore";

export type CustomerStatus = "browsing" | "engaged" | "at_risk" | "quiet" | "churned";

export interface Persona {
  id: string;
  name: string;
  archetype: string;
  description: string;
  patience: number;
  price_sensitivity: number;
  loyalty: number;
  chattiness: number;
}

export interface InboxMessage {
  turn: number;
  sender: "customer" | "retention_agent" | "support";
  text: string;
}

export interface CustomerState {
  persona: Persona;
  satisfaction: number;
  cart: string[];
  status: CustomerStatus;
  days_since_contact: number;
  inbox: InboxMessage[];
  recent_actions: string[];
  ticket_history: string[];
  ground_truth_will_churn: boolean;
}

export interface CustomerTurnResult {
  customer_id: string;
  action: CustomerAction;
  reasoning: string;
  item?: string | null;
  message_text?: string | null;
}

export interface InvestigationStep {
  tool: string;
  result_summary: string;
}

export interface RetentionTurnResult {
  customer_id: string;
  investigation: InvestigationStep[];
  reasoning: string;
  action: RetentionAction;
  message_text?: string | null;
}

export interface Product {
  id: string;
  name: string;
  price: number;
}

export interface TurnLogEntry {
  tick: number;
  actor: string;
  result: CustomerTurnResult | RetentionTurnResult;
}

export interface SimulationState {
  tick: number;
  turn_index: number;
  turn_queue: string[];
  customers: Record<string, CustomerState>;
  products: Product[];
  log: TurnLogEntry[];
  is_complete: boolean;
}

export interface TurnEvent {
  event: "customer_turn" | "retention_turn" | "simulation_complete";
  customer_id?: string;
  result?: CustomerTurnResult | RetentionTurnResult;
}
