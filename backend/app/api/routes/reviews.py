"""API routes for access reviews and certification campaigns."""

from __future__ import annotations

from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException

from app.agents.review_agent import review_agent

router = APIRouter(prefix="/api/v1/reviews", tags=["reviews"])


class CreateCampaignRequest(BaseModel):
    name: str | None = None
    scope: str = Field(default="all", description="'all', 'high_risk', or a system_id")
    reviewer_id: str | None = None


class ReviewDecisionRequest(BaseModel):
    grant_id: str
    decision: str = Field(..., description="'certify', 'revoke', or 'modify'")
    reviewer_id: str
    reason: str = ""


@router.post("/campaigns")
async def create_campaign(body: CreateCampaignRequest):
    """Create a new access review campaign."""
    try:
        result = await review_agent.create_campaign(
            name=body.name,
            scope=body.scope,
            reviewer_id=body.reviewer_id,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Campaign creation failed: {str(e)}")


@router.get("/stats")
async def get_review_stats():
    """Get access review statistics."""
    try:
        return await review_agent.get_review_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/decide")
async def submit_decision(body: ReviewDecisionRequest):
    """Submit a review decision for a grant."""
    if body.decision not in ("certify", "revoke", "modify"):
        raise HTTPException(status_code=400, detail="Decision must be 'certify', 'revoke', or 'modify'")

    try:
        result = await review_agent.process_decision(
            grant_id=body.grant_id,
            decision=body.decision,
            reviewer_id=body.reviewer_id,
            reason=body.reason,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
