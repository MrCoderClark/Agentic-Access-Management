"""Request Agent — parses natural language access requests into structured intent."""

from __future__ import annotations

from uuid import UUID

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.state import AccessIntent, AgentPhase, AgentState
from app.api.deps import get_supabase_client
from app.config import settings

SYSTEM_PROMPT = """You are an access request parser for an enterprise IT governance system called AgentGuard.

Given a user's natural language request, extract:
- system_name: the system/app they want access to
- permission: the role or permission level (e.g. "read", "admin", "write", "viewer", "editor")
- justification: business reason for the request
- duration_hours: how long they need access (if mentioned), as an integer

Respond in this exact JSON format (no markdown):
{"system_name": "...", "permission": "...", "justification": "...", "duration_hours": null}

If you cannot determine a field, set it to null. Always try to infer the permission level from context.
Examples:
- "I need admin access to Jira for the sprint migration" → {"system_name": "Jira", "permission": "admin", "justification": "sprint migration", "duration_hours": null}
- "Can I get read access to the production database for 2 hours?" → {"system_name": "production database", "permission": "read", "justification": "", "duration_hours": 2}
"""


async def request_agent(state: dict) -> dict:
    """Parse user message into a structured AccessIntent.

    LangGraph node function — takes and returns dict (TypedDict-style).
    """
    agent_state = AgentState(**state)
    agent_state.phase = AgentPhase.INTAKE
    agent_state.add_step("request_agent", "start", f"Parsing: {agent_state.user_message[:100]}")

    try:
        intent = await _parse_intent(agent_state.user_message, agent_state.user_id)
        agent_state.intent = intent
        agent_state.add_step(
            "request_agent",
            "parsed",
            f"system={intent.system_name}, perm={intent.permission}, conf={intent.confidence}",
        )

        # Resolve system name to system_id
        if intent.system_name and not intent.system_id:
            system_id = await _resolve_system(intent.system_name)
            if system_id:
                intent.system_id = system_id
                agent_state.add_step("request_agent", "resolved_system", str(system_id))
            else:
                agent_state.add_step("request_agent", "system_not_found", intent.system_name)

        agent_state.phase = AgentPhase.POLICY_EVAL

    except Exception as e:
        agent_state.error = f"Request parsing failed: {str(e)}"
        agent_state.phase = AgentPhase.ERROR
        agent_state.add_step("request_agent", "error", str(e))

    return agent_state.model_dump()


async def _parse_intent(message: str, user_id: UUID | None) -> AccessIntent:
    """Use LLM to extract structured intent from natural language."""
    import json

    llm = ChatOpenAI(
        model=settings.agent_model,
        api_key=settings.openai_api_key,
        temperature=0,
    )

    response = await llm.ainvoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=message),
    ])

    # Parse JSON from response
    content = response.content.strip()
    # Handle potential markdown code blocks
    if content.startswith("```"):
        content = content.split("\n", 1)[1].rsplit("```", 1)[0].strip()

    parsed = json.loads(content)

    return AccessIntent(
        user_id=user_id,
        system_name=parsed.get("system_name"),
        permission=parsed.get("permission"),
        justification=parsed.get("justification", ""),
        duration_hours=parsed.get("duration_hours"),
        confidence=0.85,  # LLM-based parsing confidence
        raw_input=message,
    )


async def _resolve_system(system_name: str) -> UUID | None:
    """Look up system by name (case-insensitive partial match)."""
    client = get_supabase_client()
    result = (
        client.schema("agentguard")
        .table("systems")
        .select("id, name")
        .ilike("name", f"%{system_name}%")
        .limit(1)
        .execute()
    )
    if result.data:
        return UUID(result.data[0]["id"])
    return None
