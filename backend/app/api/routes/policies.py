from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_supabase_client
from app.core.security import get_current_user
from app.schemas.policies import PolicyCreate, PolicyList, PolicyResponse, PolicyUpdate

router = APIRouter(prefix="/api/v1/policies", tags=["policies"])

TABLE = "policies"
SCHEMA = "agentguard"


@router.get("", response_model=PolicyList)
async def list_policies(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    system_id: str | None = None,
    is_active: bool | None = None,
    _user=Depends(get_current_user),
):
    """List all policies with optional filters."""
    client = get_supabase_client()
    query = client.schema(SCHEMA).table(TABLE).select("*", count="exact")

    if system_id:
        query = query.eq("system_id", system_id)
    if is_active is not None:
        query = query.eq("is_active", is_active)

    query = query.order("created_at", desc=True).range(offset, offset + limit - 1)
    result = query.execute()

    return PolicyList(data=result.data, count=result.count or len(result.data))


@router.get("/{policy_id}", response_model=PolicyResponse)
async def get_policy(policy_id: str, _user=Depends(get_current_user)):
    """Get a single policy by ID."""
    client = get_supabase_client()
    result = client.schema(SCHEMA).table(TABLE).select("*").eq("id", policy_id).execute()

    if not result.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Policy not found")

    return result.data[0]


@router.post("", response_model=PolicyResponse, status_code=status.HTTP_201_CREATED)
async def create_policy(payload: PolicyCreate, _user=Depends(get_current_user)):
    """Create a new policy."""
    client = get_supabase_client()
    result = (
        client.schema(SCHEMA)
        .table(TABLE)
        .insert(payload.model_dump())
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to create policy")

    return result.data[0]


@router.patch("/{policy_id}", response_model=PolicyResponse)
async def update_policy(policy_id: str, payload: PolicyUpdate, _user=Depends(get_current_user)):
    """Update a policy's fields (partial update)."""
    client = get_supabase_client()
    update_data = payload.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")

    result = (
        client.schema(SCHEMA)
        .table(TABLE)
        .update(update_data)
        .eq("id", policy_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Policy not found")

    return result.data[0]


@router.delete("/{policy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_policy(policy_id: str, _user=Depends(get_current_user)):
    """Deactivate a policy (soft delete)."""
    client = get_supabase_client()
    result = (
        client.schema(SCHEMA)
        .table(TABLE)
        .update({"is_active": False})
        .eq("id", policy_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Policy not found")
