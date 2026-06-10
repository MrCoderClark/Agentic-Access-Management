"""Policy Agent — evaluates access requests using policies and RAG context."""

from __future__ import annotations

from app.agents.state import AgentPhase, AgentState, PolicyResult
from app.services.policy_engine import policy_engine


async def policy_agent(state: dict) -> dict:
    """Evaluate the parsed intent against policies with RAG context.

    LangGraph node function.
    """
    agent_state = AgentState(**state)
    agent_state.phase = AgentPhase.POLICY_EVAL
    agent_state.add_step("policy_agent", "start", "Evaluating request against policies")

    intent = agent_state.intent
    if not intent:
        agent_state.error = "No intent available for policy evaluation"
        agent_state.phase = AgentPhase.ERROR
        agent_state.add_step("policy_agent", "error", "Missing intent")
        return agent_state.model_dump()

    if not intent.system_id:
        agent_state.policy_result = PolicyResult(
            approved=False,
            risk_score=0.8,
            reasoning=f"System '{intent.system_name}' not found in registry. Cannot evaluate.",
            confidence=0.9,
        )
        agent_state.phase = AgentPhase.COMPLETE
        agent_state.add_step("policy_agent", "denied", "System not found")
        return agent_state.model_dump()

    if not intent.permission:
        agent_state.policy_result = PolicyResult(
            approved=False,
            risk_score=0.5,
            reasoning="Could not determine the requested permission level.",
            confidence=0.7,
        )
        agent_state.phase = AgentPhase.COMPLETE
        agent_state.add_step("policy_agent", "denied", "Permission not specified")
        return agent_state.model_dump()

    try:
        decision = await policy_engine.evaluate_request(
            user_id=intent.user_id,
            system_id=intent.system_id,
            permission=intent.permission,
            justification=intent.justification,
        )

        agent_state.policy_result = PolicyResult(
            approved=decision.approved,
            risk_score=decision.risk_score,
            reasoning=decision.reasoning,
            matched_policy_id=decision.matched_policy_id,
            rag_sources=[
                {"id": s["id"], "content": s["content"][:200], "similarity": s["similarity"]}
                for s in decision.rag_sources
            ],
            confidence=decision.confidence,
        )

        agent_state.add_step(
            "policy_agent",
            "approved" if decision.approved else "denied",
            f"risk={decision.risk_score}, reason={decision.reasoning[:100]}",
        )

        # Route to provisioning if approved, otherwise complete
        if decision.approved:
            agent_state.phase = AgentPhase.PROVISIONING
        else:
            agent_state.phase = AgentPhase.COMPLETE

    except Exception as e:
        agent_state.error = f"Policy evaluation failed: {str(e)}"
        agent_state.phase = AgentPhase.ERROR
        agent_state.add_step("policy_agent", "error", str(e))

    return agent_state.model_dump()
