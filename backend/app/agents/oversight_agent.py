"""Oversight Agent — agent-to-agent governance, reviews other agent decisions."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from app.api.deps import get_supabase_client
from app.config import settings


OVERSIGHT_PROMPT = """You are the Oversight Agent for AgentGuard, an enterprise access governance system.

Your role is to review decisions made by other AI agents (Request Agent, Policy Agent, Provisioning Agent)
and flag potential issues including:

1. Overly permissive grants (admin/write access to production systems)
2. Inconsistent decisions (similar requests getting different outcomes)
3. Missing justification for high-risk approvals
4. Potential policy violations or circumventions
5. Unusual patterns (burst of requests, privilege escalation chains)

Given the following agent decision, provide your assessment:
- is_flagged: true if the decision should be reviewed by a human
- severity: "low", "medium", "high", or "critical"
- reason: brief explanation of your concern (or "ok" if no issues)
- recommendation: what action to take ("none", "review", "revoke", "escalate")

Respond in JSON (no markdown):
{"is_flagged": false, "severity": "low", "reason": "ok", "recommendation": "none"}
"""


class OversightAgent:
    """Reviews and audits other agent decisions for governance compliance."""

    def __init__(self):
        self.schema = "agentguard"

    def _client(self):
        return get_supabase_client()

    async def review_decision(self, agent_decision: dict) -> dict:
        """Review a single agent pipeline decision.

        Args:
            agent_decision: The full result from run_agent_pipeline.

        Returns:
            Oversight assessment with flagging info.
        """
        import json

        llm = ChatOpenAI(
            model=settings.agent_model,
            api_key=settings.openai_api_key,
            temperature=0,
        )

        # Summarize the decision for review
        summary = {
            "response": agent_decision.get("response", ""),
            "phase": agent_decision.get("phase", ""),
            "intent": agent_decision.get("intent", {}),
            "policy_result": agent_decision.get("policy_result", {}),
            "provisioning_result": agent_decision.get("provisioning_result", {}),
            "steps": agent_decision.get("steps", []),
        }

        response = await llm.ainvoke([
            SystemMessage(content=OVERSIGHT_PROMPT),
            HumanMessage(content=f"Agent decision to review:\n{json.dumps(summary, default=str)}"),
        ])

        content = response.content.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[1].rsplit("```", 1)[0].strip()

        assessment = json.loads(content)

        # Log if flagged
        if assessment.get("is_flagged"):
            self._log_flag(agent_decision, assessment)

        return assessment

    def _log_flag(self, decision: dict, assessment: dict):
        """Log a flagged decision to audit."""
        client = self._client()
        client.schema(self.schema).table("audit_events").insert({
            "actor": "oversight_agent",
            "actor_type": "system",
            "action": "decision.flagged",
            "target_type": "agent_decision",
            "target_id": str(uuid4()),
            "metadata": {
                "severity": assessment.get("severity"),
                "reason": assessment.get("reason"),
                "recommendation": assessment.get("recommendation"),
                "original_intent": decision.get("intent"),
                "original_phase": decision.get("phase"),
            },
        }).execute()

    async def audit_recent_decisions(self, limit: int = 20) -> dict:
        """Review recent agent decisions in bulk for patterns.

        Returns:
            Summary of flagged items.
        """
        client = self._client()

        # Fetch recent agent-processed audit events
        events = (
            client.schema(self.schema)
            .table("audit_events")
            .select("id, action, metadata, created_at")
            .eq("actor", "agent_pipeline")
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        ).data

        flagged = []
        for event in events:
            meta = event.get("metadata", {}) or {}
            risk = meta.get("risk_score", 0)

            # Heuristic flags (fast, no LLM call)
            issues = []
            if risk >= 0.8 and meta.get("decision") == "approved":
                issues.append("High-risk approval without escalation")
            if meta.get("permission") in ("admin", "superadmin", "root"):
                issues.append("Elevated privilege grant")

            if issues:
                flagged.append({
                    "event_id": event["id"],
                    "action": event["action"],
                    "issues": issues,
                    "risk_score": risk,
                    "created_at": event.get("created_at"),
                })

        return {
            "total_reviewed": len(events),
            "flagged_count": len(flagged),
            "flagged_items": flagged,
        }


oversight_agent = OversightAgent()
