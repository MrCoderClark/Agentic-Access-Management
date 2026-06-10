"""Review Agent — continuous access review and certification campaigns."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from app.api.deps import get_supabase_client


class ReviewAgent:
    """Manages access review campaigns and certifications.

    Responsibilities:
    - Create periodic review campaigns for all active grants
    - Flag high-risk grants for immediate review
    - Track reviewer decisions (certify / revoke / modify)
    - Generate review summaries and compliance reports
    """

    def __init__(self):
        self.schema = "agentguard"

    def _client(self):
        return get_supabase_client()

    async def create_campaign(
        self,
        name: str | None = None,
        scope: str = "all",
        reviewer_id: str | None = None,
    ) -> dict:
        """Create a new access review campaign.

        Args:
            name: Campaign name (auto-generated if None)
            scope: "all", "high_risk", or a specific system_id
            reviewer_id: UUID of the assigned reviewer

        Returns:
            Campaign summary with items to review.
        """
        client = self._client()
        now = datetime.now(timezone.utc)
        campaign_id = str(uuid4())

        if not name:
            name = f"Access Review - {now.strftime('%Y-%m-%d')}"

        # Fetch grants based on scope
        query = (
            client.schema(self.schema)
            .table("access_grants")
            .select("id, user_id, system_id, permission, risk_score, granted_at, expires_at, metadata")
            .eq("status", "active")
        )

        if scope == "high_risk":
            query = query.gte("risk_score", 0.6)
        elif scope != "all":
            query = query.eq("system_id", scope)

        grants = query.execute().data

        # Create review items
        review_items = []
        for grant in grants:
            item = {
                "id": str(uuid4()),
                "campaign_id": campaign_id,
                "grant_id": grant["id"],
                "user_id": grant["user_id"],
                "system_id": grant["system_id"],
                "permission": grant["permission"],
                "risk_score": grant.get("risk_score", 0),
                "granted_at": grant.get("granted_at"),
                "status": "pending_review",
                "reviewer_id": reviewer_id,
                "recommendation": self._generate_recommendation(grant),
            }
            review_items.append(item)

        # Store campaign
        campaign_data = {
            "id": campaign_id,
            "name": name,
            "scope": scope,
            "reviewer_id": reviewer_id,
            "status": "active",
            "created_at": now.isoformat(),
            "due_date": (now + timedelta(days=14)).isoformat(),
            "total_items": len(review_items),
            "completed_items": 0,
            "metadata": {
                "scope_filter": scope,
                "items": review_items,
            },
        }

        client.schema(self.schema).table("audit_events").insert({
            "actor": "review_agent",
            "actor_type": "system",
            "action": "review_campaign.created",
            "target_type": "campaign",
            "target_id": campaign_id,
            "metadata": {
                "name": name,
                "scope": scope,
                "total_items": len(review_items),
            },
        }).execute()

        return {
            "campaign_id": campaign_id,
            "name": name,
            "scope": scope,
            "total_items": len(review_items),
            "items": review_items[:20],  # Return first 20 for preview
            "due_date": campaign_data["due_date"],
        }

    def _generate_recommendation(self, grant: dict) -> str:
        """Generate AI recommendation for a grant review."""
        risk = grant.get("risk_score", 0)
        granted_at = grant.get("granted_at", "")

        if risk >= 0.8:
            return "revoke"
        elif risk >= 0.6:
            return "review_with_justification"

        # Check if grant is very old (> 90 days)
        if granted_at:
            try:
                granted_dt = datetime.fromisoformat(granted_at.replace("Z", "+00:00"))
                age_days = (datetime.now(timezone.utc) - granted_dt).days
                if age_days > 90:
                    return "review_with_justification"
            except (ValueError, TypeError):
                pass

        return "certify"

    async def get_review_stats(self) -> dict:
        """Get statistics about access reviews."""
        client = self._client()

        # Count active grants by risk level
        grants = (
            client.schema(self.schema)
            .table("access_grants")
            .select("id, risk_score, status, granted_at, system_id")
            .eq("status", "active")
            .execute()
        ).data

        high_risk = sum(1 for g in grants if (g.get("risk_score") or 0) >= 0.7)
        medium_risk = sum(1 for g in grants if 0.4 <= (g.get("risk_score") or 0) < 0.7)
        low_risk = sum(1 for g in grants if (g.get("risk_score") or 0) < 0.4)

        # Count old grants (> 90 days)
        now = datetime.now(timezone.utc)
        stale_count = 0
        for g in grants:
            try:
                granted_at = g.get("granted_at", "")
                if granted_at:
                    dt = datetime.fromisoformat(granted_at.replace("Z", "+00:00"))
                    if (now - dt).days > 90:
                        stale_count += 1
            except (ValueError, TypeError):
                pass

        # Unique systems
        systems = set(g.get("system_id") for g in grants if g.get("system_id"))

        return {
            "total_active_grants": len(grants),
            "high_risk": high_risk,
            "medium_risk": medium_risk,
            "low_risk": low_risk,
            "stale_grants": stale_count,
            "systems_covered": len(systems),
            "review_coverage": 1.0 if not grants else 0.0,  # Placeholder
        }

    async def process_decision(
        self,
        grant_id: str,
        decision: str,
        reviewer_id: str,
        reason: str = "",
    ) -> dict:
        """Process a reviewer's decision on a grant.

        Args:
            grant_id: The grant being reviewed
            decision: "certify", "revoke", or "modify"
            reviewer_id: Who made the decision
            reason: Optional justification

        Returns:
            Action result dict.
        """
        client = self._client()
        now = datetime.now(timezone.utc).isoformat()

        if decision == "revoke":
            client.schema(self.schema).table("access_grants").update(
                {"status": "revoked", "revoked_at": now}
            ).eq("id", grant_id).execute()

        # Audit
        client.schema(self.schema).table("audit_events").insert({
            "actor": reviewer_id,
            "actor_type": "user",
            "action": f"review.{decision}",
            "target_type": "access_grant",
            "target_id": grant_id,
            "metadata": {"reason": reason, "decision": decision},
        }).execute()

        return {
            "grant_id": grant_id,
            "decision": decision,
            "processed": True,
        }


review_agent = ReviewAgent()
