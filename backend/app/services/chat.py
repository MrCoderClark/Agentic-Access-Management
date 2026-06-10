"""Chat service — conversational RAG for employee self-service."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from app.config import settings
from app.services.rag import rag_service


SYSTEM_PROMPT = """You are AgentGuard Assistant, an AI helper for enterprise access governance.

You help employees with:
- Answering questions about access policies, security procedures, and compliance
- Explaining how to request access to systems
- Providing information from the organization's knowledge base (policies, runbooks, decisions)
- Guiding users through the access request process

When answering questions:
1. Use the provided context from the knowledge base when available
2. Be concise and helpful
3. If you don't have enough information, say so clearly
4. For access requests, suggest using the Agent pipeline (/dashboard/agents)
5. Always cite which document type your answer comes from when using KB context

You are NOT able to directly grant or modify access. Direct users to submit a request if they need access changes.
"""


class ChatMessage:
    """A single message in a conversation."""

    def __init__(self, role: str, content: str, sources: list[dict] | None = None):
        self.role = role
        self.content = content
        self.sources = sources or []
        self.timestamp = datetime.now(timezone.utc).isoformat()


class ChatSession:
    """In-memory chat session with message history."""

    def __init__(self, session_id: str | None = None, user_id: str | None = None):
        self.session_id = session_id or str(uuid4())
        self.user_id = user_id
        self.messages: list[ChatMessage] = []
        self.created_at = datetime.now(timezone.utc).isoformat()

    def add_message(self, role: str, content: str, sources: list[dict] | None = None):
        self.messages.append(ChatMessage(role=role, content=content, sources=sources))

    def get_history(self, max_messages: int = 10) -> list[dict]:
        """Get recent message history for context."""
        recent = self.messages[-max_messages:]
        return [{"role": m.role, "content": m.content} for m in recent]


# In-memory session store (replace with Redis/DB in production)
_sessions: dict[str, ChatSession] = {}


def get_or_create_session(session_id: str | None = None, user_id: str | None = None) -> ChatSession:
    """Get existing session or create a new one."""
    if session_id and session_id in _sessions:
        return _sessions[session_id]
    session = ChatSession(session_id=session_id, user_id=user_id)
    _sessions[session.session_id] = session
    return session


async def chat_with_rag(
    message: str,
    session_id: str | None = None,
    user_id: str | None = None,
) -> dict:
    """Process a chat message with RAG context retrieval.

    1. Search knowledge base for relevant context
    2. Build prompt with context + conversation history
    3. Generate response via LLM
    4. Return response with sources

    Returns:
        Dict with response, sources, and session_id.
    """
    session = get_or_create_session(session_id, user_id)
    session.add_message("user", message)

    # RAG retrieval
    rag_results = await rag_service.search_multi(
        query=message,
        match_count=5,
        doc_types=["policy", "runbook", "decision", "system_doc", "compliance"],
        similarity_threshold=0.3,
    )

    # Build context from RAG results
    context_parts = []
    sources = []
    for r in rag_results:
        context_parts.append(f"[{r['doc_type']}] {r['content']}")
        sources.append({
            "id": r["id"],
            "doc_type": r["doc_type"],
            "content": r["content"][:200],
            "similarity": r["similarity"],
        })

    context_str = "\n\n".join(context_parts) if context_parts else "No relevant documents found in the knowledge base."

    # Build LLM messages
    llm_messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        SystemMessage(content=f"Knowledge Base Context:\n{context_str}"),
    ]

    # Add conversation history (last 6 messages for context)
    history = session.get_history(max_messages=6)
    for msg in history[:-1]:  # Exclude the current message (already added)
        if msg["role"] == "user":
            llm_messages.append(HumanMessage(content=msg["content"]))
        else:
            llm_messages.append(AIMessage(content=msg["content"]))

    llm_messages.append(HumanMessage(content=message))

    # Generate response
    llm = ChatOpenAI(
        model=settings.agent_model,
        api_key=settings.openai_api_key,
        temperature=0.3,
    )

    response = await llm.ainvoke(llm_messages)
    assistant_content = response.content.strip()

    session.add_message("assistant", assistant_content, sources=sources)

    return {
        "response": assistant_content,
        "sources": sources,
        "session_id": session.session_id,
        "message_count": len(session.messages),
    }
