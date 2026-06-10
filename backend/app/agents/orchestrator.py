"""Agent Orchestrator — LangGraph-based pipeline for access request processing."""

from __future__ import annotations

from typing import Any

from langgraph.graph import StateGraph, END

from app.agents.state import AgentPhase, AgentState
from app.agents.request_agent import request_agent
from app.agents.policy_agent import policy_agent
from app.agents.provisioning_agent import provisioning_agent


def _route_after_intake(state: dict) -> str:
    """Route after the request agent based on phase."""
    phase = state.get("phase", AgentPhase.ERROR)
    if phase == AgentPhase.POLICY_EVAL:
        return "policy_agent"
    return "respond"


def _route_after_policy(state: dict) -> str:
    """Route after policy evaluation."""
    phase = state.get("phase", AgentPhase.ERROR)
    if phase == AgentPhase.PROVISIONING:
        return "provisioning_agent"
    return "respond"


def _route_after_provisioning(state: dict) -> str:
    """Always go to respond after provisioning."""
    return "respond"


async def respond(state: dict) -> dict:
    """Generate final user-facing response based on pipeline results."""
    agent_state = AgentState(**state)

    if agent_state.error:
        agent_state.response = f"I couldn't process your request: {agent_state.error}"
        return agent_state.model_dump()

    intent = agent_state.intent
    policy_result = agent_state.policy_result
    prov = agent_state.provisioning_result

    if prov and prov.success and prov.grant_id:
        # Access was granted
        agent_state.response = (
            f"✓ Access granted! I've approved {intent.permission} access to "
            f"{intent.system_name}."
        )
        if intent.duration_hours:
            agent_state.response += f" This grant expires in {intent.duration_hours} hours."
        agent_state.response += f"\n\nRisk score: {policy_result.risk_score:.2f}"
        if policy_result.reasoning:
            agent_state.response += f"\nReason: {policy_result.reasoning}"

    elif prov and prov.ticket_id:
        # Ticket created, awaiting approval
        agent_state.response = (
            f"⏳ Your request for {intent.permission} access to "
            f"{intent.system_name} requires manual approval.\n\n"
            f"A ticket has been created (#{str(prov.ticket_id)[:8]}).\n"
            f"Risk score: {policy_result.risk_score:.2f}\n"
            f"Reason: {policy_result.reasoning}"
        )

    elif policy_result and not policy_result.approved:
        # Denied without ticket (system not found, etc.)
        agent_state.response = (
            f"✗ Request cannot be fulfilled: {policy_result.reasoning}"
        )

    elif intent and not intent.system_id:
        agent_state.response = (
            f"I couldn't find a system matching '{intent.system_name}' in our registry. "
            f"Please check the system name and try again."
        )

    else:
        agent_state.response = "I wasn't able to process your request. Please try again with more details."

    return agent_state.model_dump()


def build_agent_graph() -> StateGraph:
    """Construct the LangGraph state graph for the agent pipeline."""
    graph = StateGraph(dict)

    # Add nodes
    graph.add_node("request_agent", request_agent)
    graph.add_node("policy_agent", policy_agent)
    graph.add_node("provisioning_agent", provisioning_agent)
    graph.add_node("respond", respond)

    # Set entry point
    graph.set_entry_point("request_agent")

    # Conditional edges
    graph.add_conditional_edges("request_agent", _route_after_intake)
    graph.add_conditional_edges("policy_agent", _route_after_policy)
    graph.add_conditional_edges("provisioning_agent", _route_after_provisioning)

    # respond → END
    graph.add_edge("respond", END)

    return graph


# Compiled graph singleton
_compiled_graph = None


def get_agent_graph():
    """Get or create the compiled agent graph."""
    global _compiled_graph
    if _compiled_graph is None:
        graph = build_agent_graph()
        _compiled_graph = graph.compile()
    return _compiled_graph


async def run_agent_pipeline(
    user_message: str,
    user_id: str | None = None,
) -> dict[str, Any]:
    """Run the full agent pipeline for an access request.

    Args:
        user_message: Natural language request from user.
        user_id: UUID of the requesting user.

    Returns:
        Final agent state dict with response, steps, and results.
    """
    from uuid import UUID

    graph = get_agent_graph()

    initial_state = AgentState(
        user_message=user_message,
        user_id=UUID(user_id) if user_id else None,
    ).model_dump()

    # Run the graph
    result = await graph.ainvoke(initial_state)

    return result
