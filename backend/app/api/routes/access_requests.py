"""API routes for access request submission and evaluation."""

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException

from app.api.deps import get_supabase_client
from app.schemas.access_request import AccessRequestSubmit, AccessRequestDecision
from app.services.policy_engine import policy_engine

router = APIRouter(prefix="/api/v1/access-requests", tags=["access-requests"])


@router.post("/evaluate", response_model=AccessRequestDecision)
async def evaluate_access_request(body: AccessRequestSubmit):
    """Evaluate an access request against policies and return decision.

    This does NOT auto-provision — it evaluates and creates a ticket.
    If auto-approved, it also creates a grant.
    """
    try:
        decision = await policy_engine.evaluate_request(
            user_id=body.user_id,
            system_id=body.system_id,
            permission=body.permission,
            justification=body.justification,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Policy evaluation failed: {str(e)}")

    client = get_supabase_client()
    schema = "agentguard"

    # Create ticket for tracking
    ticket_data = {
        "requester_id": str(body.user_id),
        "ticket_type": "access_request",
        "subject": f"Access request: {body.permission} on system",
        "description": body.justification or "No justification provided",
        "status": "resolved" if decision.approved else "waiting_approval",
        "priority": "high" if decision.risk_score > 0.7 else "medium" if decision.risk_score > 0.4 else "low",
        "metadata": {
            "system_id": str(body.system_id),
            "permission": body.permission,
            "risk_score": decision.risk_score,
            "policy_id": str(decision.matched_policy_id) if decision.matched_policy_id else None,
        },
    }

    ticket_result = (
        client.schema(schema)
        .table("tickets")
        .insert(ticket_data)
        .execute()
    )
    ticket_id = ticket_result.data[0]["id"] if ticket_result.data else None

    # If auto-approved, create grant
    grant_id = None
    if decision.approved:
        expires_at = None
        if body.duration_hours:
            expires_at = (datetime.now(timezone.utc) + timedelta(hours=body.duration_hours)).isoformat()

        grant_data = {
            "user_id": str(body.user_id),
            "system_id": str(body.system_id),
            "permission": body.permission,
            "status": "active",
            "granted_by": "policy_engine",
            "granted_at": datetime.now(timezone.utc).isoformat(),
            "expires_at": expires_at,
            "risk_score": decision.risk_score,
            "ticket_id": ticket_id,
            "metadata": {
                "auto_approved": True,
                "policy_id": str(decision.matched_policy_id) if decision.matched_policy_id else None,
                "confidence": decision.confidence,
            },
        }

        grant_result = (
            client.schema(schema)
            .table("access_grants")
            .insert(grant_data)
            .execute()
        )
        grant_id = grant_result.data[0]["id"] if grant_result.data else None

    # Log audit event
    audit_data = {
        "actor": "policy_engine",
        "actor_type": "system",
        "action": "access_request.evaluated",
        "target_type": "access_grant" if grant_id else "ticket",
        "target_id": grant_id or ticket_id,
        "decision": "approved" if decision.approved else "pending_approval",
        "reasoning": decision.reasoning,
        "confidence": decision.confidence,
        "rag_sources": decision.rag_sources,
        "metadata": {
            "user_id": str(body.user_id),
            "system_id": str(body.system_id),
            "permission": body.permission,
            "risk_score": decision.risk_score,
        },
    }

    client.schema(schema).table("audit_events").insert(audit_data).execute()

    return AccessRequestDecision(
        approved=decision.approved,
        risk_score=decision.risk_score,
        reasoning=decision.reasoning,
        matched_policy_id=decision.matched_policy_id,
        rag_sources=decision.rag_sources,
        confidence=decision.confidence,
        ticket_id=ticket_id,
        grant_id=grant_id,
    )
