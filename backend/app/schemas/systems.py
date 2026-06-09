from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class SystemBase(BaseModel):
    name: str
    display_name: Optional[str] = None
    system_type: Optional[str] = None  # saas, infrastructure, internal
    connector_type: Optional[str] = None  # okta, scim, api, manual
    risk_level: str = "low"  # low, medium, high, critical
    owner_id: Optional[str] = None
    config: dict = {}
    metadata: dict = {}


class SystemCreate(SystemBase):
    pass


class SystemUpdate(BaseModel):
    name: Optional[str] = None
    display_name: Optional[str] = None
    system_type: Optional[str] = None
    connector_type: Optional[str] = None
    risk_level: Optional[str] = None
    owner_id: Optional[str] = None
    config: Optional[dict] = None
    metadata: Optional[dict] = None


class SystemResponse(SystemBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class SystemList(BaseModel):
    data: list[SystemResponse]
    count: int
