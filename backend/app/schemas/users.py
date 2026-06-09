from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    department: Optional[str] = None
    title: Optional[str] = None
    manager_id: Optional[str] = None
    status: str = "active"
    identity_provider: Optional[str] = None
    groups: list[str] = []
    risk_score: float = 0.0
    metadata: dict = {}


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    department: Optional[str] = None
    title: Optional[str] = None
    manager_id: Optional[str] = None
    status: Optional[str] = None
    identity_provider: Optional[str] = None
    groups: Optional[list[str]] = None
    risk_score: Optional[float] = None
    metadata: Optional[dict] = None


class UserResponse(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserList(BaseModel):
    data: list[UserResponse]
    count: int
