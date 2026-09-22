# Retention Agent

A live, turn-based simulation: 3 customer agents act inside a small marketplace, one at a time,
each deciding for itself whether to browse, message support, go quiet, renew, or leave. When a
customer's behavior signals risk, a retention specialist agent investigates — via real tool
calls, not a lookup table — and decides whether to offer a discount, send a retention email,
escalate to a human, or do nothing.

No customer agent knows the retention agent exists. It just behaves like a person in a
marketplace; the retention agent watches and reacts.

## Why this is actually agentic (not a scoring pipeline with an LLM sprinkled on top)

- **Customer agents** decide their own action each turn based on their current state (satisfaction,
  cart, days since contact, their own recent actions) — not a scripted sequence. Behavior varies
  run to run because the *situation* genuinely changes turn to turn, not because of injected
  randomness.
- **The retention agent runs a real tool-use loop** (`llm_client.call_agentic_loop`): it calls
  `get_usage_trend`, `get_support_tickets`, `get_contract_info`, `get_similar_past_accounts` as
  many times as it wants before committing to a decision via `decide_action`. That investigation
  step — deciding what to look at, not just outputting a number — is the actual agentic core.

## Reliability, so a live demo doesn't break

- Every customer turn is a **forced tool call** (`tool_choice`) — the model literally cannot
  return unparseable free text.
- Every LLM call has a **timeout + one retry + a safe fallback action** (`go_quiet` / `ignore`),
  so a slow or malformed response degrades the simulation instead of freezing it.
- State updates are atomic — a turn either fully resolves or falls back; nothing is left
  half-applied.

## Setup

### Backend
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env    # fill .env
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev             # http://localhost:5173
```

JSONBin is optional — the app runs entirely in-memory if `JSONBIN_BIN_ID`/`JSONBIN_API_KEY`
are left unset in `.env`.

**Built:**
- Full turn-based orchestration (one actor at a time, retention triggers queued dynamically)
- Customer agent decision loop with forced structured output
- Retention agent investigation loop with real tool use
- Live Playground (marketplace + customer state), Agent reasoning timeline, Client persona view
- Reliability layer (timeout/retry/fallback) end to end

## Stack

- Python (FastAPI, Anthropic SDK, Pydantic) 
- TypeScript (React, Vite)
