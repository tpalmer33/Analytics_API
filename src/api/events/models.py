from datetime import datetime, timezone
from typing import List, Optional
import sqlmodel
from sqlmodel import SQLModel, Field
from timescaledb import TimescaleModel
from timescaledb.utils import get_utc_now

# Tracking page visits at any given time

class EventModel(TimescaleModel, table=True):
    # id: Optional[int] = Field(default=None, primary_key=True)
    page: str = Field(index=True) # /about, /contact, /pricing
    description: Optional[str] = ""
    # created_at: datetime = Field(
    #     default_factory=get_utc_now,
    #     sa_type=sqlmodel.DateTime,
    #     nullable=False
    # )
    updated_at: datetime = Field(
        default_factory=get_utc_now,
        sa_type=sqlmodel.DateTime,
        nullable=False
    )


class EventCreateSchema(SQLModel):
    page: str
    description: Optional[str] = Field(default="")


class EventUpdateSchema(SQLModel):
    description: str


class EventListSchema(SQLModel):
    results: List[EventModel]
    count: int