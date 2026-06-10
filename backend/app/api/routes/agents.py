"""API routes for the AI agent pipeline."""

from __future__ import annotations

from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException

from app.agents.orchestrator import run_agent_pipeline

router = APIRouter(prefix="/api/v1/agents", tags=["agents"])


class AgentRequest(BaseModel):
    message: str = Field(..., min_length=1, description="Natural language access request")
    user_id: str | None = Field(default=None, description="UUID of the requesting user")


class AgentResponse(BaseModel):
    response: str
    phase: str
    steps: list[dict]
    intent: dict | None = None
    policy_result: dict | None = None
    provisioning_result: dict | None = None
    error: str | None = None


@router.post("/run", response_model=AgentResponse)
async def run_agent(body: AgentRequest):
    """Run the AI agent pipeline with a natural language access request.

    The pipeline:
    1. Request Agent: parses intent from NL
    2. Policy Agent: evaluates against policies + RAG
    3. Provisioning Agent: creates grants/tickets if approved
    4. Respond: generates user-facing explanation
    """
    try:
        result = await run_agent_pipeline(
            user_message=body.message,
            user_id=body.user_id,
        )

        return AgentResponse(
            response=result.get("response", ""),
            phase=result.get("phase", "error"),
            steps=result.get("steps", []),
            intent=result.get("intent"),
            policy_result=result.get("policy_result"),
            provisioning_result=result.get("provisioning_result"),
            error=result.get("error"),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent pipeline error: {str(e)}")


@router.get("/status")
async def agent_status():
    """Health check for the agent system."""
    from app.agents.orchestrator import get_agent_graph

    try:
        graph = get_agent_graph()
        return {
            "status": "operational",
            "graph_nodes": list(graph.get_graph().nodes.keys()) if hasattr(graph, "get_graph") else [],
        }
    except Exception as e:
        return {"status": "error", "detail": str(e)}


@router.post("/sentinel/scan")
async def run_sentinel_scan():
    """Run the Sentinel Agent to scan for governance issues.

    Checks:
    - Expired grants (auto-revokes them)
    - Unused grants (>30 days inactive)
    - Policy drift (grants exceeding current thresholds)
    """
    from app.agents.sentinel_agent import sentinel_agent

    try:
        result = await sentinel_agent.run_full_scan()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sentinel scan failed: {str(e)}")


@router.post("/oversight/audit")
async def run_oversight_audit(limit: int = 20):
    """Run the Oversight Agent to review recent agent decisions.

    Checks for:
    - High-risk approvals without escalation
    - Elevated privilege grants
    - Pattern anomalies
    """
    from app.agents.oversight_agent import oversight_agent

    try:
        result = await oversight_agent.audit_recent_decisions(limit=limit)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Oversight audit failed: {str(e)}")
