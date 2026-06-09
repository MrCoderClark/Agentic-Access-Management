from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_supabase_client
from app.core.security import get_current_user
from app.schemas.users import UserCreate, UserList, UserResponse, UserUpdate

router = APIRouter(prefix="/api/v1/users", tags=["users"])

TABLE = "users"
SCHEMA = "agentguard"


@router.get("/me")
async def get_me(user=Depends(get_current_user)):
    """Return the currently authenticated user's profile."""
    return {
        "id": user.id,
        "email": user.email,
        "role": user.role,
    }


@router.get("", response_model=UserList)
async def list_users(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status_filter: str | None = Query(None, alias="status"),
    department: str | None = None,
    _user=Depends(get_current_user),
):
    """List all users with optional filters."""
    client = get_supabase_client()
    query = client.schema(SCHEMA).table(TABLE).select("*", count="exact")

    if status_filter:
        query = query.eq("status", status_filter)
    if department:
        query = query.eq("department", department)

    query = query.order("created_at", desc=True).range(offset, offset + limit - 1)
    result = query.execute()

    return UserList(data=result.data, count=result.count or len(result.data))


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, _user=Depends(get_current_user)):
    """Get a single user by ID."""
    client = get_supabase_client()
    result = client.schema(SCHEMA).table(TABLE).select("*").eq("id", user_id).execute()

    if not result.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return result.data[0]


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserCreate, _user=Depends(get_current_user)):
    """Create a new user record."""
    client = get_supabase_client()
    result = (
        client.schema(SCHEMA)
        .table(TABLE)
        .insert(payload.model_dump())
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to create user")

    return result.data[0]


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, payload: UserUpdate, _user=Depends(get_current_user)):
    """Update a user's fields (partial update)."""
    client = get_supabase_client()
    update_data = payload.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")

    result = (
        client.schema(SCHEMA)
        .table(TABLE)
        .update(update_data)
        .eq("id", user_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return result.data[0]


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: str, _user=Depends(get_current_user)):
    """Soft-delete a user (set status to offboarded)."""
    client = get_supabase_client()
    result = (
        client.schema(SCHEMA)
        .table(TABLE)
        .update({"status": "offboarded"})
        .eq("id", user_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
