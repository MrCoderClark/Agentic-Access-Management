from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class GrantBase(BaseModel):
    user_id: str
    system_id: str
    permission: str
    status: str = "pending"  # pending, active, expired, revoked
    granted_by: Optional[str] = None
    justification: Optional[str] = None
    risk_score: Optional[float] = None
    granted_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    revoked_at: Optional[datetime] = None
    request_id: Optional[str] = None
    metadata: dict = {}


class GrantCreate(BaseModel):
    user_id: str
    system_id: str
    permission: str
    granted_by: Optional[str] = None
    justification: Optional[str] = None
    risk_score: Optional[float] = None
    expires_at: Optional[datetime] = None
    request_id: Optional[str] = None
    metadata: dict = {}


class GrantUpdate(BaseModel):
    status: Optional[str] = None
    granted_by: Optional[str] = None
    granted_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    revoked_at: Optional[datetime] = None
    metadata: Optional[dict] = None


class GrantResponse(GrantBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class GrantList(BaseModel):
    data: list[GrantResponse]
    count: int
