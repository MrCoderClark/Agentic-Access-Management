from fastapi import APIRouter

from app.api.deps import get_supabase_client

router = APIRouter()


@router.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {"status": "healthy", "service": "agentguard-api", "version": "0.1.0"}


@router.get("/health/db")
async def health_check_db():
    """Health check with database connectivity verification."""
    try:
        client = get_supabase_client()
        result = client.schema("agentguard").from_("users").select("id", count="exact").limit(0).execute()
        return {
            "status": "healthy",
            "service": "agentguard-api",
            "database": "connected",
            "schema": "agentguard",
        }
    except Exception as e:
        return {
            "status": "degraded",
            "service": "agentguard-api",
            "database": "error",
            "detail": str(e),
        }
