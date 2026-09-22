import random

from schemas import (
    CustomerAction, CustomerState, CustomerTurnResult, RetentionAction,
    RetentionTurnResult, InvestigationStep,
)
from prompts import CUSTOMER_SYSTEM_PROMPT, RETENTION_SYSTEM_PROMPT
from llm_client import call_forced_tool, call_agentic_loop, CUSTOMER_MODEL, RETENTION_MODEL

# Safe fallbacks used when the model fails or times out even after a retry.
# These keep the simulation moving forward instead of freezing.
CUSTOMER_FALLBACK = CustomerAction.GO_QUIET
RETENTION_FALLBACK = RetentionAction.IGNORE


# ---------------------------------------------------------------------------
# Customer agent
# ---------------------------------------------------------------------------

CUSTOMER_TOOL = {
    "name": "take_action",
    "description": "Commit to exactly one action for this turn.",
    "input_schema": {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": [a.value for a in CustomerAction],
            },
            "reasoning": {
                "type": "string",
                "description": "One or two sentences on why you're doing this, in character.",
            },
            "item": {
                "type": "string",
                "description": "Product name, only if action is add_to_cart or purchase.",
            },
            "message_text": {
                "type": "string",
                "description": "What you say to support, only if action is message_support.",
            },
        },
        "required": ["action", "reasoning"],
    },
}


def take_customer_turn(customer_id: str, state: CustomerState, product_names: list[str]) -> CustomerTurnResult:
    system = CUSTOMER_SYSTEM_PROMPT.format(
        name=state.persona.name,
        archetype=state.persona.archetype,
        description=state.persona.description,
        patience=state.persona.patience,
        price_sensitivity=state.persona.price_sensitivity,
        loyalty=state.persona.loyalty,
        chattiness=state.persona.chattiness,
        satisfaction=round(state.satisfaction, 2),
        cart=state.cart or "empty",
        days_since_contact=state.days_since_contact,
        recent_actions=state.recent_actions[-3:] or "none yet",
        inbox_summary=[m.text for m in state.inbox[-2:]] or "none",
    )
    messages = [{
        "role": "user",
        "content": f"Available products: {product_names}. Decide your action for this turn.",
    }]

    result = call_forced_tool(system, messages, CUSTOMER_TOOL, model=CUSTOMER_MODEL)

    if result is None:
        return CustomerTurnResult(
            customer_id=customer_id,
            action=CUSTOMER_FALLBACK,
            reasoning="(fallback: agent call failed after retry, defaulted to going quiet)",
        )

    return CustomerTurnResult(
        customer_id=customer_id,
        action=CustomerAction(result["action"]),
        reasoning=result.get("reasoning", ""),
        item=result.get("item"),
        message_text=result.get("message_text"),
    )


# ---------------------------------------------------------------------------
# Retention agent -- investigation tools (mocked data, deterministic given
# the customer's own state so results stay consistent within a run) plus
# the real agentic tool-use loop.
# ---------------------------------------------------------------------------

INVESTIGATION_TOOLS = [
    {
        "name": "get_usage_trend",
        "description": "Get this customer's recent activity/engagement trend.",
        "input_schema": {"type": "object", "properties": {"customer_id": {"type": "string"}}, "required": ["customer_id"]},
    },
    {
        "name": "get_support_tickets",
        "description": "Get this customer's support ticket history.",
        "input_schema": {"type": "object", "properties": {"customer_id": {"type": "string"}}, "required": ["customer_id"]},
    },
    {
        "name": "get_contract_info",
        "description": "Get this customer's plan tier, price, and renewal date.",
        "input_schema": {"type": "object", "properties": {"customer_id": {"type": "string"}}, "required": ["customer_id"]},
    },
    {
        "name": "get_similar_past_accounts",
        "description": "Look up how similar customers behaved historically.",
        "input_schema": {"type": "object", "properties": {"customer_id": {"type": "string"}}, "required": ["customer_id"]},
    },
]

DECIDE_ACTION_TOOL = {
    "name": "decide_action",
    "description": "Commit to your final retention decision after investigating.",
    "input_schema": {
        "type": "object",
        "properties": {
            "action": {"type": "string", "enum": [a.value for a in RetentionAction]},
            "reasoning": {"type": "string", "description": "Grounded in what you found via your tools."},
            "message_text": {"type": "string", "description": "Only if action is discount or retention_email."},
        },
        "required": ["action", "reasoning"],
    },
}

# In-memory registry so execute_investigation_tool can look up live state
# without the llm_client module needing to know about SimulationState.
_active_customer_states: dict[str, CustomerState] = {}


def register_customer_state(customer_id: str, state: CustomerState) -> None:
    _active_customer_states[customer_id] = state


def execute_investigation_tool(tool_name: str, tool_input: dict) -> dict:
    """Mock data lookups the retention agent can call. Grounded in the
    customer's actual simulated state so investigation results are
    consistent with what's happening in the sim, not random noise."""
    customer_id = tool_input.get("customer_id")
    state = _active_customer_states.get(customer_id)
    if state is None:
        return {"error": "unknown customer"}

    if tool_name == "get_usage_trend":
        trend = "declining" if state.satisfaction < 0.5 else "stable"
        return {"trend": trend, "satisfaction_score": round(state.satisfaction, 2),
                "days_since_contact": state.days_since_contact}
    if tool_name == "get_support_tickets":
        return {"tickets": state.ticket_history[-5:] or ["no tickets on file"]}
    if tool_name == "get_contract_info":
        return {"tier": state.persona.archetype, "price_sensitivity": state.persona.price_sensitivity}
    if tool_name == "get_similar_past_accounts":
        # Lightweight heuristic standing in for a real historical lookup.
        similar_churn_rate = round(0.7 - state.persona.loyalty * 0.5, 2)
        return {"similar_accounts_churn_rate": similar_churn_rate}
    return {"error": f"unknown tool {tool_name}"}


def investigate_and_decide(customer_id: str, state: CustomerState) -> RetentionTurnResult:
    register_customer_state(customer_id, state)

    system = RETENTION_SYSTEM_PROMPT
    messages = [{
        "role": "user",
        "content": f"Customer {customer_id} needs review. Investigate and decide.",
    }]

    final_input, trace = call_agentic_loop(
        system, messages, INVESTIGATION_TOOLS + [DECIDE_ACTION_TOOL],
        final_tool_name="decide_action", model=RETENTION_MODEL,
    )

    steps = [InvestigationStep(tool=t["tool"], result_summary=str(t["result"])) for t in trace]

    if final_input is None:
        return RetentionTurnResult(
            customer_id=customer_id,
            investigation=steps,
            reasoning="(fallback: agent loop failed or hit iteration limit, defaulted to ignore)",
            action=RETENTION_FALLBACK,
        )

    return RetentionTurnResult(
        customer_id=customer_id,
        investigation=steps,
        reasoning=final_input.get("reasoning", ""),
        action=RetentionAction(final_input["action"]),
        message_text=final_input.get("message_text"),
    )
