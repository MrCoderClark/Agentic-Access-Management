from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AuditEventCreate(BaseModel):
    actor: str  # user id, agent name, or 'system'
    actor_type: str  # user, agent, system
    action: str  # access_granted, access_revoked, policy_evaluated, etc.
    target_type: Optional[str] = None  # user, system, policy, ticket
    target_id: Optional[str] = None
    decision: Optional[str] = None  # approved, denied, escalated
    reasoning: Optional[str] = None
    confidence: Optional[float] = None
    rag_sources: Optional[dict] = None
    metadata: dict = {}


class AuditEventResponse(BaseModel):
    id: str
    actor: str
    actor_type: str
    action: str
    target_type: Optional[str] = None
    target_id: Optional[str] = None
    decision: Optional[str] = None
    reasoning: Optional[str] = None
    confidence: Optional[float] = None
    rag_sources: Optional[dict] = None
    metadata: dict = {}
    created_at: datetime

    class Config:
        from_attributes = True


class AuditEventList(BaseModel):
    data: list[AuditEventResponse]
    count: int
