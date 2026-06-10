"""Schemas for access request evaluation."""

from uuid import UUID

from pydantic import BaseModel, Field


class AccessRequestSubmit(BaseModel):
    user_id: UUID
    system_id: UUID
    permission: str = Field(..., min_length=1, description="Requested permission/role")
    justification: str = Field(default="", description="Business justification")
    duration_hours: int | None = Field(default=None, ge=1, le=8760, description="Requested access duration in hours")


class AccessRequestDecision(BaseModel):
    approved: bool
    risk_score: float
    reasoning: str
    matched_policy_id: UUID | None
    rag_sources: list[dict]
    confidence: float
    ticket_id: UUID | None = None
    grant_id: UUID | None = None
