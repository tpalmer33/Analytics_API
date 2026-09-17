from fastapi import APIRouter
from .schemas import EventSchema

router = APIRouter()

@router.get("/")
def read_events():
    # a bunch of items in a table
    return {
        "items": [1,2,3]
    }

@router.get("/{event_id}")
def get_events(event_id:int) -> EventSchema:
    # a single row
    return EventSchema(id=event_id)

