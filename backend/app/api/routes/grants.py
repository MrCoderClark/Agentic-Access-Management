from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_supabase_client
from app.core.security import get_current_user
from app.schemas.grants import GrantCreate, GrantList, GrantResponse, GrantUpdate

router = APIRouter(prefix="/api/v1/grants", tags=["grants"])

TABLE = "access_grants"
SCHEMA = "agentguard"


@router.get("", response_model=GrantList)
async def list_grants(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    user_id: str | None = None,
    system_id: str | None = None,
    status_filter: str | None = Query(None, alias="status"),
    _user=Depends(get_current_user),
):
    """List access grants with optional filters."""
    client = get_supabase_client()
    query = client.schema(SCHEMA).table(TABLE).select("*", count="exact")

    if user_id:
        query = query.eq("user_id", user_id)
    if system_id:
        query = query.eq("system_id", system_id)
    if status_filter:
        query = query.eq("status", status_filter)

    query = query.order("created_at", desc=True).range(offset, offset + limit - 1)
    result = query.execute()

    return GrantList(data=result.data, count=result.count or len(result.data))


@router.get("/{grant_id}", response_model=GrantResponse)
async def get_grant(grant_id: str, _user=Depends(get_current_user)):
    """Get a single grant by ID."""
    client = get_supabase_client()
    result = client.schema(SCHEMA).table(TABLE).select("*").eq("id", grant_id).execute()

    if not result.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grant not found")

    return result.data[0]


@router.post("", response_model=GrantResponse, status_code=status.HTTP_201_CREATED)
async def create_grant(payload: GrantCreate, _user=Depends(get_current_user)):
    """Create a new access grant."""
    client = get_supabase_client()
    data = payload.model_dump()
    data["status"] = "active"
    data["granted_at"] = "now()"

    result = (
        client.schema(SCHEMA)
        .table(TABLE)
        .insert(data)
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to create grant")

    return result.data[0]


@router.patch("/{grant_id}", response_model=GrantResponse)
async def update_grant(grant_id: str, payload: GrantUpdate, _user=Depends(get_current_user)):
    """Update a grant (e.g., change status, extend expiry)."""
    client = get_supabase_client()
    update_data = payload.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")

    result = (
        client.schema(SCHEMA)
        .table(TABLE)
        .update(update_data)
        .eq("id", grant_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grant not found")

    return result.data[0]


@router.post("/{grant_id}/revoke", response_model=GrantResponse)
async def revoke_grant(grant_id: str, _user=Depends(get_current_user)):
    """Revoke an active access grant."""
    client = get_supabase_client()
    result = (
        client.schema(SCHEMA)
        .table(TABLE)
        .update({"status": "revoked", "revoked_at": "now()"})
        .eq("id", grant_id)
        .eq("status", "active")
        .execute()
    )

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grant not found or not currently active",
        )

    return result.data[0]
