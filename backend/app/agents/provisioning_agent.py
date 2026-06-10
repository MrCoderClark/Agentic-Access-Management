"""Provisioning Agent — creates grants and tickets based on policy decisions."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.agents.state import AgentPhase, AgentState, ProvisioningResult
from app.api.deps import get_supabase_client


async def provisioning_agent(state: dict) -> dict:
    """Create the actual grant and ticket records.

    LangGraph node function.
    """
    agent_state = AgentState(**state)
    agent_state.phase = AgentPhase.PROVISIONING
    agent_state.add_step("provisioning_agent", "start", "Creating grant and ticket")

    intent = agent_state.intent
    policy_result = agent_state.policy_result

    if not intent or not policy_result:
        agent_state.error = "Missing intent or policy result"
        agent_state.phase = AgentPhase.ERROR
        return agent_state.model_dump()

    client = get_supabase_client()
    schema = "agentguard"

    try:
        # Create ticket
        ticket_data = {
            "requester_id": str(intent.user_id),
            "ticket_type": "access_request",
            "subject": f"Access request: {intent.permission} on {intent.system_name}",
            "description": intent.justification or "Agent-processed request",
            "status": "resolved" if policy_result.approved else "waiting_approval",
            "priority": _risk_to_priority(policy_result.risk_score),
            "metadata": {
                "system_id": str(intent.system_id),
                "permission": intent.permission,
                "risk_score": policy_result.risk_score,
                "agent_processed": True,
                "policy_id": str(policy_result.matched_policy_id) if policy_result.matched_policy_id else None,
            },
        }

        ticket_result = (
            client.schema(schema)
            .table("tickets")
            .insert(ticket_data)
            .execute()
        )
        ticket_id = ticket_result.data[0]["id"] if ticket_result.data else None

        agent_state.add_step("provisioning_agent", "ticket_created", ticket_id or "failed")

        # Create grant if approved
        grant_id = None
        if policy_result.approved and intent.system_id:
            expires_at = None
            if intent.duration_hours:
                expires_at = (
                    datetime.now(timezone.utc) + timedelta(hours=intent.duration_hours)
                ).isoformat()

            grant_data = {
                "user_id": str(intent.user_id),
                "system_id": str(intent.system_id),
                "permission": intent.permission,
                "status": "active",
                "granted_by": "agent_pipeline",
                "granted_at": datetime.now(timezone.utc).isoformat(),
                "expires_at": expires_at,
                "risk_score": policy_result.risk_score,
                "ticket_id": ticket_id,
                "metadata": {
                    "auto_approved": True,
                    "agent_processed": True,
                    "policy_id": str(policy_result.matched_policy_id) if policy_result.matched_policy_id else None,
                    "confidence": policy_result.confidence,
                },
            }

            grant_result = (
                client.schema(schema)
                .table("access_grants")
                .insert(grant_data)
                .execute()
            )
            grant_id = grant_result.data[0]["id"] if grant_result.data else None
            agent_state.add_step("provisioning_agent", "grant_created", grant_id or "failed")

        # Log audit event
        audit_data = {
            "actor": "agent_pipeline",
            "actor_type": "system",
            "action": "access_request.agent_processed",
            "target_type": "access_grant" if grant_id else "ticket",
            "target_id": grant_id or ticket_id,
            "decision": "approved" if policy_result.approved else "pending_approval",
            "reasoning": policy_result.reasoning,
            "confidence": policy_result.confidence,
            "rag_sources": policy_result.rag_sources,
            "metadata": {
                "user_id": str(intent.user_id),
                "system_id": str(intent.system_id),
                "permission": intent.permission,
                "risk_score": policy_result.risk_score,
                "steps": agent_state.steps,
            },
        }
        client.schema(schema).table("audit_events").insert(audit_data).execute()

        agent_state.provisioning_result = ProvisioningResult(
            success=True,
            grant_id=grant_id,
            ticket_id=ticket_id,
            message="Access granted" if grant_id else "Ticket created — awaiting approval",
        )
        agent_state.phase = AgentPhase.COMPLETE
        agent_state.add_step("provisioning_agent", "complete", "Success")

    except Exception as e:
        agent_state.error = f"Provisioning failed: {str(e)}"
        agent_state.phase = AgentPhase.ERROR
        agent_state.add_step("provisioning_agent", "error", str(e))

    return agent_state.model_dump()


def _risk_to_priority(risk_score: float) -> str:
    """Convert risk score to ticket priority."""
    if risk_score > 0.7:
        return "high"
    elif risk_score > 0.4:
        return "medium"
    return "low"
