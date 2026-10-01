import os
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, col, select
from timescaledb.hyperfunctions import time_bucket
from datetime import datetime, timedelta, timezone
from sqlalchemy import func

from api.db.session import get_session
from api.db.config import DATABASE_URL

from .models import (
    EventModel, 
    EventBucketSchema, 
    EventCreateSchema,
    EventUpdateSchema,
    get_utc_now
)

router = APIRouter()

DEFAULT_LOOKUP_PAGES = ['/about', '/contact', '/pages', 'pricing'] 

# GET /api/events/
@router.get("/", response_model=List[EventBucketSchema])
def read_events(
    duration: str = Query(default="1 day"),
    pages: List = Query(default=None),
    session: Session = Depends(get_session)
    ):
    bucket = time_bucket(duration, EventModel.time) # Buckets of data are chunked by a time range of 1 hour
    lookup_pages = pages if isinstance(pages, list) and len(pages) > 0 else DEFAULT_LOOKUP_PAGES 

    query = (
        select(
            bucket.label("bucket"), 
            col(EventModel.page).label("page"),
            func.count().label("count")
        )
        .where(
            col(EventModel.page).in_(lookup_pages) # Filter by page
        )
        .group_by(
            bucket,
            EventModel.page
        ) # Group
        .order_by(
            bucket,
            EventModel.page
        )
    )
    results = session.exec(query).fetchall()
    return results

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
