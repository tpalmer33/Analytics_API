from fastapi import APIRouter
from .schemas import (
    EventSchema, 
    EventListSchema, 
    EventCreateSchema,
    EventUpdateSchema
)

router = APIRouter()

# GET /api/events/
@router.get("/")
def read_events() -> EventListSchema:
    # a bunch of items in a table
    return EventListSchema(
        results=[EventSchema(id=1), EventSchema(id=2), EventSchema(id=3)], 
        count=3
    )

# POST /api/events/
@router.post("/")
def create_event(payload:EventCreateSchema) -> EventSchema:
    # a bunch of items in a table
    data = payload.model_dump()
    return EventSchema(id=123, **data)

# GET /api/events/{int}
@router.get("/{event_id}")
def get_events(event_id:int) -> EventSchema:
    # a single row
    return EventSchema(id=event_id)

# PUT /api/events/{int}
@router.put("/{event_id}")
def update_events(event_id:int, payload:EventUpdateSchema) -> EventSchema:
    # a single row
    data = payload.model_dump()
    return EventSchema(id=event_id, **data)
