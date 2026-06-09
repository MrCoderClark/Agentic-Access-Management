from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class TicketBase(BaseModel):
    requester_id: str
    assignee_id: Optional[str] = None
    ticket_type: str  # access_request, incident, change, general
    subject: str
    description: Optional[str] = None
    status: str = "open"  # open, in_progress, waiting_approval, resolved, closed
    priority: str = "medium"  # low, medium, high, critical
    resolution: Optional[str] = None
    resolved_by: Optional[str] = None
    sla_deadline: Optional[datetime] = None
    metadata: dict = {}


class TicketCreate(BaseModel):
    requester_id: str
    assignee_id: Optional[str] = None
    ticket_type: str
    subject: str
    description: Optional[str] = None
    priority: str = "medium"
    sla_deadline: Optional[datetime] = None
    metadata: dict = {}


class TicketUpdate(BaseModel):
    assignee_id: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    resolution: Optional[str] = None
    resolved_by: Optional[str] = None
    metadata: Optional[dict] = None


class TicketResponse(TicketBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TicketList(BaseModel):
    data: list[TicketResponse]
    count: int
