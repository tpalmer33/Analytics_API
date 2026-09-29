import os
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, col, select

from api.db.session import get_session

from .models import (
    EventModel, 
    EventListSchema, 
    EventCreateSchema,
    EventUpdateSchema,
    get_utc_now
)

router = APIRouter()
from api.db.config import DATABASE_URL

# GET /api/events/
@router.get("/", response_model=EventListSchema)
def read_events(session: Session = Depends(get_session)):
    # a bunch of items in a table
    query = select(EventModel).order_by(col(EventModel.updated_at).desc()).limit(20)
    results = session.exec(query).all()
    return {
        "results": results,
        "count": len(results)
    }

# POST /api/events/
@router.post("/", response_model=EventModel)
def create_event(
    payload:EventCreateSchema, 
    session: Session = Depends(get_session)):
    # a bunch of items in a table
    data = payload.model_dump() # payload -> dict -> pydantic
    obj = EventModel.model_validate(data) # Validate incoming data against EventModel
    session.add(obj)
    session.commit()
    session.refresh(obj)

    return obj

# GET /api/events/{int}
@router.get("/{event_id}", response_model=EventModel)
def get_events(event_id:int, session: Session = Depends(get_session)):
    # a single row
    query = select(EventModel).where(EventModel.id == event_id)
    result = session.exec(query).first()
    if not result:
        raise HTTPException(status_code=404, detail="Event not found")
    return result

# PUT /api/events/{int}
@router.put("/{event_id}", response_model=EventModel)
def update_events(
        event_id:int, 
        payload:EventUpdateSchema,
        session: Session = Depends(get_session)):
    # a single row
    query = select(EventModel).where(EventModel.id == event_id)
    obj = session.exec(query).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Event not found")

    data = payload.model_dump()
    for k, v in data.items():
        setattr(obj, k, v)

    obj.updated_at = get_utc_now()

    session.add(obj)
    session.commit()
    session.refresh(obj)
    return obj

@router.delete("/{event_id}")
def delete_event(event_id: int, session: Session = Depends(get_session)) -> str:
    query = select(EventModel).where(EventModel.id == event_id)
    obj = session.exec(query).first()
    if not obj: 
        raise HTTPException(status_code=404, detail="Event not found")

    session.delete(obj)
    session.commit()
    return "Event deleted"
