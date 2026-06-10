"""Agent state definitions for the LangGraph orchestrator."""

from __future__ import annotations

from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class AgentPhase(str, Enum):
    """Phases of the agent pipeline."""

    INTAKE = "intake"
    POLICY_EVAL = "policy_eval"
    PROVISIONING = "provisioning"
    COMPLETE = "complete"
    ERROR = "error"


class AccessIntent(BaseModel):
    """Parsed intent from a natural language access request."""

    user_id: UUID | None = None
    system_name: str | None = None
    system_id: UUID | None = None
    permission: str | None = None
    justification: str = ""
    duration_hours: int | None = None
    confidence: float = 0.0
    raw_input: str = ""


class PolicyResult(BaseModel):
    """Result of policy evaluation."""

    approved: bool = False
    risk_score: float = 0.5
    reasoning: str = ""
    matched_policy_id: UUID | None = None
    rag_sources: list[dict] = Field(default_factory=list)
    confidence: float = 0.0


class ProvisioningResult(BaseModel):
    """Result of provisioning action."""

    success: bool = False
    grant_id: UUID | None = None
    ticket_id: UUID | None = None
    message: str = ""


class AgentState(BaseModel):
    """Shared state passed through the LangGraph agent pipeline.

    Each node reads and writes to this state object.
    """

    # Input
    user_message: str = ""
    user_id: UUID | None = None

    # Phase tracking
    phase: AgentPhase = AgentPhase.INTAKE
    steps: list[dict] = Field(default_factory=list)

    # Agent outputs
    intent: AccessIntent | None = None
    policy_result: PolicyResult | None = None
    provisioning_result: ProvisioningResult | None = None

    # Final response
    response: str = ""
    error: str | None = None

    def add_step(self, agent: str, action: str, detail: str = "") -> None:
        """Record a reasoning step for explainability."""
        self.steps.append({"agent": agent, "action": action, "detail": detail})
