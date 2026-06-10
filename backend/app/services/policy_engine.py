"""Policy engine — evaluates access requests against policies with RAG context."""

from dataclasses import dataclass
from uuid import UUID

from app.api.deps import get_supabase_client
from app.services.rag import rag_service


@dataclass
class PolicyDecision:
    approved: bool
    risk_score: float
    reasoning: str
    matched_policy_id: UUID | None
    rag_sources: list[dict]
    confidence: float


class PolicyEngine:
    """Evaluates access requests against stored policies."""

    def __init__(self):
        self.schema = "agentguard"

    def _client(self):
        return get_supabase_client()

    async def evaluate_request(
        self,
        user_id: UUID,
        system_id: UUID,
        permission: str,
        justification: str = "",
    ) -> PolicyDecision:
        """Evaluate an access request against policies.

        Steps:
        1. Fetch relevant policies for the system
        2. Check user risk score
        3. RAG search for precedents and relevant docs
        4. Score risk and make decision
        """
        client = self._client()

        # 1. Get matching policies
        policies = (
            client.schema(self.schema)
            .table("policies")
            .select("*")
            .or_(f"system_id.eq.{system_id},system_id.is.null")
            .eq("is_active", True)
            .execute()
        ).data

        # 2. Get user risk info
        user = (
            client.schema(self.schema)
            .table("users")
            .select("id, risk_score, status, groups")
            .eq("id", str(user_id))
            .single()
            .execute()
        ).data

        if not user:
            return PolicyDecision(
                approved=False,
                risk_score=1.0,
                reasoning="User not found",
                matched_policy_id=None,
                rag_sources=[],
                confidence=1.0,
            )

        if user.get("status") != "active":
            return PolicyDecision(
                approved=False,
                risk_score=1.0,
                reasoning=f"User is {user.get('status', 'unknown')} — access denied",
                matched_policy_id=None,
                rag_sources=[],
                confidence=1.0,
            )

        # 3. Get system risk level
        system = (
            client.schema(self.schema)
            .table("systems")
            .select("id, name, risk_level")
            .eq("id", str(system_id))
            .single()
            .execute()
        ).data

        if not system:
            return PolicyDecision(
                approved=False,
                risk_score=1.0,
                reasoning="System not found",
                matched_policy_id=None,
                rag_sources=[],
                confidence=1.0,
            )

        # 4. RAG search for relevant context
        search_query = f"access request for {permission} on {system.get('name', 'system')}"
        if justification:
            search_query += f" justification: {justification}"

        rag_results = await rag_service.search_multi(
            query=search_query,
            match_count=5,
            doc_types=["policy", "decision", "runbook"],
            similarity_threshold=0.3,
        )

        # 5. Compute risk score
        risk_score = self._compute_risk_score(
            user_risk=user.get("risk_score", 0.5),
            system_risk_level=system.get("risk_level", "medium"),
            permission=permission,
        )

        # 6. Find best matching policy and decide
        decision = self._apply_policies(
            policies=policies,
            risk_score=risk_score,
            user=user,
            system=system,
            permission=permission,
        )

        return PolicyDecision(
            approved=decision["approved"],
            risk_score=risk_score,
            reasoning=decision["reasoning"],
            matched_policy_id=decision.get("policy_id"),
            rag_sources=[
                {"id": r["id"], "content": r["content"][:200], "similarity": r["similarity"]}
                for r in rag_results
            ],
            confidence=decision["confidence"],
        )

    def _compute_risk_score(
        self,
        user_risk: float,
        system_risk_level: str,
        permission: str,
    ) -> float:
        """Compute combined risk score from user, system, and permission factors."""
        system_risk_map = {
            "low": 0.2,
            "medium": 0.5,
            "high": 0.75,
            "critical": 0.95,
        }
        system_risk = system_risk_map.get(system_risk_level, 0.5)

        # Permission risk heuristic
        high_risk_keywords = ["admin", "delete", "write", "superuser", "root", "owner"]
        permission_risk = 0.3
        if any(kw in permission.lower() for kw in high_risk_keywords):
            permission_risk = 0.8

        # Weighted average
        combined = (user_risk * 0.3) + (system_risk * 0.4) + (permission_risk * 0.3)
        return round(min(max(combined, 0.0), 1.0), 3)

    def _apply_policies(
        self,
        policies: list[dict],
        risk_score: float,
        user: dict,
        system: dict,
        permission: str,
    ) -> dict:
        """Apply matching policies to make approve/deny decision."""
        if not policies:
            return {
                "approved": False,
                "reasoning": "No matching policy found for this system",
                "confidence": 0.9,
                "policy_id": None,
            }

        # Find best matching policy (system-specific > global)
        system_policies = [p for p in policies if p.get("system_id") == str(system["id"])]
        global_policies = [p for p in policies if p.get("system_id") is None]
        best_policy = (system_policies or global_policies)[0] if (system_policies or global_policies) else policies[0]

        policy_id = best_policy.get("id")
        risk_threshold = best_policy.get("risk_threshold", 0.7)

        # Auto-approve check
        if best_policy.get("auto_approve") and risk_score < risk_threshold:
            return {
                "approved": True,
                "reasoning": f"Auto-approved by policy '{best_policy['name']}' — risk {risk_score} below threshold {risk_threshold}",
                "confidence": 0.85,
                "policy_id": policy_id,
            }

        # Risk threshold check
        if risk_score >= risk_threshold:
            return {
                "approved": False,
                "reasoning": f"Risk score {risk_score} exceeds threshold {risk_threshold} in policy '{best_policy['name']}' — requires manual approval",
                "confidence": 0.8,
                "policy_id": policy_id,
            }

        # Default: requires approval
        return {
            "approved": False,
            "reasoning": f"Policy '{best_policy['name']}' requires manual approval for this access type",
            "confidence": 0.7,
            "policy_id": policy_id,
        }


policy_engine = PolicyEngine()
