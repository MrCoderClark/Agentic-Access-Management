from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_supabase_client
from app.core.security import get_current_user
from app.schemas.tickets import TicketCreate, TicketList, TicketResponse, TicketUpdate

router = APIRouter(prefix="/api/v1/tickets", tags=["tickets"])

TABLE = "tickets"
SCHEMA = "agentguard"


@router.get("", response_model=TicketList)
async def list_tickets(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    ticket_type: str | None = None,
    status_filter: str | None = Query(None, alias="status"),
    requester_id: str | None = None,
    _user=Depends(get_current_user),
):
    """List tickets with optional filters."""
    client = get_supabase_client()
    query = client.schema(SCHEMA).table(TABLE).select("*", count="exact")

    if ticket_type:
        query = query.eq("ticket_type", ticket_type)
    if status_filter:
        query = query.eq("status", status_filter)
    if requester_id:
        query = query.eq("requester_id", requester_id)

    query = query.order("created_at", desc=True).range(offset, offset + limit - 1)
    result = query.execute()

    return TicketList(data=result.data, count=result.count or len(result.data))


@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket(ticket_id: str, _user=Depends(get_current_user)):
    """Get a single ticket by ID."""
    client = get_supabase_client()
    result = client.schema(SCHEMA).table(TABLE).select("*").eq("id", ticket_id).execute()

    if not result.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    return result.data[0]


@router.post("", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def create_ticket(payload: TicketCreate, _user=Depends(get_current_user)):
    """Create a new ticket (access request, incident, etc.)."""
    client = get_supabase_client()
    result = (
        client.schema(SCHEMA)
        .table(TABLE)
        .insert(payload.model_dump())
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to create ticket")

    return result.data[0]


@router.patch("/{ticket_id}", response_model=TicketResponse)
async def update_ticket(ticket_id: str, payload: TicketUpdate, _user=Depends(get_current_user)):
    """Update a ticket (status, assignee, resolution, etc.)."""
    client = get_supabase_client()
    update_data = payload.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")

    result = (
        client.schema(SCHEMA)
        .table(TABLE)
        .update(update_data)
        .eq("id", ticket_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    return result.data[0]
