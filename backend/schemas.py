from __future__ import annotations
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Actions each agent type is allowed to take. Keeping these as closed enums
# (rather than free text) is what makes every turn safe to render in the UI.
# ---------------------------------------------------------------------------

class CustomerAction(str, Enum):
    ADD_TO_CART = "add_to_cart"
    PURCHASE = "purchase"
    MESSAGE_SUPPORT = "message_support"
    GO_QUIET = "go_quiet"
    RENEW = "renew"
    LEAVE = "leave"


class RetentionAction(str, Enum):
    DISCOUNT = "discount"
    RETENTION_EMAIL = "retention_email"
    ESCALATE_HUMAN = "escalate_human"
    IGNORE = "ignore"


# ---------------------------------------------------------------------------
# Persona: defines who a customer agent *is*. Traits shape behavior but never
# force a specific action -- the agent still decides each turn based on its
# current state, which is what produces natural variability run to run.
# ---------------------------------------------------------------------------

class Persona(BaseModel):
    id: str
    name: str
    archetype: str  # e.g. "Silently Churning", "Price Sensitive", "Happy Regular"
    description: str
    patience: float = Field(ge=0, le=1)          # low = frustrates fast
    price_sensitivity: float = Field(ge=0, le=1)  # high = reacts strongly to discounts
    loyalty: float = Field(ge=0, le=1)            # high = takes more to lose
    chattiness: float = Field(ge=0, le=1)         # high = messages support more


# ---------------------------------------------------------------------------
# Live state per customer. This is what actually changes turn to turn and is
# what the agent reasons over -- it is the reason behavior varies even though
# the persona itself is fixed.
# ---------------------------------------------------------------------------

class CustomerStatus(str, Enum):
    BROWSING = "browsing"
    ENGAGED = "engaged"
    AT_RISK = "at_risk"
    QUIET = "quiet"
    CHURNED = "churned"


class InboxMessage(BaseModel):
    turn: int
    sender: str          # "customer" | "retention_agent" | "support"
    text: str


class CustomerState(BaseModel):
    persona: Persona
    satisfaction: float = Field(ge=0, le=1, default=0.7)
    cart: list[str] = Field(default_factory=list)
    status: CustomerStatus = CustomerStatus.BROWSING
    days_since_contact: int = 0
    inbox: list[InboxMessage] = Field(default_factory=list)
    # Short rolling memory of the customer's OWN past actions -- given back
    # to the agent each turn so it can avoid mechanically repeating itself.
    recent_actions: list[str] = Field(default_factory=list)
    ticket_history: list[str] = Field(default_factory=list)
    ground_truth_will_churn: bool = False  # hidden from the agent, used only for eval


# ---------------------------------------------------------------------------
# What a single agent turn returns. `reasoning` is always populated -- it's
# the thing the Agent tab actually displays.
# ---------------------------------------------------------------------------

class CustomerTurnResult(BaseModel):
    customer_id: str
    action: CustomerAction
    reasoning: str
    item: Optional[str] = None      # for add_to_cart / purchase
    message_text: Optional[str] = None  # for message_support


class InvestigationStep(BaseModel):
    tool: str
    result_summary: str


class RetentionTurnResult(BaseModel):
    customer_id: str
    investigation: list[InvestigationStep]
    reasoning: str
    action: RetentionAction
    message_text: Optional[str] = None


# ---------------------------------------------------------------------------
# Simulation-wide state, what gets persisted to JSONBin after every turn.
# ---------------------------------------------------------------------------

class Product(BaseModel):
    id: str
    name: str
    price: float


class TurnLogEntry(BaseModel):
    tick: int
    actor: str  # customer_id or "retention_agent"
    result: dict  # serialized CustomerTurnResult | RetentionTurnResult


class SimulationState(BaseModel):
    tick: int = 0
    turn_index: int = 0  # position within this tick's turn queue
    turn_queue: list[str] = Field(default_factory=list)  # actor ids for this tick
    customers: dict[str, CustomerState] = Field(default_factory=dict)
    products: list[Product] = Field(default_factory=list)
    log: list[TurnLogEntry] = Field(default_factory=list)
    is_complete: bool = False
