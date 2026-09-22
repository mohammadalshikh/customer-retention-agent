from schemas import (
    SimulationState, CustomerState, Persona, Product, CustomerAction,
    RetentionAction, CustomerStatus, InboxMessage, TurnLogEntry,
)
from agents import take_customer_turn, investigate_and_decide

RETENTION_PREFIX = "retention:"


# ---------------------------------------------------------------------------
# Default seed data -- 3 customer archetypes, a handful of fake products.
# The Client tab is meant to let a user edit/add personas on top of this.
# ---------------------------------------------------------------------------

DEFAULT_PERSONAS = [
    Persona(
        id="alice", name="Alice", archetype="Happy Regular",
        description="A satisfied long-time subscriber who mostly just uses the product.",
        patience=0.8, price_sensitivity=0.2, loyalty=0.9, chattiness=0.3,
    ),
    Persona(
        id="bob", name="Bob", archetype="Silently Churning",
        description="Engagement has been quietly dropping; won't complain, will just leave.",
        patience=0.4, price_sensitivity=0.5, loyalty=0.3, chattiness=0.15,
    ),
    Persona(
        id="carol", name="Carol", archetype="Price Sensitive",
        description="Watches the bill closely and reacts strongly to price or value changes.",
        patience=0.5, price_sensitivity=0.9, loyalty=0.4, chattiness=0.6,
    ),
]

DEFAULT_PRODUCTS = [
    Product(id="p1", name="Pro Plan Upgrade", price=15),
    Product(id="p2", name="Extra Storage Pack", price=5),
    Product(id="p3", name="Priority Support Add-on", price=8),
]


def new_simulation() -> SimulationState:
    customers = {
        p.id: CustomerState(persona=p, ground_truth_will_churn=(p.id == "bob"))
        for p in DEFAULT_PERSONAS
    }
    state = SimulationState(
        tick=1,
        turn_index=0,
        turn_queue=list(customers.keys()),
        customers=customers,
        products=DEFAULT_PRODUCTS,
    )
    return state


def _trigger_retention(action: CustomerAction, state: CustomerState) -> bool:
    if action == CustomerAction.LEAVE:
        return True
    if action == CustomerAction.MESSAGE_SUPPORT and state.satisfaction < 0.6:
        return True
    if action == CustomerAction.GO_QUIET and state.days_since_contact >= 3:
        return True
    return False


def _apply_customer_effects(state: CustomerState, result) -> None:
    action = result.action
    state.recent_actions.append(action.value)
    state.recent_actions = state.recent_actions[-5:]

    if action == CustomerAction.ADD_TO_CART:
        if result.item:
            state.cart.append(result.item)
        state.status = CustomerStatus.ENGAGED
    elif action == CustomerAction.PURCHASE:
        state.cart = []
        state.satisfaction = min(1.0, state.satisfaction + 0.05)
        state.status = CustomerStatus.ENGAGED
        state.days_since_contact = 0
    elif action == CustomerAction.MESSAGE_SUPPORT:
        state.ticket_history.append(result.message_text or "issue reported")
        state.status = CustomerStatus.AT_RISK if state.satisfaction < 0.5 else CustomerStatus.ENGAGED
        state.days_since_contact = 0
    elif action == CustomerAction.GO_QUIET:
        state.days_since_contact += 1
        state.satisfaction = max(0.0, state.satisfaction - 0.03)
        state.status = CustomerStatus.QUIET
    elif action == CustomerAction.RENEW:
        state.satisfaction = min(1.0, state.satisfaction + 0.1)
        state.status = CustomerStatus.ENGAGED
        state.days_since_contact = 0
    elif action == CustomerAction.LEAVE:
        state.status = CustomerStatus.CHURNED
        state.satisfaction = 0.0


def _apply_retention_effects(state: CustomerState, result, tick: int) -> None:
    action = result.action
    if action == RetentionAction.DISCOUNT:
        state.satisfaction = min(1.0, state.satisfaction + 0.15)
        state.status = CustomerStatus.ENGAGED
    elif action == RetentionAction.RETENTION_EMAIL:
        state.satisfaction = min(1.0, state.satisfaction + 0.08)
    elif action == RetentionAction.ESCALATE_HUMAN:
        pass  # a human takes it from here; no automated satisfaction change
    elif action == RetentionAction.IGNORE:
        pass

    if result.message_text:
        state.inbox.append(InboxMessage(turn=tick, sender="retention_agent", text=result.message_text))


def process_next_turn(state: SimulationState) -> dict:
    """Advance exactly one actor's turn. Returns a small dict describing what
    just happened, for the frontend to animate/display."""
    if state.turn_index >= len(state.turn_queue):
        # Start a new tick.
        state.tick += 1
        state.turn_index = 0
        state.turn_queue = [cid for cid, c in state.customers.items() if c.status != CustomerStatus.CHURNED]
        if not state.turn_queue:
            state.is_complete = True
            return {"event": "simulation_complete"}

    actor = state.turn_queue[state.turn_index]

    if actor.startswith(RETENTION_PREFIX):
        customer_id = actor[len(RETENTION_PREFIX):]
        customer_state = state.customers[customer_id]
        result = investigate_and_decide(customer_id, customer_state)
        _apply_retention_effects(customer_state, result, state.tick)
        state.log.append(TurnLogEntry(tick=state.tick, actor="retention_agent", result=result.model_dump()))
        state.turn_index += 1
        return {"event": "retention_turn", "customer_id": customer_id, "result": result.model_dump()}

    customer_state = state.customers[actor]
    product_names = [p.name for p in state.products]
    result = take_customer_turn(actor, customer_state, product_names)
    _apply_customer_effects(customer_state, result)
    state.log.append(TurnLogEntry(tick=state.tick, actor=actor, result=result.model_dump()))

    if _trigger_retention(result.action, customer_state):
        state.turn_queue.append(f"{RETENTION_PREFIX}{actor}")

    state.turn_index += 1
    return {"event": "customer_turn", "customer_id": actor, "result": result.model_dump()}
