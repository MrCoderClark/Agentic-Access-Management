"""API routes for analytics, metrics, and security posture."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.services.analytics import analytics_service

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])


@router.get("/overview")
async def get_overview():
    """High-level platform metrics."""
    try:
        return await analytics_service.get_overview()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/risk-distribution")
async def get_risk_distribution():
    """Risk score distribution across active grants."""
    try:
        return await analytics_service.get_risk_distribution()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/grant-trends")
async def get_grant_trends(days: int = 30):
    """Grant creation/revocation trends over time."""
    try:
        return await analytics_service.get_grant_trends(days=days)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agent-activity")
async def get_agent_activity(days: int = 30):
    """Agent pipeline activity summary."""
    try:
        return await analytics_service.get_agent_activity(days=days)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/security-posture")
async def get_security_posture():
    """Overall security posture score and factors."""
    try:
        return await analytics_service.get_security_posture()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/risk-heatmap")
async def get_risk_heatmap():
    """Risk heatmap data per system."""
    try:
        return await analytics_service.get_system_risk_heatmap()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
