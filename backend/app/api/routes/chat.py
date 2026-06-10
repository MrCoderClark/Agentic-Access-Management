"""API routes for the conversational chat interface."""

from __future__ import annotations

import time
from collections import defaultdict

from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException

from app.services.chat import chat_with_rag, get_or_create_session, _sessions

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])

# Simple in-memory rate limiter
_rate_limits: dict[str, list[float]] = defaultdict(list)
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX = 20  # requests per window


def _check_rate_limit(client_id: str) -> bool:
    """Check if client has exceeded rate limit."""
    now = time.time()
    window_start = now - RATE_LIMIT_WINDOW
    # Remove old entries
    _rate_limits[client_id] = [t for t in _rate_limits[client_id] if t > window_start]
    if len(_rate_limits[client_id]) >= RATE_LIMIT_MAX:
        return False
    _rate_limits[client_id].append(now)
    return True


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, description="User message")
    session_id: str | None = Field(default=None, description="Session ID for conversation continuity")
    user_id: str | None = Field(default=None, description="User UUID")


class ChatSource(BaseModel):
    id: str
    doc_type: str
    content: str
    similarity: float


class ChatResponse(BaseModel):
    response: str
    sources: list[ChatSource]
    session_id: str
    message_count: int


class ChatHistoryMessage(BaseModel):
    role: str
    content: str


class ChatHistoryResponse(BaseModel):
    session_id: str
    messages: list[ChatHistoryMessage]
    message_count: int


@router.post("/message", response_model=ChatResponse)
async def send_message(body: ChatRequest):
    """Send a message to the conversational RAG assistant.

    The assistant answers questions using the knowledge base (policies,
    runbooks, compliance docs) and maintains conversation context via
    session_id.
    """
    # Rate limiting
    client_id = body.user_id or "anonymous"
    if not _check_rate_limit(client_id):
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Max {RATE_LIMIT_MAX} messages per {RATE_LIMIT_WINDOW}s.",
        )

    try:
        result = await chat_with_rag(
            message=body.message,
            session_id=body.session_id,
            user_id=body.user_id,
        )

        return ChatResponse(
            response=result["response"],
            sources=[ChatSource(**s) for s in result["sources"]],
            session_id=result["session_id"],
            message_count=result["message_count"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


@router.get("/history/{session_id}", response_model=ChatHistoryResponse)
async def get_history(session_id: str):
    """Get conversation history for a session."""
    if session_id not in _sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = _sessions[session_id]
    return ChatHistoryResponse(
        session_id=session.session_id,
        messages=[
            ChatHistoryMessage(role=m.role, content=m.content)
            for m in session.messages
        ],
        message_count=len(session.messages),
    )


@router.delete("/history/{session_id}")
async def clear_history(session_id: str):
    """Clear a conversation session."""
    if session_id in _sessions:
        del _sessions[session_id]
    return {"status": "cleared"}
