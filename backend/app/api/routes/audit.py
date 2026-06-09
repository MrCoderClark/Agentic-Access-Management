from fastapi import APIRouter, Depends, Query

from app.api.deps import get_supabase_client
from app.core.security import get_current_user
from app.schemas.audit import AuditEventCreate, AuditEventList, AuditEventResponse

router = APIRouter(prefix="/api/v1/audit", tags=["audit"])

TABLE = "audit_events"
SCHEMA = "agentguard"


@router.get("", response_model=AuditEventList)
async def list_audit_events(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    actor_type: str | None = None,
    action: str | None = None,
    target_type: str | None = None,
    target_id: str | None = None,
    _user=Depends(get_current_user),
):
    """List audit events (read-only, append-only log)."""
    client = get_supabase_client()
    query = client.schema(SCHEMA).table(TABLE).select("*", count="exact")

    if actor_type:
        query = query.eq("actor_type", actor_type)
    if action:
        query = query.eq("action", action)
    if target_type:
        query = query.eq("target_type", target_type)
    if target_id:
        query = query.eq("target_id", target_id)

    query = query.order("created_at", desc=True).range(offset, offset + limit - 1)
    result = query.execute()

    return AuditEventList(data=result.data, count=result.count or len(result.data))


@router.post("", response_model=AuditEventResponse, status_code=201)
async def create_audit_event(payload: AuditEventCreate, _user=Depends(get_current_user)):
    """Append a new audit event (immutable — no update or delete)."""
    client = get_supabase_client()
    result = (
        client.schema(SCHEMA)
        .table(TABLE)
        .insert(payload.model_dump())
        .execute()
    )

    return result.data[0]
