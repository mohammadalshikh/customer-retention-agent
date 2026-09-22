import os
import anthropic

# Cheap/fast model plays the customer agents (many calls, simple decisions).
CUSTOMER_MODEL = os.environ.get("CUSTOMER_MODEL", "claude-haiku-4-5-20251001")
# Stronger model plays the retention specialist (fewer calls, real investigation).
RETENTION_MODEL = os.environ.get("RETENTION_MODEL", "claude-sonnet-5")

_client = None


def get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _client


def call_forced_tool(
    system: str,
    messages: list[dict],
    tool: dict,
    model: str,
    timeout: float = 8.0,
    max_retries: int = 1,
) -> dict | None:
    """Call the model, forcing it to respond via the given tool.
    Returns the tool's input dict, or None if every attempt failed
    (caller must supply a safe fallback action in that case).
    """
    client = get_client().with_options(timeout=timeout)
    last_error = None
    for attempt in range(max_retries + 1):
        try:
            response = client.messages.create(
                model=model,
                max_tokens=1024,
                system=system,
                messages=messages,
                tools=[tool],
                tool_choice={"type": "tool", "name": tool["name"]},
            )
            for block in response.content:
                if block.type == "tool_use" and block.name == tool["name"]:
                    return block.input
        except Exception as e:  # noqa: BLE001 - deliberately broad, this must never crash a turn
            last_error = e
            continue
    if last_error:
        print(f"[llm_client] forced tool call failed after retries: {last_error}")
    return None


def call_agentic_loop(
    system: str,
    messages: list[dict],
    tools: list[dict],
    final_tool_name: str,
    model: str,
    timeout: float = 15.0,
    max_iterations: int = 5,
) -> tuple[dict | None, list[dict]]:
    """Run a real tool-use loop: the model can call investigation tools
    repeatedly before calling `final_tool_name` to commit its decision.

    Returns (final_tool_input | None, trace) where trace is the list of
    (tool_name, tool_input) calls made along the way, for display in the UI.
    """
    client = get_client().with_options(timeout=timeout)
    conversation = list(messages)
    trace: list[dict] = []

    for _ in range(max_iterations):
        try:
            response = client.messages.create(
                model=model,
                max_tokens=1024,
                system=system,
                messages=conversation,
                tools=tools,
            )
        except Exception as e:  # noqa: BLE001
            print(f"[llm_client] agentic loop call failed: {e}")
            return None, trace

        tool_use_blocks = [b for b in response.content if b.type == "tool_use"]
        if not tool_use_blocks:
            # Model responded with plain text instead of a tool -- nudge it once.
            conversation.append({"role": "assistant", "content": response.content})
            conversation.append({
                "role": "user",
                "content": "Please respond by calling one of your tools.",
            })
            continue

        conversation.append({"role": "assistant", "content": response.content})
        tool_results = []
        for block in tool_use_blocks:
            if block.name == final_tool_name:
                return block.input, trace
            # An investigation tool -- the caller's mock data functions live
            # in agents.py and are dispatched there; this module stays
            # domain-agnostic about what the tools actually do.
            from agents import execute_investigation_tool  # local import avoids a cycle
            result = execute_investigation_tool(block.name, block.input)
            trace.append({"tool": block.name, "input": block.input, "result": result})
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": str(result),
            })
        conversation.append({"role": "user", "content": tool_results})

    return None, trace
