from fastapi import APIRouter, Depends

from app.core.security import get_current_user

router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.get("/me")
async def get_me(user=Depends(get_current_user)):
    """Return the currently authenticated user's profile."""
    return {
        "id": user.id,
        "email": user.email,
        "role": user.role,
    }
