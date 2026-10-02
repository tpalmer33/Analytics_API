import os
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, col, select
from timescaledb.hyperfunctions import time_bucket
from datetime import datetime, timedelta, timezone
from sqlalchemy import func, case

from api.db.session import get_session
from api.db.config import DATABASE_URL

from .models import (
    EventModel, 
    EventBucketSchema, 
    EventCreateSchema,
    get_utc_now
)

router = APIRouter()

# Limit aggregation to these pages when no nonempty page list is supplied.
DEFAULT_LOOKUP_PAGES = [
    "/", "/about", "/pricing", "/contact",
    "/blog", "/products", "/login", "/signup",
    "/dashboard", "/settings"
]

@router.get("/", response_model=List[EventBucketSchema])
def read_events(
    duration: str = Query(default="1 day"),
    pages: List = Query(default=None),
    session: Session = Depends(get_session)
    ):
    """Aggregate event counts and average durations by time bucket, OS, and page."""
    # Match user-agent substrings in order; unmatched or null values become Other.
    os_case = case(
        (col(EventModel.user_agent).ilike('%windows%'), 'Windows'),
        (col(EventModel.user_agent).ilike('%macintosh%'), 'MacOS'),
        (col(EventModel.user_agent).ilike('%iphone%'), 'iOS'),
        (col(EventModel.user_agent).ilike('%android%'), 'Android'),
        (col(EventModel.user_agent).ilike('%linux%'), 'Linux'),
        else_='Other'
    ).label('operating_system')
    # duration sets the bucket width (default: one day), not the lookback window.
    bucket = time_bucket(duration, EventModel.time)
    lookup_pages = pages if isinstance(pages, list) and len(pages) > 0 else DEFAULT_LOOKUP_PAGES 

    query = (
        select(
            bucket.label("bucket"), 
            os_case,
            col(EventModel.page).label("page"),
            func.avg(EventModel.duration).label('avg_duration'),
        )
        .add_columns(
            func.count().label("count")
        )
        .where(
            col(EventModel.page).in_(lookup_pages)
        )
        .group_by(
            bucket,
            os_case,
            EventModel.page
        )
        .order_by(
            bucket,
            os_case,
            EventModel.page
        )
    )
    results = session.execute(query).fetchall()
    return results

@router.post("/", response_model=EventModel)
def create_event(
    payload:EventCreateSchema, 
    session: Session = Depends(get_session)):
    """Persist a page-visit event and return the stored record."""
    # Convert the request schema to the table model, applying its defaults.
    data = payload.model_dump()
    obj = EventModel.model_validate(data)
    session.add(obj)
    session.commit()
    # Load database-generated values before serializing the response.
    session.refresh(obj)

    return obj

@router.get("/{event_id}", response_model=EventModel)
def get_events(event_id:int, session: Session = Depends(get_session)):
    """Return an event by ID, or respond with 404 when it does not exist."""
    query = select(EventModel).where(EventModel.id == event_id)
    result = session.exec(query).first()
    if not result:
        raise HTTPException(status_code=404, detail="Event not found")
    return result

# Inactive update/delete route examples; these are not registered with the router.
# PUT /api/events/{event_id}
# @router.put("/{event_id}", response_model=EventModel)
# def update_events(
#         event_id:int, 
#         payload:EventUpdateSchema,
#         session: Session = Depends(get_session)):
#     # Find the existing event before applying the requested changes.
#     query = select(EventModel).where(EventModel.id == event_id)
#     obj = session.exec(query).first()
#     if not obj:
#         raise HTTPException(status_code=404, detail="Event not found")

#     data = payload.model_dump()
#     for k, v in data.items():
#         setattr(obj, k, v)

#     obj.updated_at = get_utc_now()

#     session.add(obj)
#     session.commit()
#     session.refresh(obj)
#     return obj

# @router.delete("/{event_id}")
# def delete_event(event_id: int, session: Session = Depends(get_session)) -> str:
#     query = select(EventModel).where(EventModel.id == event_id)
#     obj = session.exec(query).first()
#     if not obj: 
#         raise HTTPException(status_code=404, detail="Event not found")

#     session.delete(obj)
#     session.commit()
#     return "Event deleted"
