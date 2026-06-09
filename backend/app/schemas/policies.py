from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class PolicyBase(BaseModel):
    system_id: Optional[str] = None
    name: str
    description: Optional[str] = None
    conditions: dict  # who can request, under what conditions
    approvers: Optional[dict] = None  # approval chain config
    max_duration_hours: Optional[int] = None
    risk_threshold: Optional[float] = None
    auto_approve: bool = False
    is_active: bool = True


class PolicyCreate(PolicyBase):
    pass


class PolicyUpdate(BaseModel):
    system_id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    conditions: Optional[dict] = None
    approvers: Optional[dict] = None
    max_duration_hours: Optional[int] = None
    risk_threshold: Optional[float] = None
    auto_approve: Optional[bool] = None
    is_active: Optional[bool] = None


class PolicyResponse(PolicyBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PolicyList(BaseModel):
    data: list[PolicyResponse]
    count: int
