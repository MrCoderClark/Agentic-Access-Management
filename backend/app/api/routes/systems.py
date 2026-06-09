from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_supabase_client
from app.core.security import get_current_user
from app.schemas.systems import SystemCreate, SystemList, SystemResponse, SystemUpdate

router = APIRouter(prefix="/api/v1/systems", tags=["systems"])

TABLE = "systems"
SCHEMA = "agentguard"


@router.get("", response_model=SystemList)
async def list_systems(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    system_type: str | None = None,
    risk_level: str | None = None,
    _user=Depends(get_current_user),
):
    """List all systems with optional filters."""
    client = get_supabase_client()
    query = client.schema(SCHEMA).table(TABLE).select("*", count="exact")

    if system_type:
        query = query.eq("system_type", system_type)
    if risk_level:
        query = query.eq("risk_level", risk_level)

    query = query.order("name").range(offset, offset + limit - 1)
    result = query.execute()

    return SystemList(data=result.data, count=result.count or len(result.data))


@router.get("/{system_id}", response_model=SystemResponse)
async def get_system(system_id: str, _user=Depends(get_current_user)):
    """Get a single system by ID."""
    client = get_supabase_client()
    result = client.schema(SCHEMA).table(TABLE).select("*").eq("id", system_id).execute()

    if not result.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="System not found")

    return result.data[0]


@router.post("", response_model=SystemResponse, status_code=status.HTTP_201_CREATED)
async def create_system(payload: SystemCreate, _user=Depends(get_current_user)):
    """Create a new system."""
    client = get_supabase_client()
    result = (
        client.schema(SCHEMA)
        .table(TABLE)
        .insert(payload.model_dump())
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to create system")

    return result.data[0]


@router.patch("/{system_id}", response_model=SystemResponse)
async def update_system(system_id: str, payload: SystemUpdate, _user=Depends(get_current_user)):
    """Update a system's fields (partial update)."""
    client = get_supabase_client()
    update_data = payload.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")

    result = (
        client.schema(SCHEMA)
        .table(TABLE)
        .update(update_data)
        .eq("id", system_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="System not found")

    return result.data[0]


@router.delete("/{system_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_system(system_id: str, _user=Depends(get_current_user)):
    """Delete a system."""
    client = get_supabase_client()
    result = (
        client.schema(SCHEMA)
        .table(TABLE)
        .delete()
        .eq("id", system_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="System not found")
