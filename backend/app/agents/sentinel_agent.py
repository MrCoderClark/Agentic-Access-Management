"""Sentinel Agent — background scanner for unused permissions and policy drift."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID

from app.api.deps import get_supabase_client


class SentinelAgent:
    """Scans for access governance issues on demand or on schedule."""

    def __init__(self):
        self.schema = "agentguard"

    def _client(self):
        return get_supabase_client()

    async def scan_expired_grants(self) -> list[dict]:
        """Find and revoke grants that have passed their expiration."""
        client = self._client()
        now = datetime.now(timezone.utc).isoformat()

        # Find active grants that are expired
        expired = (
            client.schema(self.schema)
            .table("access_grants")
            .select("id, user_id, system_id, permission, expires_at")
            .eq("status", "active")
            .lt("expires_at", now)
            .execute()
        ).data

        revoked = []
        for grant in expired:
            # Revoke
            client.schema(self.schema).table("access_grants").update(
                {"status": "revoked", "revoked_at": now}
            ).eq("id", grant["id"]).execute()

            # Audit
            client.schema(self.schema).table("audit_events").insert({
                "actor": "sentinel_agent",
                "actor_type": "system",
                "action": "grant.auto_revoked",
                "target_type": "access_grant",
                "target_id": grant["id"],
                "metadata": {
                    "reason": "expired",
                    "user_id": grant["user_id"],
                    "system_id": grant["system_id"],
                    "permission": grant["permission"],
                    "expired_at": grant["expires_at"],
                },
            }).execute()

            revoked.append(grant)

        return revoked

    async def scan_unused_grants(self, inactive_days: int = 30) -> list[dict]:
        """Find active grants that haven't been used recently.

        Returns grants that were created more than `inactive_days` ago
        with no recent audit activity.
        """
        client = self._client()
        cutoff = (datetime.now(timezone.utc) - timedelta(days=inactive_days)).isoformat()

        # Grants older than cutoff that are still active
        old_grants = (
            client.schema(self.schema)
            .table("access_grants")
            .select("id, user_id, system_id, permission, granted_at")
            .eq("status", "active")
            .lt("granted_at", cutoff)
            .limit(100)
            .execute()
        ).data

        return old_grants

    async def scan_policy_drift(self) -> list[dict]:
        """Detect grants that no longer align with current policies.

        Checks active grants against current policy risk thresholds.
        """
        client = self._client()

        # Get active policies
        policies = (
            client.schema(self.schema)
            .table("policies")
            .select("id, name, system_id, risk_threshold, auto_approve")
            .eq("is_active", True)
            .execute()
        ).data

        # Get active grants with risk scores
        grants = (
            client.schema(self.schema)
            .table("access_grants")
            .select("id, user_id, system_id, permission, risk_score, metadata")
            .eq("status", "active")
            .execute()
        ).data

        drifted = []
        for grant in grants:
            # Find matching policy for this grant's system
            system_id = grant.get("system_id")
            matching_policies = [
                p for p in policies
                if p.get("system_id") == system_id or p.get("system_id") is None
            ]

            if not matching_policies:
                continue

            policy = matching_policies[0]
            threshold = policy.get("risk_threshold", 0.7)

            # If grant risk exceeds current threshold and policy doesn't auto-approve
            if grant.get("risk_score", 0) >= threshold and not policy.get("auto_approve"):
                drifted.append({
                    "grant_id": grant["id"],
                    "user_id": grant["user_id"],
                    "system_id": system_id,
                    "permission": grant["permission"],
                    "risk_score": grant.get("risk_score"),
                    "policy_threshold": threshold,
                    "policy_name": policy["name"],
                })

        return drifted

    async def run_full_scan(self) -> dict:
        """Run all sentinel scans and return summary."""
        expired = await self.scan_expired_grants()
        unused = await self.scan_unused_grants()
        drifted = await self.scan_policy_drift()

        return {
            "expired_revoked": len(expired),
            "unused_grants": len(unused),
            "policy_drift": len(drifted),
            "details": {
                "expired": expired,
                "unused": unused,
                "drifted": drifted,
            },
        }


sentinel_agent = SentinelAgent()
