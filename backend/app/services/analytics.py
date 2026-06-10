"""Analytics service — metrics, trends, and security posture calculations."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.api.deps import get_supabase_client


class AnalyticsService:
    """Computes metrics and trends for the analytics dashboard."""

    def __init__(self):
        self.schema = "agentguard"

    def _client(self):
        return get_supabase_client()

    async def get_overview(self) -> dict:
        """High-level platform overview stats."""
        client = self._client()

        grants = client.schema(self.schema).table("access_grants").select("id, status, risk_score").execute().data
        systems = client.schema(self.schema).table("systems").select("id").execute().data
        policies = client.schema(self.schema).table("policies").select("id, is_active").execute().data
        users = client.schema(self.schema).table("users").select("id").execute().data

        active_grants = [g for g in grants if g.get("status") == "active"]
        avg_risk = (
            sum(g.get("risk_score", 0) for g in active_grants) / len(active_grants)
            if active_grants else 0
        )

        return {
            "total_users": len(users),
            "total_systems": len(systems),
            "active_grants": len(active_grants),
            "total_grants": len(grants),
            "active_policies": sum(1 for p in policies if p.get("is_active")),
            "avg_risk_score": round(avg_risk, 3),
        }

    async def get_risk_distribution(self) -> dict:
        """Risk score distribution across active grants."""
        client = self._client()

        grants = (
            client.schema(self.schema)
            .table("access_grants")
            .select("id, risk_score, system_id, permission")
            .eq("status", "active")
            .execute()
        ).data

        buckets = {"critical": 0, "high": 0, "medium": 0, "low": 0, "minimal": 0}
        for g in grants:
            score = g.get("risk_score", 0) or 0
            if score >= 0.9:
                buckets["critical"] += 1
            elif score >= 0.7:
                buckets["high"] += 1
            elif score >= 0.5:
                buckets["medium"] += 1
            elif score >= 0.3:
                buckets["low"] += 1
            else:
                buckets["minimal"] += 1

        return {
            "distribution": buckets,
            "total": len(grants),
        }

    async def get_grant_trends(self, days: int = 30) -> dict:
        """Grant creation/revocation trends over time."""
        client = self._client()
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()

        grants = (
            client.schema(self.schema)
            .table("access_grants")
            .select("id, status, granted_at, revoked_at")
            .gte("granted_at", cutoff)
            .execute()
        ).data

        # Group by date
        daily_created: dict[str, int] = {}
        daily_revoked: dict[str, int] = {}

        for g in grants:
            if g.get("granted_at"):
                date = g["granted_at"][:10]
                daily_created[date] = daily_created.get(date, 0) + 1
            if g.get("revoked_at"):
                date = g["revoked_at"][:10]
                daily_revoked[date] = daily_revoked.get(date, 0) + 1

        return {
            "period_days": days,
            "created": daily_created,
            "revoked": daily_revoked,
            "total_created": sum(daily_created.values()),
            "total_revoked": sum(daily_revoked.values()),
        }

    async def get_agent_activity(self, days: int = 30) -> dict:
        """Agent pipeline activity summary."""
        client = self._client()
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()

        events = (
            client.schema(self.schema)
            .table("audit_events")
            .select("id, actor, action, created_at, metadata")
            .in_("actor", ["agent_pipeline", "sentinel_agent", "review_agent"])
            .gte("created_at", cutoff)
            .execute()
        ).data

        by_actor: dict[str, int] = {}
        by_action: dict[str, int] = {}
        for e in events:
            actor = e.get("actor", "unknown")
            action = e.get("action", "unknown")
            by_actor[actor] = by_actor.get(actor, 0) + 1
            by_action[action] = by_action.get(action, 0) + 1

        return {
            "total_events": len(events),
            "by_actor": by_actor,
            "by_action": by_action,
            "period_days": days,
        }

    async def get_security_posture(self) -> dict:
        """Overall security posture score and breakdown."""
        client = self._client()

        grants = (
            client.schema(self.schema)
            .table("access_grants")
            .select("id, risk_score, status, expires_at, granted_at")
            .eq("status", "active")
            .execute()
        ).data

        policies = (
            client.schema(self.schema)
            .table("policies")
            .select("id, is_active")
            .execute()
        ).data

        now = datetime.now(timezone.utc)

        # Scoring factors (0-100 scale, higher is better)
        factors = {}

        # Factor 1: Average risk (lower avg risk = better)
        if grants:
            avg_risk = sum(g.get("risk_score", 0) or 0 for g in grants) / len(grants)
            factors["risk_management"] = max(0, int((1 - avg_risk) * 100))
        else:
            factors["risk_management"] = 100

        # Factor 2: Expiration coverage (grants with expiry = better)
        if grants:
            with_expiry = sum(1 for g in grants if g.get("expires_at"))
            factors["temporal_controls"] = int((with_expiry / len(grants)) * 100)
        else:
            factors["temporal_controls"] = 100

        # Factor 3: Policy coverage
        active_policies = sum(1 for p in policies if p.get("is_active"))
        factors["policy_coverage"] = min(100, active_policies * 20)  # 5+ policies = 100

        # Factor 4: Stale grant ratio (fewer stale = better)
        if grants:
            stale = 0
            for g in grants:
                try:
                    granted_at = g.get("granted_at", "")
                    if granted_at:
                        dt = datetime.fromisoformat(granted_at.replace("Z", "+00:00"))
                        if (now - dt).days > 90:
                            stale += 1
                except (ValueError, TypeError):
                    pass
            factors["access_freshness"] = max(0, int((1 - stale / len(grants)) * 100))
        else:
            factors["access_freshness"] = 100

        # Overall score (weighted average)
        weights = {
            "risk_management": 0.35,
            "temporal_controls": 0.25,
            "policy_coverage": 0.20,
            "access_freshness": 0.20,
        }
        overall = sum(factors[k] * weights[k] for k in weights)

        return {
            "overall_score": round(overall, 1),
            "factors": factors,
            "grade": _score_to_grade(overall),
            "total_active_grants": len(grants),
        }

    async def get_system_risk_heatmap(self) -> list[dict]:
        """Risk heatmap data per system."""
        client = self._client()

        systems = (
            client.schema(self.schema)
            .table("systems")
            .select("id, name, environment")
            .execute()
        ).data

        grants = (
            client.schema(self.schema)
            .table("access_grants")
            .select("system_id, risk_score, permission")
            .eq("status", "active")
            .execute()
        ).data

        # Aggregate by system
        system_map: dict[str, dict] = {}
        for s in systems:
            system_map[s["id"]] = {
                "system_id": s["id"],
                "name": s["name"],
                "environment": s.get("environment", "unknown"),
                "grant_count": 0,
                "avg_risk": 0,
                "max_risk": 0,
                "total_risk": 0,
                "permissions": set(),
            }

        for g in grants:
            sid = g.get("system_id")
            if sid and sid in system_map:
                risk = g.get("risk_score", 0) or 0
                system_map[sid]["grant_count"] += 1
                system_map[sid]["total_risk"] += risk
                system_map[sid]["max_risk"] = max(system_map[sid]["max_risk"], risk)
                system_map[sid]["permissions"].add(g.get("permission", ""))

        result = []
        for sid, data in system_map.items():
            if data["grant_count"] > 0:
                data["avg_risk"] = round(data["total_risk"] / data["grant_count"], 3)
            data["permissions"] = list(data["permissions"])
            del data["total_risk"]
            result.append(data)

        # Sort by avg_risk descending
        result.sort(key=lambda x: x["avg_risk"], reverse=True)
        return result


def _score_to_grade(score: float) -> str:
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    return "F"


analytics_service = AnalyticsService()
